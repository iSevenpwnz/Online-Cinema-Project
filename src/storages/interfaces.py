from abc import ABC, abstractmethod
from typing import Union


class S3StorageInterface(ABC):

    @abstractmethod
    async def upload_file(self, file_name: str, file_data: Union[bytes, bytearray]) -> None:
        """
        Uploads a file to the storage asynchronously.
        
        Args:
        	file_name: Name to assign to the stored file.
        	file_data: File content as bytes or bytearray.
        
        Returns:
        	The URL of the uploaded file.
        """
        pass

    @abstractmethod
    async def get_file_url(self, file_name: str) -> str:
        """
        Generates a public URL for accessing a file stored in S3-compatible storage.
        
        Args:
            file_name: The name of the file for which to generate the URL.
        
        Returns:
            The public URL to access the specified file.
        """
        pass
