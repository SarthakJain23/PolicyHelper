import os
from pathlib import Path
from typing import BinaryIO
import aiofiles
from app.core.config import settings
from app.services.storage.base import FileStorageService


class LocalStorageService(FileStorageService):
    """Local Filesystem Storage Strategy Implementation."""

    def __init__(self, base_dir: str | None = None):
        self.base_dir = Path(base_dir or settings.LOCAL_STORAGE_DIR)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def upload_file(
        self, file_obj: BinaryIO, destination_path: str, content_type: str = "application/pdf"
    ) -> str:
        full_path = self.base_dir / destination_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(full_path, "wb") as f:
            if hasattr(file_obj, "read"):
                content = file_obj.read()
                if isinstance(content, str):
                    content = content.encode("utf-8")
                await f.write(content)
            elif isinstance(file_obj, bytes):
                await f.write(file_obj)

        return str(destination_path)

    async def download_file(self, file_path: str) -> bytes:
        full_path = self.base_dir / file_path
        if not full_path.exists():
            raise FileNotFoundError(f"File not found in local storage: {file_path}")

        async with aiofiles.open(full_path, "rb") as f:
            return await f.read()

    async def delete_file(self, file_path: str) -> bool:
        full_path = self.base_dir / file_path
        if full_path.exists():
            full_path.unlink()
            return True
        return False

    async def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
        # For local storage, returns the internal API download endpoint
        return f"/api/v1/documents/files/{file_path}"
