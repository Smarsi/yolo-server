import sys
from fastapi import Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
import traceback

# Erros Import
from errors import APIError

# Logs Import
from logger_config import log_writer, errors_log_generator

# Response Schema Import
from app.api.schemas.response_schema import GlobalResponse

traceback_str = ""

def create_traceback_error_log(exception: Exception):
    tb = traceback.format_exc()
    file = errors_log_generator(tb)
    return file

async def global_error_handler(request: Request, exception: Exception):
    log_file = request.state.log_file
    traceback_file = create_traceback_error_log(exception)
    log_writer(log_file, f"Error - {str(exception)}")
    log_writer(log_file, f"INFO - Traceback file: {traceback_file}")
    response = GlobalResponse(
        status=False,
        request_id=request.state.uuid,
        message="Error - Internal Server Error"
    )
    response.set_start_ts(request.state.start_ts)
    return JSONResponse(status_code=200, content=dict(response))

async def global_api_error_handler(request: Request, exception: APIError):
    log_file = request.state.log_file
    log_writer(log_file, f"APIError - {str(exception.__dict__())}")
    response = GlobalResponse(
        status=False,
        request_id=request.state.uuid,
        message=str(exception.message)
    )
    response.set_start_ts(request.state.start_ts)
    return JSONResponse(status_code=200, content=dict(response))

async def global_http_exception_handler(request: Request, exception: HTTPException):
    log_file = request.state.log_file
    log_writer(log_file, f"Error Http - {str(exception)}")
    response = GlobalResponse(
        status=False,
        request_id=request.state.uuid,
        message=exception.detail
    )
    response.set_start_ts(request.state.start_ts)
    return JSONResponse(status_code=exception.status_code, content=dict(response))

async def global_validation_error_handler(request: Request, exception: RequestValidationError):
    log_file = request.state.log_file
    log_writer(log_file, f"Validation Error - {str(exception)}")
    error_messages = []
    for error in exception.errors():
        field = error["loc"][1]
        error_messages.append(f"{field}' {error['msg']}")
    response = GlobalResponse(
        status=False,
        request_id=request.state.uuid,
        message=", ".join(error_messages)
    )
    response.set_start_ts(request.state.start_ts)
    return JSONResponse(status_code=200, content=dict(response))