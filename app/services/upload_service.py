from minio import Minio
from app.core.config import settings
import uuid
import io
from app.utils.logger import logger

class UploadService:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
            region=settings.MINIO_REGION
        )
        self._ensure_bucket()

    def _ensure_bucket(self):
        try:
            import json
            if not self.client.bucket_exists(settings.MINIO_BUCKET):
                self.client.make_bucket(settings.MINIO_BUCKET)
                logger.info(f"Created MinIO bucket: {settings.MINIO_BUCKET}")
            
            # Cấu hình policy công khai (Public Read-only)
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": ["*"]},
                        "Action": ["s3:GetBucketLocation", "s3:ListBucket"],
                        "Resource": [f"arn:aws:s3:::{settings.MINIO_BUCKET}"]
                    },
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": ["*"]},
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{settings.MINIO_BUCKET}/*"]
                    }
                ]
            }
            self.client.set_bucket_policy(settings.MINIO_BUCKET, json.dumps(policy))
            logger.info(f"Set public policy for bucket: {settings.MINIO_BUCKET}")
        except Exception as e:
            logger.error(f"Error checking/creating/setting MinIO bucket: {e}")

    def upload_image(self, file_data: bytes, filename: str, customer_id: int) -> str:
        """
        Upload ảnh lên MinIO và trả về URL.
        Path: customers/{customer_id}/{uuid}_{filename}
        """
        extension = filename.split(".")[-1] if "." in filename else "jpg"
        unique_name = f"{uuid.uuid4()}.{extension}"
        object_name = f"customers/{customer_id}/{unique_name}"
        
        try:
            self.client.put_object(
                settings.MINIO_BUCKET,
                object_name,
                io.BytesIO(file_data),
                length=len(file_data),
                content_type=f"image/{extension}"
            )
            
            # Trả về path để lưu vào DB
            # Link thực tế sẽ được build qua proxy hoặc dùng presigned URL
            return object_name
        except Exception as e:
            logger.error(f"MinIO Upload Error: {e}")
            raise e

    def get_presigned_url(self, object_name: str) -> str:
        try:
            return self.client.get_presigned_url(
                "GET",
                settings.MINIO_BUCKET,
                object_name,
            )
        except Exception:
            return ""

upload_service = UploadService()
