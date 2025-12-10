"""
================================================================================
Package:        easy_s3_multipart
Module:         __init__.py
Description:    Core of the package, handles the core class

Author:         Arpit
Version:        0.1.0
Git Repo:       https://github.com/arpit0515/easy-s3-multipart
Created On:     12/10/2025 (MM/DD/YYYY)
Last Updated:   12/10/2025 (MM/DD/YYYY)

Notes:
    - This is what will be used to get the job done. The class is here.
================================================================================

"""

import boto3
from botocore.exceptions import ClientError, BotoCoreError
from datetime import datetime
from typing import Dict, List, Optional
import logging

from .config import S3Config
from .models import (
    InitiateUploadResponse,
    PresignedUrlResponse,
    CompleteUploadResponse,
    ListFilesResponse,
    S3FileInfo,
)
from .exceptions import (
    S3InitiationError,
    S3UploadError,
    S3ValidationError,
    S3DeleteError,
)

logger = logging.getLogger(__name__)


class S3MultipartHandler:
    """Handler for S3 multipart uploads with presigned URLs
    
    This class provides methods for:
    - Initiating multipart uploads
    - Generating presigned URLs for part uploads
    - Completing multipart uploads
    - Listing files with pagination
    - Generating download URLs
    - Deleting files
    - Aborting incomplete uploads
    
    Example:
        handler = S3MultipartHandler(
            bucket_name="my-bucket",
            aws_access_key_id="...",
            aws_secret_access_key="...",
            region="us-east-1"
        )
        
        # Initiate upload
        result = handler.initiate_upload(
            filename="large-file.pdf",
            file_size=104857600,
            content_type="application/pdf"
        )
        
        # Generate presigned URL for part 1
        url = handler.generate_presigned_url(
            upload_id=result.upload_id,
            key=result.key,
            part_number=1
        )
    """

    def __init__(
        self,
        bucket_name: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        region: str = "us-east-1",
        config: Optional[S3Config] = None,
    ):
        """Initialize S3 handler
        
        Args:
            bucket_name: S3 bucket name
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            region: AWS region (default: us-east-1)
            config: Optional S3Config for advanced settings
        """
        self.bucket_name = bucket_name
        self.config = config or S3Config(
            bucket_name=bucket_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region=region,
        )

        try:
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=region,
            )
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            raise S3InitiationError(f"Failed to initialize S3 client: {e}")

    def _validate_file(self, filename: str, file_size: int) -> None:
        """Validate file before upload
        
        Args:
            filename: Name of the file
            file_size: Size of the file in bytes
            
        Raises:
            S3ValidationError: If validation fails
        """
        if file_size > self.config.max_file_size:
            raise S3ValidationError(
                f"File size {file_size} exceeds maximum allowed size {self.config.max_file_size}"
            )

        if self.config.allowed_extensions:
            ext = filename.split(".")[-1].lower()
            if ext not in self.config.allowed_extensions:
                raise S3ValidationError(
                    f"File extension .{ext} not allowed. Allowed: {self.config.allowed_extensions}"
                )

    def _generate_s3_key(self, filename: str, prefix: str = "uploads") -> str:
        """Generate S3 key with date-based organization
        
        Args:
            filename: Name of the file
            prefix: Prefix for the key (default: uploads)
            
        Returns:
            Generated S3 key
        """
        timestamp = datetime.utcnow()
        return f"{prefix}/{timestamp.strftime('%Y/%m/%d')}/{timestamp.strftime('%H%M%S')}_{filename}"

    def initiate_upload(
        self,
        filename: str,
        file_size: int,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None,
        custom_key: Optional[str] = None,
    ) -> InitiateUploadResponse:
        """Initiate a multipart upload
        
        Args:
            filename: Name of the file to upload
            file_size: Total size of the file in bytes
            content_type: MIME type of the file
            metadata: Optional custom metadata
            custom_key: Optional custom S3 key (overrides auto-generated key)
            
        Returns:
            InitiateUploadResponse with upload details
            
        Raises:
            S3ValidationError: If file validation fails
            S3InitiationError: If upload initiation fails
        """
        self._validate_file(filename, file_size)

        key = custom_key or self._generate_s3_key(filename)
        metadata = metadata or {}

        try:
            response = self.s3_client.create_multipart_upload(
                Bucket=self.bucket_name,
                Key=key,
                ContentType=content_type,
                Metadata=metadata,
            )

            upload_id = response["UploadId"]
            parts_count = (file_size + self.config.part_size - 1) // self.config.part_size

            logger.info(
                f"Initiated upload: {upload_id} for {filename} ({parts_count} parts)"
            )

            return InitiateUploadResponse(
                upload_id=upload_id,
                key=key,
                bucket=self.bucket_name,
                parts_count=parts_count,
                part_size=self.config.part_size,
            )

        except (ClientError, BotoCoreError) as e:
            logger.error(f"Failed to initiate upload: {e}")
            raise S3InitiationError(f"Failed to initiate multipart upload: {e}")

    def generate_presigned_url(
        self, upload_id: str, key: str, part_number: int
    ) -> PresignedUrlResponse:
        """Generate presigned URL for uploading a part
        
        Args:
            upload_id: Upload ID from initiation
            key: S3 object key
            part_number: Part number (1-indexed)
            
        Returns:
            PresignedUrlResponse with the URL
            
        Raises:
            S3UploadError: If URL generation fails
        """
        if part_number < 1 or part_number > 10000:
            raise S3ValidationError("Part number must be between 1 and 10000")

        try:
            url = self.s3_client.generate_presigned_url(
                "upload_part",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": key,
                    "UploadId": upload_id,
                    "PartNumber": part_number,
                },
                ExpiresIn=self.config.presigned_url_expiry,
            )

            return PresignedUrlResponse(
                url=url,
                part_number=part_number,
                expires_in=self.config.presigned_url_expiry,
            )

        except (ClientError, BotoCoreError) as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise S3UploadError(f"Failed to generate presigned URL: {e}")

    def complete_upload(
        self, upload_id: str, key: str, parts: List[Dict[str, any]]
    ) -> CompleteUploadResponse:
        """Complete a multipart upload
        
        Args:
            upload_id: Upload ID from initiation
            key: S3 object key
            parts: List of parts with PartNumber and ETag
            
        Returns:
            CompleteUploadResponse with upload details
            
        Raises:
            S3UploadError: If completion fails
        """
        if not parts:
            raise S3ValidationError("Parts list cannot be empty")

        # Sort parts by PartNumber
        parts_sorted = sorted(parts, key=lambda x: x["PartNumber"])

        try:
            response = self.s3_client.complete_multipart_upload(
                Bucket=self.bucket_name,
                Key=key,
                UploadId=upload_id,
                MultipartUpload={"Parts": parts_sorted},
            )

            logger.info(f"Completed upload: {upload_id} for key: {key}")

            return CompleteUploadResponse(
                success=True,
                location=response["Location"],
                key=key,
                bucket=self.bucket_name,
            )

        except (ClientError, BotoCoreError) as e:
            logger.error(f"Failed to complete upload: {e}")
            raise S3UploadError(f"Failed to complete multipart upload: {e}")

    def abort_upload(self, upload_id: str, key: str) -> None:
        """Abort a multipart upload
        
        Args:
            upload_id: Upload ID to abort
            key: S3 object key
            
        Raises:
            S3UploadError: If abort fails
        """
        try:
            self.s3_client.abort_multipart_upload(
                Bucket=self.bucket_name, Key=key, UploadId=upload_id
            )
            logger.info(f"Aborted upload: {upload_id}")

        except (ClientError, BotoCoreError) as e:
            logger.error(f"Failed to abort upload: {e}")
            raise S3UploadError(f"Failed to abort multipart upload: {e}")

    def list_files(
        self, prefix: str = "uploads/", page: int = 1, page_size: int = 20
    ) -> ListFilesResponse:
        """List files from S3 with pagination
        
        Args:
            prefix: S3 prefix to filter files
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            ListFilesResponse with paginated files
            
        Raises:
            S3UploadError: If listing fails
        """
        try:
            paginator = self.s3_client.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix)

            all_objects = []
            for page_response in pages:
                if "Contents" in page_response:
                    all_objects.extend(page_response["Contents"])

            # Sort by last modified (newest first)
            all_objects.sort(key=lambda x: x["LastModified"], reverse=True)

            # Pagination
            total_count = len(all_objects)
            total_pages = (total_count + page_size - 1) // page_size
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size

            paginated_objects = all_objects[start_idx:end_idx]

            files = [
                S3FileInfo(
                    key=obj["Key"],
                    filename=obj["Key"].split("/")[-1],
                    size=obj["Size"],
                    last_modified=obj["LastModified"].isoformat(),
                    etag=obj.get("ETag", "").strip('"'),
                )
                for obj in paginated_objects
            ]

            return ListFilesResponse(
                files=files,
                total_count=total_count,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
            )

        except (ClientError, BotoCoreError) as e:
            logger.error(f"Failed to list files: {e}")
            raise S3UploadError(f"Failed to list files: {e}")

    def generate_download_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate presigned download URL
        
        Args:
            key: S3 object key
            expires_in: URL expiry time in seconds (default: 3600)
            
        Returns:
            Presigned download URL
            
        Raises:
            S3UploadError: If URL generation fails
        """
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": key},
                ExpiresIn=expires_in,
            )
            return url

        except (ClientError, BotoCoreError) as e:
            logger.error(f"Failed to generate download URL: {e}")
            raise S3UploadError(f"Failed to generate download URL: {e}")

    def delete_file(self, key: str) -> None:
        """Delete a file from S3
        
        Args:
            key: S3 object key to delete
            
        Raises:
            S3DeleteError: If deletion fails
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            logger.info(f"Deleted file: {key}")

        except (ClientError, BotoCoreError) as e:
            logger.error(f"Failed to delete file: {e}")
            raise S3DeleteError(f"Failed to delete file: {e}")

    def cleanup_incomplete_uploads(self, days_old: int = 7) -> int:
        """Clean up incomplete multipart uploads older than specified days
        
        Args:
            days_old: Delete uploads older than this many days
            
        Returns:
            Number of uploads cleaned up
            
        Raises:
            S3UploadError: If cleanup fails
        """
        try:
            response = self.s3_client.list_multipart_uploads(Bucket=self.bucket_name)
            
            if "Uploads" not in response:
                return 0

            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            cleaned = 0

            for upload in response["Uploads"]:
                if upload["Initiated"] < cutoff_date:
                    self.abort_upload(upload["UploadId"], upload["Key"])
                    cleaned += 1

            logger.info(f"Cleaned up {cleaned} incomplete uploads")
            return cleaned

        except (ClientError, BotoCoreError) as e:
            logger.error(f"Failed to cleanup incomplete uploads: {e}")
            raise S3UploadError(f"Failed to cleanup incomplete uploads: {e}")

