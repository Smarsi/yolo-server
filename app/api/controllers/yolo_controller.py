import time
import cv2
import numpy as np
from uuid import uuid4 as uuid

# Errors Import
from errors import APIError

# Logs Import
from logger_config import log_writer

# Models Import
from app.api.models.yolo_model import YoloModel, YoloOutput


# Validators Import
from app.api.validators.example_validator import ExampleValidator

# Utils Import 
from app.utils.files_manager import File_Manager

# Services Import
from app.service import get_global_yolo_service

async def get_available_models_controller(log_file):
    data_on_model = {
        "name": "Test",
        "description":"This is a test",
        "value":1,
        "is_active":True,
        "is_deleted":False
    }

    return data_on_model

async def inference_controller(file, log_file):
    log_writer(log_file, f"Controller - Inference controller requested. Received: {file.filename}")
 
    id = str(uuid()).replace("-", "")

    log_writer(log_file, f"Controller - Starting inference.")
    yolo_service = get_global_yolo_service()

    log_writer(log_file, f"Controller - Current yolo service: {yolo_service}")
    
    contents = await file.read()
    np_arr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    yolo_service.add_frame(id, image)
    result = yolo_service.get_result(id)
    
    # ==== Fit on MODEL ====
    outputs = []
    for out in result['output']: outputs.append(YoloOutput(**out))
    response = YoloModel(
        output=outputs,
        ready=result["ready"],
        # timestamp=result["timestamp"]
    )
    # ==== End Fit on MODEL ====



    ## FOR FUTURE ANALYSIS  === COULD WORK WITH A MOST POWERFUL GPU & FRONT CONTROLLERS ===
    '''
    yolo_service = new_get_global_yolo_service()
    contents = await file.read()
    np_arr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    result = yolo_service.perform_inference(image)

    outputs = []
    for out in result['output']: outputs.append(YoloOutput(**out))
    response = YoloModel(
        id=result["id"],
        output=outputs,
        ready=result["ready"],
        timestamp=result["timestamp"]
    )
    '''

    log_writer(log_file, f"Controller - Succesfully processed inference. Result: {result}")
    return response
