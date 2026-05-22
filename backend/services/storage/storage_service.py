import os
import boto3
import logging
from typing import Optional
from botocore.exceptions import ClientError
from config import settings

logger = logging.getLogger(__name__)

class StorageService:
    """
    Service for managing cloud storage uploads (S3-compatible, R2, MinIO)
    and mapping output URLs to a high-speed CDN.
    """
    def __init__(self):
        self.bucket = settings.S3_BUCKET
        self.enabled = bool(self.bucket)
        self.s3_client = None

        if self.enabled:
            try:
                session = boto3.Session(
                    aws_access_key_id=settings.S3_ACCESS_KEY,
                    aws_secret_access_key=settings.S3_SECRET_KEY,
                )
                # Supports endpoint overrides for providers like Cloudflare R2, MinIO, or DigitalOcean Spaces
                self.s3_client = session.client(
                    's3',
                    endpoint_url=settings.S3_ENDPOINT_URL
                )
                logger.info(f"StorageService initialized successfully with bucket: {self.bucket}")
            except Exception as e:
                logger.error(f"Failed to initialize S3 client: {e}. Falling back to local storage.")
                self.enabled = False

    def upload_file(self, local_path: str, s3_key: str, content_type: Optional[str] = None) -> Optional[str]:
        """
        Uploads a local file to S3. Returns the S3 URL or CDN mapped URL.
        """
        if not self.enabled:
            logger.debug(f"Cloud storage disabled. Using local file reference: {local_path}")
            return f"{settings.STATIC_URL_PREFIX}/{os.path.basename(local_path)}"

        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
                
            self.s3_client.upload_file(
                Filename=local_path,
                Bucket=self.bucket,
                Key=s3_key,
                ExtraArgs=extra_args
            )
            logger.info(f"Successfully uploaded {local_path} to S3 key: {s3_key}")
            return self.get_url(s3_key)
        except ClientError as e:
            logger.error(f"S3 upload client error for key {s3_key}: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to upload file to S3: {e}")
            return None

    def get_url(self, s3_key: str) -> str:
        """
        Retrieves the public or CDN URL for a given S3 key.
        """
        if not self.enabled:
            return f"{settings.STATIC_URL_PREFIX}/{s3_key}"

        if settings.CDN_BASE_URL:
            # Custom CDN URL mapping
            base_cdn = settings.CDN_BASE_URL.rstrip('/')
            return f"{base_cdn}/{s3_key}"
            
        # Standard S3 endpoint URL resolution
        endpoint = settings.S3_ENDPOINT_URL or "https://s3.amazonaws.com"
        # Extract protocol and hostname
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            proto, host = endpoint.split("://", 1)
            return f"{proto}://{self.bucket}.{host}/{s3_key}"
        return f"https://{self.bucket}.s3.amazonaws.com/{s3_key}"

    def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generates a pre-signed URL for temporary private resource access.
        """
        if not self.enabled:
            # Local dev fallback
            return f"{settings.STATIC_URL_PREFIX}/{s3_key}"

        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return response
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL for key {s3_key}: {e}")
            return None

# Singleton instance
storage_service = StorageService()
