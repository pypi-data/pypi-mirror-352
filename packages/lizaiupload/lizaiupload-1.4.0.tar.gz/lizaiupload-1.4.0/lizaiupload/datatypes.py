class UploadErrorException(Exception):
    def __init__(self, file_path, key, message=None):
        self.file_path = file_path
        self.key = key
        self.message = message or f"Failed to upload {file_path}"
        super().__init__(self.message)