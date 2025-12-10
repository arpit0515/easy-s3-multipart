"""
================================================================================
Package:        easy_s3_multipart
Module:         __init__.py
Description:    Sets up the package

Author:         Arpit
Version:        0.1.0
Git Repo:       https://github.com/arpit0515/easy-s3-multipart
Created On:     12/10/2025 (MM/DD/YYYY)
Last Updated:   12/10/2025 (MM/DD/YYYY)

Notes:
    - Helps everyone understand what this package is for.
================================================================================

FastAPI S3 Multipart Upload Handler

A production-ready library for handling large file uploads to AWS S3 using
multipart upload with presigned URLs in FastAPI applications.

Key Features:
- Multipart upload with configurable chunk sizes
- Presigned URL generation for direct client-to-S3 uploads
- Progress tracking
- File listing with pagination
- Download URL generation
- File deletion
- Comprehensive error handling

Example:
    from easy_s3_multipart import S3MultipartHandler

    handler = S3MultipartHandler(
        bucket_name="my-bucket",
        aws_access_key_id="...",
        aws_secret_access_key="...",
        region="us-east-1"
    )

    # Initiate upload
    result = handler.initiate_upload(
        filename="document.pdf",
        file_size=10485760,
        content_type="application/pdf"
    )
"""

from .handler import S3MultipartHandler
from .models import (
    InitiateUploadRequest,
    InitiateUploadResponse,
    PresignedUrlRequest,
    PresignedUrlResponse,
    CompleteUploadRequest,
    CompleteUploadResponse,
    ListFilesResponse,
    S3FileInfo,
)
from .exceptions import (
    S3HandlerError,
    S3InitiationError,
    S3UploadError,
    S3ValidationError,
)
from .config import S3Config

__version__ = "0.1.0"
__all__ = [
    "S3MultipartHandler",
    "S3Config",
    "InitiateUploadRequest",
    "InitiateUploadResponse",
    "PresignedUrlRequest",
    "PresignedUrlResponse",
    "CompleteUploadRequest",
    "CompleteUploadResponse",
    "ListFilesResponse",
    "S3FileInfo",
    "S3HandlerError",
    "S3InitiationError",
    "S3UploadError",
    "S3ValidationError",
]
