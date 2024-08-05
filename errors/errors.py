from typing import Optional, List

class APIError(Exception):
    level: str
    message: str
    parameters: Optional[List[any]]

    def __init__(self, level, message, parameters=None):
        self.level = level
        self.message = message
        self.parameters = parameters

        super().__init__(level, message)

    def __dict__(self):
        error_dict = {
            "level": self.level,
            "message": self.message,
            "parameters": self.parameters
        }
        return error_dict
