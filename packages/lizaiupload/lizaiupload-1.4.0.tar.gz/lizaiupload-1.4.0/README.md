# Uploader Service

  

A tool to upload folders / File with multipart upload.

  

## Installation

> pip install lizaiupload

  

## Usage Command

**usage:**
>lizaiupload folder_path [--parent-folder-name PARENT_FOLDER_NAME] [--thread THREAD]
>[--retry-delay RETRY_DELAY] [--env ENV] [--skip-extension SKIP_EXTENSIONS] [--include-folder]
  

**positional arguments:**

folder_path Path to the folder to upload

  

**options:**

-h, --help show this help message and exit

|  Parameter| Description |
|--|--|
| --include-folder | Include folder path in key |
| --parent-folder-name PARENT_FOLDER_NAME | Parent folder name to include in key |
| --thread THREAD | Number of threads upload |
| --retry-delay RETRY_DELAY | Time delay (in seconds) before retrying |
| --skip-extension SKIP_EXTENSIONS | Comma-separated list of file extensions to skip |
| --env ENV | Path file ENV |
  

*You can also include the folder name in the key:*

> lizaiupload /path/to/your/folder --include-folder

  

*Or specify a parent folder name:*

> lizaiupload /path/to/your/folder --parent-folder-name parent_folder

  

*Upload all in current path use:* folder_path = .

  

*Example:*

> lizaiupload foldertest --env ./config --thread 10 --retry-delay 30 --skip-extension .mp3,.3gp  --include-folder

  

Create .env file in folder config data config
```
API_URL=https://example

TOKEN=token_string
```

## Usage function

> from lizaiupload.config import Config
> from lizaiupload.upload import upload_folder

> conf = Config(api_url,
                token,
                number_threads,
                retry_delay_second)

|  Parameter|Required| Description |
|--|--|--|
| api_url | True | String API URL |
| token | True | String Token |
| number_threads | False | Number of threads upload (Default: 5) |
| retry_delay_second | False | Time delay (in seconds) before retrying (Default: 5) |

> upload_folder(config: Config, folder_path: str, include_folder: bool = False, parent_folder_name: str = None, skip_extensions: list[str] = ['.log'])

|  Parameter|Required| Description |
|--|--|--|
| config | True | Config setting |
| folder_path | True | Path to the folder to upload |
| include_folder | False | Include folder path in key |
| parent_folder_name | False | Parent folder name to include in key |
| skip_extensions | False | Comma-separated list of file extensions to skip |