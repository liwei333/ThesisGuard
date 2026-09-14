"""MinIO (S3-compatible) object storage client.

对象存储用于保存原始文件（PDF、研报等），结构化事实存数据库，
证据检索走 RAG。三层存储边界遵循 AGENTS.md 中的设计原则。
客户端采用懒加载：首次访问 .client 时建立 S3 连接。
"""

from typing import Any

import boto3
from backend.common.config import settings
from botocore.client import Config
from botocore.exceptions import ClientError


class StorageClient:
    """MinIO/S3 object storage client."""

    def __init__(self) -> None:
        self._client: Any = None
        self._bucket = settings.MINIO_BUCKET

    @property
    def client(self) -> Any:
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
        # head_bucket 失败说明 bucket 不存在，此时创建；其他 ClientError 向上抛出
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

    def get_object(self, key: str) -> bytes | None:
        """Download an object. Returns None if not found."""
        try:
            response = self.client.get_object(Bucket=self._bucket, Key=key)
            body = response["Body"]
            return bytes(body.read())
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
