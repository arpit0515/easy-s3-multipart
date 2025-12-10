"""
================================================================================
Package:        easy_s3_multipart
Module:         models.py
Description:    Pydantic Models

Author:         Arpit
Version:        0.1.0
Git Repo:       https://github.com/arpit0515/easy-s3-multipart
Created On:     12/10/2025 (MM/DD/YYYY)
Last Updated:   12/10/2025 (MM/DD/YYYY)

Notes:
    - The pydantic models for schema validation
================================================================================

"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, List
from datetime import datetime


class InitiateUploadRequest(BaseModel):
    """Request model for initiating multipart upload

    Attributes:
        filename: Name of the file to upload
        file_size: Total size of the file in bytes
        content_type: MIME type of the file
        metadata: Optional custom metadata key-value pairs
    """

    filename: str = Field(..., min_length=1, max_length=1024)
    file_size: int = Field(..., gt=0)
    content_type: Optional[str] = Field(default="application/octet-stream")
    metadata: Optional[Dict[str, str]] = Field(default_factory=dict)

    @field_validator("filename")
    def validate_filename(cls, v):
        """Validate filename doesn't contain path separators"""
        if "/" in v or "\\" in v:
            raise ValueError("Filename cannot contain path separators")
        return v


class InitiateUploadResponse(BaseModel):
    """Response model for initiated upload

    Attributes:
        upload_id: Unique identifier for the multipart upload
        key: S3 object key where file will be stored
        bucket: S3 bucket name
        parts_count: Number of parts the file will be split into
        part_size: Size of each part in bytes
    """

    upload_id: str
    key: str
    bucket: str
    parts_count: int
    part_size: int


class PresignedUrlRequest(BaseModel):
    """Request model for getting presigned URL

    Attributes:
        upload_id: Upload ID from initiation
        key: S3 object key
        part_number: Part number (1-indexed)
    """

    upload_id: str
    key: str
    part_number: int = Field(..., ge=1, le=10000)


class PresignedUrlResponse(BaseModel):
    """Response model for presigned URL

    Attributes:
        url: Presigned URL for uploading the part
        part_number: Part number this URL is for
        expires_in: Seconds until URL expires
    """

    url: str
    part_number: int
    expires_in: int


class PartInfo(BaseModel):
    """Information about an uploaded part

    Attributes:
        PartNumber: Part number (1-indexed)
        ETag: ETag returned by S3 after upload
    """

    PartNumber: int = Field(..., ge=1)
    ETag: str


class CompleteUploadRequest(BaseModel):
    """Request model for completing multipart upload

    Attributes:
        upload_id: Upload ID from initiation
        key: S3 object key
        parts: List of uploaded parts with ETags
    """

    upload_id: str
    key: str
    parts: List[PartInfo]

    @field_validator("parts")
    def validate_parts(cls, v):
        """Ensure parts are sorted and sequential"""
        if not v:
            raise ValueError("Parts list cannot be empty")
        part_numbers = [p.PartNumber for p in v]
        if sorted(part_numbers) != part_numbers:
            raise ValueError("Parts must be sorted by PartNumber")
        return v


class CompleteUploadResponse(BaseModel):
    """Response model for completed upload

    Attributes:
        success: Whether upload completed successfully
        location: S3 URL of uploaded file
        key: S3 object key
        bucket: S3 bucket name
    """

    success: bool
    location: str
    key: str
    bucket: str


class S3FileInfo(BaseModel):
    """Information about a file in S3

    Attributes:
        key: S3 object key
        filename: Extracted filename
        size: File size in bytes
        last_modified: Last modification timestamp
        etag: S3 ETag
    """

    key: str
    filename: str
    size: int
    last_modified: str
    etag: Optional[str] = None


class ListFilesResponse(BaseModel):
    """Response model for file listing

    Attributes:
        files: List of files
        total_count: Total number of files
        page: Current page number
        page_size: Number of items per page
        total_pages: Total number of pages
    """

    files: List[S3FileInfo]
    total_count: int
    page: int
    page_size: int
    total_pages: int
