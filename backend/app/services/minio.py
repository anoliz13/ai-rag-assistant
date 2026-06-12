from minio import Minio
from app.core.config import settings
import mimetypes


class MinioService:
    def __init__(self):
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=False,
        )
        self.bucket = settings.minio_bucket
        self._ensure_bucket()

    def _ensure_bucket(self):
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def upload_file(self, object_name: str, file_bytes: bytes, content_type: str | None = None) -> str:
        if not content_type:
            content_type = mimetypes.guess_type(object_name)[0] or "application/octet-stream"
        self.client.put_object(
            self.bucket,
            object_name,
            data=__import__("io").BytesIO(file_bytes),
            length=len(file_bytes),
            content_type=content_type,
        )
        return f"{settings.minio_endpoint}/{self.bucket}/{object_name}"

    def get_file(self, object_name: str) -> bytes | None:
        try:
            response = self.client.get_object(self.bucket, object_name)
            data = response.read()
            response.close()
            return data
        except Exception:
            return None

    def delete_file(self, object_name: str):
        try:
            self.client.remove_object(self.bucket, object_name)
        except Exception:
            pass

    def get_url(self, object_name: str) -> str:
        return f"http://{settings.minio_endpoint}/{self.bucket}/{object_name}"
