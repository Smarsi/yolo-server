from uuid import uuid4 as uuid
from fastapi import Request

# Logs Import
from logger_config import log_builder

from app.api.schemas.response_schema import GlobalResponse

# Application Errors
from errors import APIError

# Handlers Import
from app.handlers.error_handler import global_error_handler, global_api_error_handler

# Utils Import
from app.utils.datetime_manager import get_current_date, get_current_datetime, get_current_time

async def setup_request(request: Request, call_next):
    request.state.uuid = str(uuid()).replace("-", "")
    request.state.log_file = log_builder(request)
    request.state.start_ts = get_current_time()

    try:            
        response = await call_next(request)
    except APIError as exc:
        response = await global_api_error_handler(request, exc)
    except Exception as exc:
        response =  await global_error_handler(request, exc)
    finally:
        return response