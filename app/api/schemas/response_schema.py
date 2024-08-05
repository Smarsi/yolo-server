from pydantic import BaseModel, validator
from typing import Any
from typing import Optional
from datetime import time

from app.utils.datetime_manager import get_current_time, calc_timelapse

#
#   Schemas are used to define the structure of the data that will be sent and received in the API requests,
#   like JSONs body and responses.
#   The Pydantic library is used to create these schemas, which are classes that inherit from Pydantic's BaseModel.
#

class Pagination(BaseModel):
    current: Optional[Any] = ""
    max_pages: Optional[Any] = ""

    @staticmethod
    def json_model(self):
        return {
            "current": "url/current_page",
            "next": "url/next_page",
            "previous": "url/previous_page"
        }

class GlobalResponse(BaseModel):
    status: bool
    message: Optional[str] = ""
    request_id: Optional[str] = ""
    parameters: Optional[list] = []
    start_ts: Optional[time] 
    end_ts: Optional[time]
    timelapse: Optional[time]
    data: Optional[Any] = []
    pagination: Optional[Pagination] = {}

    def set_start_ts(self, value):
        self.start_ts = value
        self.end_ts = get_current_time()
        self.timelapse = calc_timelapse(self.start_ts, self.end_ts)

    def build_pagination(self, current_page, max_pages):      
        self.pagination = Pagination(current=current_page, max_pages=max_pages)

    @staticmethod
    def json_model(self):
        return {
            "status": "",
            "message": "",
            "request_id": "",
            "parameters": [],
            "start_ts": "",
            "end_ts": "",
            "timelapse": "",
            "data": [],
            "pagination": {}
        }
    
    @validator("data")
    def grant_list(cls, data):
         if type(data) != list:
              return [data]
         return data


# Classes and Functions used to generate OpenAPI Docs for Global Responses Examples 

def build_reponse_example(status_code, model, description):
        # Receives necessary info to build an openapi formated dict for responses examples (can be used in each route)
		return {
			status_code: { 
				"model": model,
				"description": description
			}
		}

class GlobalResponseExample401(BaseModel):
    class Config:
        json_schema_extra = {
            "example": [
                {
                    "status": False,
                    "message": "Unauthorized - Token Expired",
                    "request_id": "1bd5cb4729b74896a300fe6d67390513",
                    "parameters": [],
                    "start_ts": "11:32:22.958953",
                    "end_ts": "11:32:22.959590",
                    "timelapse": "0:00:00.000637",
                    "data": [],
                    "pagination": {}
                },
                {
                    "status": False,
                    "message": "Unauthorized - Invalid Token",
                    "request_id": "3b6c8b25193a48d8b1acf064e5c63c55",
                    "parameters": [],
                    "start_ts": "11:33:05.612917",
                    "end_ts": "11:33:05.613464",
                    "timelapse": "0:00:00.000547",
                    "data": [],
                    "pagination": {}
                },
                {
                    "status": False,
                    "message": "Unauthorized - Token not provided",
                    "request_id": "7fcb6ca7b14e4d77883ab66a16481006",
                    "parameters": [],
                    "start_ts": "11:33:21.210619",
                    "end_ts": "11:33:21.211108",
                    "timelapse": "0:00:00.000489",
                    "data": [],
                    "pagination": {}
                }
            ]
        }

class GlobalResponseExample403(BaseModel):
    class Config:
        json_schema_extra = {
            "example": [
                {
                    "status": False,
                    "message": "Unauthorized - Permission Denied!",
                    "request_id": "0ffacce73c9541aa97446b97924e34c1",
                    "parameters": [],
                    "start_ts": "11:28:32.099006",
                    "end_ts": "11:28:32.103417",
                    "timelapse": "0:00:00.004411",
                    "data": [],
                    "pagination": {}
                }
            ]
        }


GlobaResponsesExamples = {
    401: {
        "model": GlobalResponseExample401,
        "description": "Erros de autenticação"
    },
    403: {
        "model": GlobalResponseExample403,
        "description": "Erro de autorização (sem permissão)"
    }
}
