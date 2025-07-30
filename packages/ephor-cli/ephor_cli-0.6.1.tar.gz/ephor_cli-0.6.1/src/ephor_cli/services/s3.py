import boto3
import logging
from botocore.exceptions import ClientError
from typing import Dict
import mimetypes
import uuid
from ephor_cli.constant import AWS_S3_BUCKET

logger = logging.getLogger(__name__)


class S3Service:
    def __init__(self):
        self.bucket_name = AWS_S3_BUCKET
        try:
            self.s3_client = boto3.client("s3")
            # Verify bucket exists
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                logger.error(f"Bucket {self.bucket_name} does not exist")
            elif error_code == "403":
                logger.error(f"Access denied to bucket {self.bucket_name}")
            else:
                logger.error(f"Error connecting to S3: {e}")
            raise
        self.region = "us-east-1"  # Default region

    def get_file_content(self, s3_key: str) -> bytes:
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
            content = response["Body"].read()
            return content
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "NoSuchKey":
                logger.error(f"File not found in S3: {s3_key}")
            elif error_code == "AccessDenied":
                logger.error(f"Access denied to file in S3: {s3_key}")
            else:
                logger.error(f"Error fetching file from S3: {e}")
            return b""

    def generate_upload_url(
        self, file_name: str, content_type: str, expiration: int = 3600
    ) -> Dict[str, str]:
        try:
            # Generate a unique S3 key
            file_extension = mimetypes.guess_extension(content_type) or ""
            s3_key = f"uploads/{uuid.uuid4()}{file_extension}"

            url = self.s3_client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": s3_key,
                    "ContentType": content_type,
                },
                ExpiresIn=expiration,
            )

            return {"upload_url": url, "s3_key": s3_key, "content_type": content_type}
        except ClientError as e:
            logger.error(f"Error generating upload URL: {e}")
            return {}
