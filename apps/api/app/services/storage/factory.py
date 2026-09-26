from app.core.config import settings
from app.services.storage.base import FileStorageService
from app.services.storage.local import LocalStorageService
from app.services.storage.s3 import S3StorageService

_storage_instance: FileStorageService | None = None


class StorageFactory:
    """Factory to retrieve configured FileStorageService instance."""

    @staticmethod
    def get_storage_service() -> FileStorageService:
        global _storage_instance
        if _storage_instance is None:
            if settings.STORAGE_TYPE == "s3":
                _storage_instance = S3StorageService()
            else:
                _storage_instance = LocalStorageService()
        return _storage_instance


def get_storage() -> FileStorageService:
    """Convenience helper to get current storage instance."""
    return StorageFactory.get_storage_service()
