import boto3
import os
import uuid
from botocore.exceptions import NoCredentialsError
from app.utils.gr_logger import setup_logger


class S3Service:
    """Service for handling S3 operations"""

    def __init__(self):
        """Initialize S3 service with AWS credentials from environment variables"""
        self.logger = setup_logger(__name__)
        self.logger.info("Initializing S3Service")
        
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_REGION'),
            endpoint_url=os.environ.get('AWS_S3_ENDPOINT')
        )
        self.bucket_name = os.environ.get('S3_BUCKET_NAME')
        self.s3_access_host = os.environ.get('S3_ACCESS_HOST')
        self.s3_prefix_path = "docs"
        
        self.logger.debug(f"S3 bucket configured: {self.bucket_name}")
        self.logger.debug(f"S3 access host: {self.s3_access_host}")

    def upload_file(self, file_path):
        """Upload a file to S3 and return the public URL

        Args:
            file_path (str): Path to the file to upload

        Returns:
            str: Public URL of the uploaded file or None if upload failed
        """
        try:
            self.logger.info(f"Uploading file to S3: {file_path}")
            
            # Generate a unique filename to avoid collisions
            file_extension = os.path.splitext(file_path)[1]
            unique_filename = f"{self.s3_prefix_path}/{uuid.uuid4()}{file_extension}"
            
            self.logger.debug(f"Generated unique filename: {unique_filename}")

            # Upload the file to S3
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                unique_filename,
                ExtraArgs={'ACL': 'public-read'}
            )

            # Generate the public URL
            url = f"{self.s3_access_host}/{unique_filename}"
            self.logger.info(f"File successfully uploaded, URL: {url}")
            return url
        except NoCredentialsError:
            self.logger.error("AWS credentials not available")
            return None
        except Exception as e:
            self.logger.error(f"Error uploading file to S3: {e}", exc_info=True)
            return None
