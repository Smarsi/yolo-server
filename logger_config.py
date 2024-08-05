import os
import datetime
from uuid import uuid4 as uuid
from fastapi import Request

# Utils Import
from app.utils.datetime_manager import get_current_datetime

logs_folder = "./logs/"
errors_log_folder = "./logs/error_logs/"

def setup_file(specific_folder):
    os.makedirs(specific_folder, exist_ok=True)

def log_builder(request: Request):
    request_id = request.state.uuid
    specific_folder = logs_folder
    setup_file(specific_folder)    
    datetime_info = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    user_id_on_create = 0
    log_file = os.path.join(specific_folder+f"{datetime_info}"+f"-{user_id_on_create}-"+f"{request_id}.log")
    return log_file

def log_rename(log_file, id_account):
    setup_file = log_file.split("-")
    setup_file[2] = id_account
    new_name = setup_file[0]
    for i in setup_file[1:]:
        new_name = new_name + f"-{str(i)}"
    os.rename(log_file, new_name) 
    return new_name

def log_writer(log_file, log_content):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as file:
        file.write(f"\n{timestamp}; DEBUG; {log_content};")
    file.close()

def errors_log_generator(traceback):
    id = uuid()
    specific_folder = errors_log_folder
    setup_file(specific_folder)
    log_file = os.path.join(specific_folder + f"{id}.log")

    with open(log_file, "w") as writer:
        writer.write(traceback)
    return log_file