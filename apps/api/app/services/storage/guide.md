# Storage Services Guide (`apps/api/app/services/storage/`)

Implementation of the **Storage Strategy Pattern** for persisting uploaded policy files.

---

## File Index

| File                       | Description                                                                                  |
| :------------------------- | :------------------------------------------------------------------------------------------- |
| [`base.py`](base.py)       | Abstract base class `FileStorageService` defining upload, download, delete, and URL methods. |
| [`local.py`](local.py)     | `LocalStorageService` saving files directly to host disk (`data/policies/`).                 |
| [`s3.py`](s3.py)           | `S3StorageService` managing uploads to AWS S3 / MinIO using `boto3`.                         |
| [`factory.py`](factory.py) | `StorageFactory` instantiating the strategy selected via `STORAGE_TYPE` in `.env`.           |
