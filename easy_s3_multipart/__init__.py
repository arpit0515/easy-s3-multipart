"""FastAPI S3 Multipart Upload Handler

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
    from fastapi_s3_multipart import S3MultipartHandler
    
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
