"""S3 storage service."""
import logging
from typing import Optional
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class S3Storage:
    """S3-compatible storage service."""

    def __init__(self):
        self.settings = get_settings()
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import boto3
                self._client = boto3.client(
                    "s3",
                    aws_access_key_id=self.settings.AWS_ACCESS_KEY_ID or None,
                    aws_secret_access_key=self.settings.AWS_SECRET_ACCESS_KEY or None,
                    region_name=self.settings.AWS_REGION,
                )
            except Exception as e:
                logger.error(f"Failed to create S3 client: {e}")
                return None
        return self._client

    async def upload_file(self, file_bytes: bytes, key: str, content_type: str = "application/octet-stream") -> Optional[str]:
        """Upload a file to S3. Returns the S3 URL."""
        client = self._get_client()
        if not client:
            logger.warning("S3 client not available")
            return None

        try:
            client.put_object(
                Bucket=self.settings.AWS_BUCKET_NAME,
                Key=key,
                Body=file_bytes,
                ContentType=content_type,
            )
            return f"https://{self.settings.AWS_BUCKET_NAME}.s3.{self.settings.AWS_REGION}.amazonaws.com/{key}"
        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
            return None

    def get_presigned_url(self, key: str, expires_in: int = 3600) -> Optional[str]:
        """Generate a presigned URL for file access."""
        client = self._get_client()
        if not client:
            return None

        try:
            return client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.settings.AWS_BUCKET_NAME, "Key": key},
                ExpiresIn=expires_in,
            )
        except Exception as e:
            logger.error(f"Presigned URL generation failed: {e}")
            return None

    async def delete_file(self, key: str) -> bool:
        """Delete a file from S3."""
        client = self._get_client()
        if not client:
            return False

        try:
            client.delete_object(Bucket=self.settings.AWS_BUCKET_NAME, Key=key)
            return True
        except Exception as e:
            logger.error(f"S3 delete failed: {e}")
            return False


# Singleton instance
storage = S3Storage()
