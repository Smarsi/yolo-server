from uuid import uuid4 as uuid
import time

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
    file_manager = File_Manager()

    inference_id = str(uuid()).replace("-", "")

    file = await file_manager.save_file(file, inference_id)
    time.sleep(0.02)
    

    log_writer(log_file, f"Controller - Starting inference.")
    yolo_service = get_global_yolo_service()

    log_writer(log_file, f"Controller - Current yolo service: {yolo_service}")
    
    yolo_service.add_frame(inference_id, file["file_path"])

    result = yolo_service.get_result(inference_id)
    
    # ==== Fit on MODEL ====
    outputs = []
    for out in result['output']: outputs.append(YoloOutput(**out))
    response = YoloModel(
        id=result["id"],
        output=outputs,
        ready=result["ready"],
        timestamp=result["timestamp"]
    )
    # ==== End Fit on MODEL ====

    await file_manager.delete_file(file["file_path"])

    log_writer(log_file, f"Controller - Succesfully processed inference. Result: {result}")
    return response
