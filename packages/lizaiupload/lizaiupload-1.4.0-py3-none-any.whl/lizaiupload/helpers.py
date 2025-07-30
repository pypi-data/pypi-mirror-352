import base64
import errno
import hashlib
import math
import os
import platform
import re
import urllib.parse
from datetime import datetime

def is_valid_folder_name(folder_name):
    
    # Kiểm tra độ dài của tên thư mục
    if len(folder_name) == 0 or len(folder_name) > 255:
        return False
    
    # Kiểm tra ký tự không hợp lệ
    # Định nghĩa các ký tự không hợp lệ cho tên thư mục (dành cho Windows)
    # invalid_characters = r'[<>:"/\\|?*]'
    # if re.search(invalid_characters, folder_name):
    #     return False
    
    if '/' in folder_name:
        return False
    
    # Nếu không có lỗi nào ở trên, tên thư mục là hợp lệ
    return True

def parse_url(endpoint: str) -> urllib.parse.SplitResult:
    """Parse url string."""

    url = urllib.parse.urlsplit(endpoint)
    host = url.hostname

    if url.scheme.lower() not in ["http", "https"]:
        raise ValueError("scheme in endpoint must be http or https")

    url = url_replace(url, scheme=url.scheme.lower())

    if url.path and url.path != "/":
        raise ValueError("path in endpoint is not allowed")

    url = url_replace(url, path="")

    if url.query:
        raise ValueError("query in endpoint is not allowed")

    if url.fragment:
        raise ValueError("fragment in endpoint is not allowed")

    try:
        url.port
    except ValueError as exc:
        raise ValueError("invalid port") from exc

    if url.username:
        raise ValueError("username in endpoint is not allowed")

    if url.password:
        raise ValueError("password in endpoint is not allowed")

    if (
            (url.scheme == "http" and url.port == 80) or
            (url.scheme == "https" and url.port == 443)
    ):
        url = url_replace(url, netloc=host)

    return url

def url_replace(
        url: urllib.parse.SplitResult,
        scheme: str | None = None,
        netloc: str | None = None,
        path: str | None = None,
        query: str | None = None,
        fragment: str | None = None,
) -> urllib.parse.SplitResult:
    """Return new URL with replaced properties in given URL."""
    return urllib.parse.SplitResult(
        scheme if scheme is not None else url.scheme,
        netloc if netloc is not None else url.netloc,
        path if path is not None else url.path,
        query if query is not None else url.query,
        fragment if fragment is not None else url.fragment,
    )

def make_file_log(prefix: str, folder_path: str, include_folder: bool, skip_extension = [], parent_folder_name: str | None = None) -> str:
    name = f"{prefix}_files_{folder_path}{ f"_{parent_folder_name}" if parent_folder_name else ""}_{"1" if include_folder is True else "0"}{"_".join(skip_extension) if len(skip_extension) > 0 else ""}.log"
    return name

def append_to_file(file_path, new_line):
    # Đọc nội dung file
    try:
        #if not os.path.exists(os.path.dirname(file_path)):
        #    os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'r+') as file:
            lines = file.readlines()
    except FileNotFoundError as e:
        # Nếu file không tồn tại, coi như nội dung file là rỗng
        lines = []
        print(e)

    # Kiểm tra nếu chuỗi mới đã tồn tại trong file
    if new_line + '\n' in lines:
        return

    # Nếu chưa tồn tại, thêm chuỗi vào file
    with open(file_path, 'a') as file:
        file.write(new_line + '\n')

def is_existed_line_file(file_path, linestr):
    try:
        #os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'r+') as file:
            lines = file.readlines()
    except FileNotFoundError:
        # Nếu file không tồn tại, coi như nội dung file là rỗng
        lines = []

    # Kiểm tra nếu chuỗi mới đã tồn tại trong file
    if linestr + '\n' in lines:
        print(f"existed line {linestr}")
        return True
    return False

def key_relative_path(relative_path):
    if relative_path.startswith(".."):
        relative_path = relative_path[2:-2]

    if relative_path.startswith("."):
        relative_path = relative_path[1:-1]

    if relative_path.startswith("/"):
        relative_path = relative_path[1:-1]

    return relative_path