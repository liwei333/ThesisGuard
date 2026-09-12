"""MinIO (S3-compatible) object storage client."""

import io
from typing import Optional

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from backend.common.config import settings


class StorageClient:
    """MinIO/S3 object storage client."""

    def __init__(self) -> None:
        self._client = None
        self._bucket = settings.MINIO_BUCKET

    @property
    def client(self):
        """Lazy-initialize S3 client."""
        if self._client is None:
            protocol = "https" if settings.MINIO_SECURE else "http"
            self._client = boto3.client(
                "s3",
                endpoint_url=f"{protocol}://{settings.MINIO_ENDPOINT}",
                aws_access_key_id=settings.MINIO_ACCESS_KEY,
                aws_secret_access_key=settings.MINIO_SECRET_KEY,
                region_name=settings.MINIO_REGION,
                config=Config(signature_version="s3v4"),
            )
        return self._client

    def ensure_bucket(self) -> None:
        """Create the bucket if it doesn't exist."""
        try:
            self.client.head_bucket(Bucket=self._bucket)
        except ClientError:
            self.client.create_bucket(Bucket=self._bucket)

    def put_object(
        self,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Upload an object to storage. Returns the object key."""
        self.client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        return key

    def get_object(self, key: str) -> Optional[bytes]:
        """Download an object. Returns None if not found."""
        try:
            response = self.client.get_object(Bucket=self._bucket, Key=key)
            return response["Body"].read()
        except ClientError:
            return None

    def delete_object(self, key: str) -> bool:
        """Delete an object. Returns True if successful."""
        try:
            self.client.delete_object(Bucket=self._bucket, Key=key)
            return True
        except ClientError:
            return False

    def object_exists(self, key: str) -> bool:
        """Check if an object exists."""
        try:
            self.client.head_object(Bucket=self._bucket, Key=key)
            return True
        except ClientError:
            return False

    def health_check(self) -> bool:
        """Check if MinIO is reachable and bucket exists."""
        try:
            self.ensure_bucket()
            self.client.head_bucket(Bucket=self._bucket)
            return True
        except Exception:
            return False


# Singleton instance
storage = StorageClient()
