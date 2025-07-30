import asyncio
from .config import Config
from .uploader_service import UploaderService
from .constants import (DEFAULT_SKIP_EXTENSION)

def upload_folder(config: Config, folder_path: str, include_folder: bool = False, parent_folder_name: str = None, skip_extensions: list[str] = ['.log']):
    try:
        if len(skip_extensions) == 0:
            skip_extensions = DEFAULT_SKIP_EXTENSION
        uploader_service = UploaderService(config)
        asyncio.run(uploader_service.upload_folder(folder_path, include_folder, parent_folder_name, skip_extensions))
    except Exception as e:
        print("An error occurred during the upload Folder:", str(e))

def upload_file(config: Config, file_path: str):
    try:
        uploader_service = UploaderService(config)
        uploader_service.WRITE_LOG_UPLOAD = False
        uploader_service.SKIP_CHECK_UPLOADED = True
        asyncio.run(uploader_service.upload_file(file_path, False))
    except Exception as e:
        print("An error occurred during the upload File:", str(e))