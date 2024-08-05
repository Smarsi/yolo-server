import os
import base64
from dotenv import load_dotenv
from ftplib import FTP
from pathlib import Path
from fastapi import UploadFile
from uuid import uuid4 as uuid

load_dotenv()

# Errors Imports
from errors import APIError

from logger_config import log_writer

class File_Manager:
    async def save_file(self, file: UploadFile, id):
        save_directory = Path("./evidences")
        save_directory.mkdir(parents=True, exist_ok=True)
        file_info = file.content_type.split('/')
        file_name = f"{id}_evidence" + str(uuid()) + f".{file_info[1]}"
        file_path = save_directory / file_name
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        return {
            "filename": file_name,
            "file_path": str(file_path),
            "file_type": file_info[0]
            }
    
    async def delete_local_file(self, file):
        os.remove(file)
    
    async def save_file_ftp(self, file: UploadFile, id_notification):
        file_info = file.content_type.split('/')
        file_name = f"{id_notification}_evidence" + str(uuid()) + f".{file_info[1]}"

        # Get variables from .env
        ftp_host = os.getenv("FTP_HOST")
        ftp_user = os.getenv("FTP_USER")
        ftp_password = os.getenv("FTP_PASSWORD")
        ftp_http_folder = os.getenv("FTP_HTTP_FOLDER")
        ftp_evidence_folder = os.getenv("FTP_EVIDENCE_FOLDER")
        
        ftp = FTP(ftp_host)
        ftp.login(ftp_user, ftp_password)
        ftp.set_pasv(True)
        
        ftp.storbinary(f"STOR {ftp_http_folder}{ftp_evidence_folder}/{file_name}", file.file)
        ftp.quit()

        return {
            "filename": file_name,
            "file_path": f"{ftp_host}{ftp_evidence_folder}/{file_name}",
            "file_type": file_info[0]
            }
    
    async def save_thumb_ftp(self, filepath):
        file_name = filepath.split("/")[1]

        # Get variables from .env
        ftp_host = os.getenv("FTP_HOST")
        ftp_user = os.getenv("FTP_USER")
        ftp_password = os.getenv("FTP_PASSWORD")
        ftp_http_folder = os.getenv("FTP_HTTP_FOLDER")
        thumbs_folder = "/thumbs"
        
        ftp = FTP(ftp_host)
        ftp.login(ftp_user, ftp_password)
        ftp.set_pasv(True)
        
        with open(filepath, 'rb') as file:
            # Use storbinary para enviar arquivos binários
            ftp.storbinary(f"STOR {ftp_http_folder}{thumbs_folder}/{file_name}", file)

        await self.delete_file(filepath)    

        return {
            "filename": file_name,
            "file_path": f"{ftp_host}{thumbs_folder}/{file_name}"
            }

    async def convert_base64_to_file(binary_string):
        binary_data = base64.b64decode(binary_string)
        local_path = Path('./base64')
        local_path.mkdir(parents=True, exist_ok=True)
        result_file_name = f"tmp_file_{uuid()}"
        with open(f"{local_path}/{result_file_name}", 'wb') as file:
            file.write(binary_data)
            return f"{local_path}/{result_file_name}"
        
    async def delete_file(self, filepath):
        try:
            os.remove(filepath)
            print(f"Arquivo {filepath} removido com sucesso.")
        except Exception as e:
            print(f"Erro ao remover arquivo {filepath}: {e}")
        