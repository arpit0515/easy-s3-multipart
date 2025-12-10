"""
================================================================================
Package:        easy_s3_multipart
Module:         config.py
Description:    Setting up the configuration

Author:         Arpit
Version:        0.1.0
Git Repo:       https://github.com/arpit0515/easy-s3-multipart
Created On:     12/10/2025 (MM/DD/YYYY)
Last Updated:   12/10/2025 (MM/DD/YYYY)

Notes:
    - Sets the configuration for the class params.
================================================================================

"""

from pydantic import BaseModel, Field
from typing import Optional


class S3Config(BaseModel):
    """S3 configuration settings

    Attributes:
        bucket_name: S3 bucket name
        aws_access_key_id: AWS access key ID
        aws_secret_access_key: AWS secret access key
        region: AWS region (default: us-east-1)
        part_size: Size of each upload part in bytes (default: 5MB, minimum for S3)
        presigned_url_expiry: Expiry time for presigned URLs in seconds (default: 3600)
        max_file_size: Maximum allowed file size in bytes (default: 5GB)
        allowed_extensions: List of allowed file extensions (None = all allowed)
    """

    bucket_name: str
    aws_access_key_id: str
    aws_secret_access_key: str
    region: str = "us-east-1"
    part_size: int = Field(default=5 * 1024 * 1024, ge=5 * 1024 * 1024)  # 5MB minimum
    presigned_url_expiry: int = Field(default=3600, ge=60, le=604800)  # 1 min to 7 days
    max_file_size: int = Field(default=5 * 1024 * 1024 * 1024)  # 5GB
    allowed_extensions: Optional[list[str]] = None
