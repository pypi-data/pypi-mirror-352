import aiohttp
import asyncio
import os
import aiofiles
import logging
from tenacity import retry, stop_after_attempt, wait_fixed
import argparse
from dotenv import load_dotenv
from pathlib import Path
import signal

from .datatypes import (UploadErrorException)
from .config import Config
from .helpers import (parse_url, is_valid_folder_name, make_file_log, append_to_file, is_existed_line_file, key_relative_path)
from .constants import (PART_CHUNK_SIZE)

class UploaderService:
    API_INIT_STUDY = "SLizAI/InitStudy"
    API_CREATE_OBJECT = "SLizAI/CreateObject"
    API_COMPLETE_OBJECT = "SLizAI/CompleteObject"
    API_CREATE_PART = "SLizAI/CreatePart"
    API_COMPLETE_PART = "SLizAI/CompletePart"

    def __init__(self, config: Config):
        self.api_url = config.api_url
        self.version = config.version
        self.token = config.token
        self.semaphore_limit = config.number_threads
        self.semaphore = asyncio.Semaphore(config.number_threads)
        self.retry_delay = config.retry_delay_seconds
        self.logger = logging.getLogger('UploaderService')
        self.ERROR_401 = False
        self.WRITE_LOG_UPLOAD = True
        self.SKIP_CHECK_UPLOADED = False
        self.name_log_file_upload = ""
        self.part_chunk_size = PART_CHUNK_SIZE
        self.study_name = config.study_name
        self.study_sig = None

        # Setup logging
        logging.basicConfig(filename='upload_errors.log', level=logging.ERROR, 
                            format='%(asctime)s:%(levelname)s:%(message)s')
        logging.basicConfig(filename='upload_debug.log', level=logging.DEBUG, 
                            format='%(asctime)s:%(levelname)s:%(message)s')
    def getToken(self):
        _token = ""
        if self.token is not None:
            _token = self.token
        else:
            if os.getenv('TOKEN') is not None:
                _token = os.getenv('TOKEN')
        return f"Bearer {_token}"
    
    def makeUrlRequest(self, URL):
        return f"{self.api_url}/api/v{self.version}/{URL}"
    
    def write_log_to_file(self, fileName, value):
        try:
            append_to_file(fileName, value)
        except Exception as e:
            logging.error(f"Write log {str(e)}")

    async def getStudySig(self, session):
        _signature = ""
        if self.study_sig is not None:
            _signature = self.study_sig
        else:
            study_response = await self.init_study(session, self.study_name)
            _signature = study_response['data']['signature']
        return f"{_signature}"

    # Retry configuration
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry_error_callback=lambda retry_state: retry_state.outcome.result())
    async def retry_request(self, request_coro):
        return await request_coro
    
    async def init_study(self, session, study_name):
        url = f"{self.makeUrlRequest(self.API_INIT_STUDY)}"
        data = {
            "Name": study_name
        }
        headers = {
            "Authorization": f"{self.getToken()}"
        }
        async with session.post(url, json=data, headers=headers) as response:
            if response.status == 401:
                self.ERROR_401 = True
                raise aiohttp.ClientResponseError(response.request_info, response.history, status=response.status)
            if response.status == 502:
                return await self.init_study(session, study_name)
            response.raise_for_status()
            return await response.json()
    
    async def create_object(self, session, size_bytes, last_modified_timestamp, key):
        url = f"{self.makeUrlRequest(self.API_CREATE_OBJECT)}"
        data = {
            "sizeBytes": size_bytes,
            "key": key,
            "lastModified": last_modified_timestamp,
            "groupSig": f"{await self.getStudySig(session)}"
        }
        headers = {
            "Authorization": f"{self.getToken()}"
        }
        async with session.post(url, json=data, headers=headers) as response:
            if response.status == 401:
                self.ERROR_401 = True
                raise aiohttp.ClientResponseError(response.request_info, response.history, status=response.status)
            if response.status == 502:
                return await self.create_object(session, size_bytes, last_modified_timestamp, key)
            response.raise_for_status()
            return await response.json()
        
    async def complete_object(self, session, signature):
        url = f"{self.makeUrlRequest(self.API_COMPLETE_OBJECT)}"
        data = {
            "signature": signature
        }
        headers = {
            "Authorization": f"{self.getToken()}"
        }
        async with session.post(url, json=data, headers=headers) as response:
            if response.status == 401:
                self.ERROR_401 = True
                raise aiohttp.ClientResponseError(response.request_info, response.history, status=response.status)
            if response.status == 502:
                return await self.complete_object(session, signature)
            response.raise_for_status()
            return await response.json()
    
    async def create_part(self, session, signature, part_number, upload_id):
        url = f"{self.makeUrlRequest(self.API_CREATE_PART)}"
        data = {
            "signature": signature,
            "partNumber": part_number,
            "uploadId": upload_id
        }
        headers = {
            "Authorization": f"{self.getToken()}"
        }
        async with session.post(url, json=data, headers=headers) as response:
            if response.status == 401:
                self.ERROR_401 = True
                raise aiohttp.ClientResponseError(response.request_info, response.history, status=response.status)
            if response.status == 502:
                return await self.create_part(session, signature, part_number, upload_id)
            response.raise_for_status()
            return await response.json()
        
    async def complete_part(self, session, signature, part_etags, upload_id):
        url = f"{self.makeUrlRequest(self.API_COMPLETE_PART)}"
        data = {
            "signature": signature,
            "partEtags": part_etags,
            "uploadId": upload_id
        }
        headers = {
            "Authorization": f"{self.getToken()}"
        }
        async with session.post(url, json=data, headers=headers) as response:
            if response.status == 401:
                self.ERROR_401 = True
                raise aiohttp.ClientResponseError(response.request_info, response.history, status=response.status)
            if response.status == 502:
                return await self.complete_part(session, signature, part_etags, upload_id)
            response.raise_for_status()
            print(f"complete_part OK")
            return await response.json()
    
    async def upload_part(self, session, presigned_url, part_data):
        async with session.put(presigned_url, data=part_data) as response:
            response.raise_for_status()
            print(f"upload_part OK {presigned_url}")
            return response.headers['ETag']

    async def upload_whole_file(self, session, presigned_url, file_path):
        async with aiofiles.open(file_path, 'rb') as file:
            file_data = await file.read()
            async with session.put(presigned_url, data=file_data) as response:
                print(f"upload_whole_file OK {presigned_url}")
                response.raise_for_status()
                return True
    
    async def upload_file_multipart(self, session, file_path, key, semaphore):
        async with semaphore:
            print(f"Start upload {key}")
            size_bytes = os.path.getsize(file_path)
            last_modified_timestamp = os.path.getmtime(file_path)
            try:
                # Step 1: Create Object
                create_object_response = await self.retry_request(self.create_object(session, size_bytes, last_modified_timestamp, key))
                signature = create_object_response['data']['signature']
                upload_id = create_object_response['data']['uploadPartId']
                presigned_url = create_object_response['data']['presignedURL']

                if upload_id:
                    # Step 2: Upload Parts
                    part_etags = []
                    part_number = 1
                    chunk_size = self.part_chunk_size  

                    async with aiofiles.open(file_path, 'rb') as file:
                        while True:
                            part_data = await file.read(chunk_size)
                            if not part_data:
                                break
                            
                            create_part_response = await self.retry_request(self.create_part(session, signature, part_number, upload_id))
                            presigned_url = create_part_response['data']['presignedURL']
                            e_tag = await self.retry_request(self.upload_part(session, presigned_url, part_data))
                            
                            part_etags.append({
                                "partNumber": part_number,
                                "eTag": e_tag
                            })
                            part_number += 1

                    # Step 3: Complete Parts
                    complete_part_response = await self.retry_request(self.complete_part(session, signature, part_etags, upload_id))
                    #return complete_part_response
                else:
                    upload_full_file_response = await self.retry_request(self.upload_whole_file(session, presigned_url, file_path))
                    #return upload_full_file_response
                complete_object_response = await self.retry_request(self.complete_object(session,signature))
                if self.WRITE_LOG_UPLOAD:
                    self.write_log_to_file(self.name_log_file_upload, key)
                return complete_object_response
            except Exception as e:
                if self.ERROR_401 is True:
                    logging.error(f"Unauthorized (401) - Stopping all uploads")
                    print(f"Unauthorized (401)")
                    os.kill(os.getpid(), signal.SIGINT)
                logging.error(f"Failed to upload {file_path}: {str(e)}")
                custom_exception = UploadErrorException(file_path, key, str(e))
                custom_exception.key = key
                raise custom_exception
    
    async def retry_failed_uploads(self, failed_files):
        if not failed_files:
            return

        print(f"Retry upload")
        semaphore = asyncio.Semaphore(self.semaphore_limit)
        await asyncio.sleep(self.retry_delay)  # Wait for 5 minutes
        async with aiohttp.ClientSession() as session:
            tasks = [self.upload_file_multipart(session, file_path, key, semaphore) 
                    for file_path, key in failed_files]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            new_failed_files = []
            for result in results:
                if isinstance(result, Exception):
                    new_failed_files.append((result.file_path, result.key))
            
            if new_failed_files:
                await self.retry_failed_uploads(new_failed_files)

    async def upload_folder(self, folder_path: str, include_folder: bool, parent_folder_name: str = None, skip_extensions = [".log"]):
        if parent_folder_name and not is_valid_folder_name(parent_folder_name):
            raise ValueError("--parent-folder-name is not valid")
        async with aiohttp.ClientSession() as session:
            tasks = []
            failed_files = []
            self.name_log_file_upload = make_file_log("upload",folder_path, include_folder, skip_extensions, parent_folder_name)
            for root, dirs, files in os.walk(folder_path):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                files = [f for f in files if not f.startswith('.')]
                if len(skip_extensions) > 0:
                    files = [f for f in files if not f.endswith(tuple(skip_extensions))]
                for file in files:
                    file_path = os.path.join(root, file)
                    if parent_folder_name:
                        key = os.path.join(parent_folder_name, os.path.relpath(file_path, os.path.dirname(folder_path)).replace(os.sep, '/')).replace(os.sep, '/') # f"{parent_folder_name}/{os.path.relpath(file_path, os.path.dirname(folder_path)).replace(os.sep, '/')}"
                    elif include_folder:
                        key = os.path.relpath(file_path, os.path.dirname(folder_path)).replace(os.sep, '/')
                    else:
                        key = os.path.relpath(file_path, folder_path).replace(os.sep, '/')
                    key = key_relative_path(key)
                    if self.SKIP_CHECK_UPLOADED is True or not is_existed_line_file(self.name_log_file_upload, key):
                        tasks.append(self.upload_file_multipart(session, file_path, key, self.semaphore))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            try:
                for result in results:
                    if isinstance(result, Exception):
                        print(f"An error occurred: {(result.file_path, result.key)}")
                        failed_files.append((result.file_path, result.key))
                    #else:
                    #    print(f"Multipart upload completed successfully")
            except Exception as e:
                logging.error(f"{e}")
            
            if failed_files:
                await self.retry_failed_uploads(failed_files)

    async def upload_file(self, file_path: str, skip_extensions = [".log"]):
        async with aiohttp.ClientSession() as session:
            tasks = []
            failed_files = []
            key = os.path.normpath(file_path).replace(os.sep, '/')
            key = key_relative_path(key)
            tasks.append(self.upload_file_multipart(session, file_path, key, self.semaphore))
            results = await asyncio.gather(*tasks, return_exceptions=True)
            try:
                for result in results:
                    if isinstance(result, Exception):
                        print(f"An error occurred: {(result.file_path, result.key)}")
                        failed_files.append((result.file_path, result.key))
                    #else:
                    #    print(f"Multipart upload completed successfully")
            except Exception as e:
                logging.error(f"{e}")
            
            if failed_files:
                await self.retry_failed_uploads(failed_files)