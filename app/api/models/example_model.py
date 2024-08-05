from pydantic import BaseModel, StrictStr
from typing import Optional

# Model
class ExampleModel(BaseModel):
    name: StrictStr
    description: Optional[StrictStr] = None
    value: int
    is_active: bool
    is_deleted: bool

    def normalize_fields(self):
        for field_name, field_value in self.dict().items():
            if field_value is None:
                new_value = ""
                setattr(self, field_name, new_value)
