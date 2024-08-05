# Errors Import
from errors import APIError

# Logs Import
from logger_config import log_writer

# Models Import
from app.api.models.example_model import ExampleModel

# Validators Import
from app.api.validators.example_validator import ExampleValidator

async def get_available_models_controller(requester, log_file):
    data_on_model = ExampleModel(
        name="Test",
        description="This is a test",
        value=1,
        is_active=True,
        is_deleted=False
    )

    return data_on_model
