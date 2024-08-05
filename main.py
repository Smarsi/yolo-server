import os 
import logging
import logging.config
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError, HTTPException
from app.api.middlewares.setup_request import setup_request
from fastapi.openapi.utils import get_openapi

# Handlers Import
from app.handlers.error_handler import global_error_handler, global_http_exception_handler, global_validation_error_handler

# Routers Import
from app.api.routes import router, get_tags_description

# Services Import
from app.service.yolo_service import Yolo_Service

log = logging.getLogger("uvicorn")

def create_application() -> FastAPI:
    application = FastAPI()
    application.include_router(
        router,
        prefix="/api"
    )
    return application

app = create_application()
app.middleware("http")(setup_request)  # Generate a request_id and needed data for each request received

@app.get("/")
async def root():
    return {"status": "running"}

origins = [
    "*", # Allow all origins
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def custom_openapi():
    # if app.openapi_schema:
    #     return app.openapi_schema
    openapi_schema = get_openapi(
        title="Yolo Server - API",
        version="1.0",
        #summary="This is a model API",
        description="All the documentation for this API can be found here.",
        routes=app.routes,
        tags=get_tags_description()
    )
    # openapi_schema["info"]["x-logo"] = {
    #     "url": "" # Add a logo url here if you want
    # }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi_schema = custom_openapi()

# Registering Handlers

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return await global_http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return await global_validation_error_handler(request, exc)

# @app.exception_handler(Exception) 
# async def default_exception_handler(request: Request, exc: Exception):
#     return await global_error_handler(request, exc)
#-------------------------------------------------------
# This handler is commented because it need to be declared on global middleware (cannot be used here when a global middleware is registred)
# Use this handler only in case you don't have a global middleware registred.
# You can found this same declaration working on app/api/middlewares/setup_request.py

yolo_service = Yolo_Service(2, "/home/richard/DNN-models/Yolo-v8/Detection/yolov8s.onnx", "/home/richard/DNN-models/Yolo-v8/Detection/classes.txt")

@app.on_event("startup")
async def startup_event():
    yolo_service.start_service()
    logging.info(
        "Starting Up..."
    )


@app.on_event("shutdown")
async def shutdown_event():
    yolo_service.stop_service()
    logging.info(
        "Shutting Down"
    )
