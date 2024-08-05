from fastapi import APIRouter, Depends, Request, Body, File, UploadFile

# Logs Import
from logger_config import log_writer

# Schema Import
from app.api.schemas.response_schema import GlobalResponse, GlobaResponsesExamples, build_reponse_example

# Depends Import
from app.api.depends.is_authenticated_depend import verify_authentication

# Controllers Import
from app.api.controllers.yolo_controller import get_available_models_controller, inference_controller

# Models Import
from app.api.models.example_model import ExampleModel

router = APIRouter(
    prefix='/yolo',
    tags=["First Example Routes"]
)

def get_tag_description():
    return {
        "name": "Yolo Server Routes",
        "description": """ Used to interact with the YOLO server as a service. """
    }

@router.get("/get-available-models", response_model=GlobalResponse, response_model_exclude_unset=False, responses={**GlobaResponsesExamples})
async def get_available_models(request: Request):
    log_file = request.state.log_file
    log_writer(log_file, "Get Available Models - Requested")

    controller = await get_available_models_controller(log_file)

    response = GlobalResponse(
        status=True,
        request_id=request.state.request_id,
        data=controller,
    )
    response.set_start_ts(request.state.start_ts)
    return response

@router.post("/inference", response_model=GlobalResponse, response_model_exclude_unset=False, responses={**GlobaResponsesExamples})
async def inference(request: Request, file: UploadFile = File(...)):
    log_file = request.state.log_file
    log_writer(log_file, f"Router - Inference router requested. Received: {file.filename}")

    controller = await inference_controller(file, log_file)

    response = GlobalResponse(
        status=True,
        request_id=request.state.request_id,
        data=controller
    )
    response.set_start_ts(request.state.start_ts)
    return response
