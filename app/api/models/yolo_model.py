from pydantic import BaseModel, StrictStr, StrictInt, StrictFloat, StrictBool
from typing import Optional
from datetime import time

# Model
class YoloOutput(BaseModel):
    class_id: StrictInt
    class_name: StrictStr
    confidence: StrictFloat
    bb_x_center: StrictFloat
    bb_y_center: StrictFloat
    bb_width: StrictFloat
    bb_height: StrictFloat
    bb_x_min: StrictFloat
    bb_y_min: StrictFloat
    bb_x_max: StrictFloat
    bb_y_max: StrictFloat
    bb_x_bottom_center: StrictFloat
    bb_y_bottom_center: StrictFloat
    bb_x_top_center: StrictFloat
    bb_y_top_center: StrictFloat

    def normalize_fields(self):
        for field_name, field_value in self.model_dump().items():
            if field_value is None:
                new_value = ""
                setattr(self, field_name, new_value)

class YoloModel(BaseModel):
        output: list[YoloOutput]
        ready: StrictBool
        timestamp: time

        def normalize_fields(self):
            for field_name, field_value in self.model_dump().items():
                if field_value is None:
                    new_value = ""
                    setattr(self, field_name, new_value)
