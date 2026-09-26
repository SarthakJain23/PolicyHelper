from abc import ABC, abstractmethod
from typing import BinaryIO


class FileStorageService(ABC):
    """Abstract Base Class for Document File Storage strategy."""

    @abstractmethod
    async def upload_file(
        self, file_obj: BinaryIO, destination_path: str, content_type: str = "application/pdf"
    ) -> str:
        """Upload a file to storage and return its stored identifier/path."""
        pass

    @abstractmethod
    async def download_file(self, file_path: str) -> bytes:
        """Download and return raw file bytes from storage."""
        pass

    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file from storage."""
        pass

    @abstractmethod
    async def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
        """Generate a presigned or accessible URL/path for the file."""
        pass
