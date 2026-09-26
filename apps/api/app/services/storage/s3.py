import io
from typing import BinaryIO
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from app.core.config import settings
from app.services.storage.base import FileStorageService


class S3StorageService(FileStorageService):
    """AWS S3 / MinIO Storage Strategy Implementation."""

    def __init__(self):
        self.bucket_name = settings.S3_BUCKET_NAME
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL if settings.S3_ENDPOINT_URL else None,
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            region_name=settings.S3_REGION,
            config=Config(signature_version="s3v4"),
        )
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError:
            try:
                self.s3_client.create_bucket(Bucket=self.bucket_name)
            except Exception:
                pass

    async def upload_file(
        self, file_obj: BinaryIO, destination_path: str, content_type: str = "application/pdf"
    ) -> str:
        if isinstance(file_obj, bytes):
            file_data = io.BytesIO(file_obj)
        elif hasattr(file_obj, "read"):
            data = file_obj.read()
            file_data = io.BytesIO(data) if isinstance(data, bytes) else io.BytesIO(data.encode())
        else:
            file_data = file_obj

        self.s3_client.upload_fileobj(
            file_data,
            self.bucket_name,
            destination_path,
            ExtraArgs={"ContentType": content_type},
        )
        return destination_path

    async def download_file(self, file_path: str) -> bytes:
        buffer = io.BytesIO()
        self.s3_client.download_fileobj(self.bucket_name, file_path, buffer)
        buffer.seek(0)
        return buffer.read()

    async def delete_file(self, file_path: str) -> bool:
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_path)
            return True
        except ClientError:
            return False

    async def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": file_path},
                ExpiresIn=expires_in,
            )
            return url
        except Exception:
            return f"/api/v1/documents/files/{file_path}"
