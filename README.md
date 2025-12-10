# FastAPI S3 Multipart Upload Handler

A production-ready Python library for handling large file uploads to AWS S3 using multipart uploads with presigned URLs in FastAPI applications.

## Features

- ✅ Multipart upload with configurable chunk sizes
- ✅ Presigned URL generation for direct client-to-S3 uploads
- ✅ Progress tracking support
- ✅ File listing with pagination
- ✅ Download URL generation
- ✅ File deletion
- ✅ Automatic cleanup of incomplete uploads
- ✅ Comprehensive error handling
- ✅ Type-safe with Pydantic models
- ✅ AI-friendly documentation

## Installation

```bash
pip install fastapi-s3-multipart
```

## Quick Start

```python
from fastapi import FastAPI
from fastapi_s3_multipart import S3MultipartHandler

app = FastAPI()

# Initialize handler
s3_handler = S3MultipartHandler(
    bucket_name="your-bucket",
    aws_access_key_id="your-key",
    aws_secret_access_key="your-secret",
    region="us-east-1"
)

# Initiate upload
@app.post("/upload/initiate")
async def initiate_upload(filename: str, file_size: int):
    return s3_handler.initiate_upload(
        filename=filename,
        file_size=file_size,
        content_type="application/pdf"
    )

# Generate presigned URL for part
@app.post("/upload/presigned-url")
async def get_presigned_url(upload_id: str, key: str, part_number: int):
    return s3_handler.generate_presigned_url(
        upload_id=upload_id,
        key=key,
        part_number=part_number
    )

# Complete upload
@app.post("/upload/complete")
async def complete_upload(upload_id: str, key: str, parts: list):
    return s3_handler.complete_upload(
        upload_id=upload_id,
        key=key,
        parts=parts
    )
```

## Complete API Examples

### Upload Flow

```python
# 1. Client initiates upload
result = s3_handler.initiate_upload(
    filename="large-video.mp4",
    file_size=104857600,  # 100MB
    content_type="video/mp4",
    metadata={"uploader": "user123"}
)
# Returns: upload_id, key, parts_count, part_size

# 2. Client requests presigned URLs for each part
for part_num in range(1, result.parts_count + 1):
    url_response = s3_handler.generate_presigned_url(
        upload_id=result.upload_id,
        key=result.key,
        part_number=part_num
    )
    # Client uploads part directly to S3 using this URL

# 3. Client completes upload
response = s3_handler.complete_upload(
    upload_id=result.upload_id,
    key=result.key,
    parts=[
        {"PartNumber": 1, "ETag": "etag1"},
        {"PartNumber": 2, "ETag": "etag2"},
    ]
)
```

### File Management

```python
# List files with pagination
files = s3_handler.list_files(
    prefix="uploads/",
    page=1,
    page_size=20
)

# Generate download URL
download_url = s3_handler.generate_download_url(
    key="uploads/2024/01/15/file.pdf",
    expires_in=3600
)

# Delete file
s3_handler.delete_file(key="uploads/2024/01/15/file.pdf")

# Cleanup old incomplete uploads
cleaned = s3_handler.cleanup_incomplete_uploads(days_old=7)
```

## Advanced Configuration

```python
from fastapi_s3_multipart import S3MultipartHandler, S3Config

config = S3Config(
    bucket_name="my-bucket",
    aws_access_key_id="...",
    aws_secret_access_key="...",
    region="...",
    part_size=10 * 1024 * 1024,  # 10MB parts
    presigned_url_expiry=7200,  # 2 hours
    max_file_size=10 * 1024 * 1024 * 1024,  # 10GB limit
    allowed_extensions=["pdf", "mp4", "zip"]  # Restrict file types
)

handler = S3MultipartHandler(
    bucket_name=config.bucket_name,
    aws_access_key_id=config.aws_access_key_id,
    aws_secret_access_key=config.aws_secret_access_key,
    region=config.region,
    config=config
)
```

## Error Handling

```python
from fastapi_s3_multipart.exceptions import (
    S3ValidationError,
    S3InitiationError,
    S3UploadError
)

try:
    result = s3_handler.initiate_upload(
        filename="file.pdf",
        file_size=1000000000000  # Too large
    )
except S3ValidationError as e:
    print(f"Validation failed: {e}")
except S3InitiationError as e:
    print(f"Upload initiation failed: {e}")
```
