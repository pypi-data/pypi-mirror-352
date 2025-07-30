import asyncio
import os
import logging
import argparse
from dotenv import load_dotenv
from pathlib import Path
from .uploader_service import UploaderService
from .helpers import (parse_url, is_valid_folder_name)
from .upload import (upload_folder, upload_file)
from .config import Config
from .constants import (DEFAULT_VERSION, DEFAULT_SKIP_EXTENSION, MAX_THREAD, DEFAULT_THREAD_UPLOAD, RETRY_DELAY_SECONDS)

TOKEN = ""
NUMBER_THREAD = DEFAULT_THREAD_UPLOAD
RETRY_DELAY_SECONDS = RETRY_DELAY_SECONDS

def main():
    current_dir = Path(os.getcwd())
    parser = argparse.ArgumentParser(description="Upload folder to API with multipart upload.")
    parser.add_argument('folder_path', type=str, help='Path to the folder to upload')
    parser.add_argument('--study-name', type=str, help='Study name')
    parser.add_argument('--include-folder', action='store_true', help='Include folder path in key')
    parser.add_argument('--parent-folder-name', type=str, help='Parent folder name to include in key')
    parser.add_argument('--thread', type=int, help='Number of threads upload')
    parser.add_argument('--retry-delay', type=int, help='time delay (in seconds) before retrying')
    parser.add_argument('--skip-extension', type=str, default='', help='Comma-separated list of file extensions to skip')
    parser.add_argument('--env', type=str, help='path file ENV')
    args = parser.parse_args()
    if args.env:
        dotenv_path = os.path.join(args.env, '.env')
    else:
        dotenv_path = os.path.join(current_dir, '.env')
    load_dotenv(dotenv_path)
    api_url = os.getenv('API_URL')
    version = os.getenv('VERSION') or DEFAULT_VERSION
    global TOKEN
    TOKEN = os.getenv('TOKEN')

    if not api_url or not version:
        raise ValueError("API_URL and TOKEN environment variables must be set")
    
    parse_url(api_url)
    
    folder_path = args.folder_path
    include_folder = args.include_folder
    parent_folder_name = args.parent_folder_name
    study_name = args.study_name
    skip_extensions = []
    try:
        skip_extensions = [ext.strip() for ext in args.skip_extension.split(',') if ext.strip().startswith('.')] if args.skip_extension else []
    except Exception as e:
        raise e
    if len(skip_extensions) == 0:
        skip_extensions = DEFAULT_SKIP_EXTENSION

    if parent_folder_name and not is_valid_folder_name(parent_folder_name):
        raise ValueError("--parent-folder-name is not valid")
    
    if not study_name:
        raise ValueError("--study-name is required")

    global NUMBER_THREAD, RETRY_DELAY_SECONDS
    if args.thread:
        NUMBER_THREAD = args.thread if args.thread <= MAX_THREAD else MAX_THREAD
    if args.retry_delay:
        RETRY_DELAY_SECONDS = args.retry_delay
    try:
        config = Config(api_url, TOKEN, study_name, NUMBER_THREAD, RETRY_DELAY_SECONDS)
        if os.path.isfile(folder_path):
            upload_file(config, folder_path)
        else:
            upload_folder(config, folder_path, include_folder, parent_folder_name, skip_extensions)
    except Exception as e:
        print("An error occurred during the upload process:", str(e))

if __name__ == "__main__":
    try:
        main()
        print("Upload Done")
    except Exception as e:
        print("Error occurred:", str(e))
