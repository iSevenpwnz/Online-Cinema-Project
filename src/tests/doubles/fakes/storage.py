from typing import Dict, Union

from storages import S3StorageInterface


class FakeS3Storage(S3StorageInterface):
    """
    Fake S3 Storage class for unit testing.

    This class simulates an S3 storage by storing files in an internal dictionary
    instead of actually uploading them to a remote server.
    """

    def __init__(self):
        """
        Initializes the FakeS3Storage instance with an empty in-memory storage dictionary.
        """
        self.storage: Dict[str, bytes] = {}

    async def upload_file(self, file_name: str, file_data: Union[bytes, bytearray]) -> None:
        """
        Simulates uploading a file by storing its data in memory under the given file name.
        
        Args:
        	file_name: The name to associate with the stored file.
        	file_data: The file's contents as bytes or bytearray.
        """
        self.storage[file_name] = file_data

    async def get_file_url(self, file_name: str) -> str:
        """
        Returns a fake URL for the specified file name as if it were stored in S3.
        
        Args:
            file_name: The name of the file.
        
        Returns:
            A fake URL string pointing to the file.
        """
        return f"http://fake-s3.local/{file_name}"
