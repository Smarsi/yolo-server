from pydantic import BaseModel, StrictInt, StrictStr

#
#  These models are used to grant that all controllers will allways return a model, even when they don't have
#  a specific one or don't have data to return. This way, the response will be consistent and the frontend will 
#  know what to expect.
#

class Global_Created_Response_Model(BaseModel):
    message: StrictStr = "Successfully Created"
    item_id: StrictInt

class Global_Updated_Response_Model(BaseModel):
    message: StrictStr = "Successfully Updated"
    item_id: StrictInt

class Global_Deleted_Response_Model(BaseModel):
    message: StrictStr = "Successfully Deleted"
    item_id: StrictInt
