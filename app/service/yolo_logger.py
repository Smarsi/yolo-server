import os
import traceback
from datetime import datetime, time
from uuid import uuid4 as uuid

logs_folder = "./logs/yolo_logs/"
errors_log_folder = "./logs/yolo_logs/error_logs/"

def yolo_log_builder():
    log_id = str(uuid()).replace("-", "")
    specific_folder = logs_folder
    os.makedirs(specific_folder, exist_ok=True)
    datetime_info = datetime.now().strftime("%Y%m%d-%H%M%S")
    user_id_on_create = 0
    log_file = os.path.join(specific_folder+f"{datetime_info}"+f"-{user_id_on_create}-"+f"{log_id}.log")
    print(log_file)
    return log_file

def log_writer(log_file, log_content):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as file:
        file.write(f"\n{timestamp}; DEBUG; {log_content};")
    file.close()

def errors_log_generator(traceback):
    id = uuid()
    specific_folder = errors_log_folder
    os.makedirs(specific_folder, exist_ok=True)
    log_file = os.path.join(specific_folder + f"{id}.log")

    with open(log_file, "w") as writer:
        writer.write(traceback)
    return log_file

def create_traceback_error_log(exception: Exception):
    tb = traceback.format_exc()
    file = errors_log_generator(tb)
    return file
