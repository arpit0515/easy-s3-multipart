"""
================================================================================
Package:        easy_s3_multipart
Module:         test_models.py
Description:    Testing the models

Author:         Arpit
Version:        0.1.0
Git Repo:       https://github.com/arpit0515/easy-s3-multipart
Created On:     12/10/2025 (MM/DD/YYYY)
Last Updated:   12/10/2025 (MM/DD/YYYY)

Notes:
    - Tests for simple data models.
    - These tests only verify:
    - attributes exist
    - attributes types behave as expected
    - model init does not crash
================================================================================
"""

from fastapi_s3_multipart.models import (
    InitiateUploadResponse,
    PresignedUrlResponse,
    CompleteUploadResponse,
    ListFilesResponse,
    S3FileInfo,
)


def test_initiate_upload_response():
    model = InitiateUploadResponse(
        upload_id="123",
        key="uploads/2025/01/01/file.txt",
        bucket="my-bucket",
        parts_count=5,
        part_size=5_000_000,
    )

    assert model.upload_id == "123"
    assert model.parts_count == 5
    assert model.bucket == "my-bucket"
    assert model.key.endswith("file.txt")


def test_presigned_url_response():
    model = PresignedUrlResponse(
        url="https://example.com",
        part_number=1,
        expires_in=3600,
    )

    assert model.url.startswith("https://")
    assert model.part_number == 1
    assert model.expires_in == 3600


def test_complete_upload_response():
    model = CompleteUploadResponse(
        success=True,
        location="https://s3.amazonaws.com/myfile",
        key="uploads/myfile.txt",
        bucket="test-bucket",
    )

    assert model.success is True
    assert model.location.startswith("https://")
    assert model.key.endswith("myfile.txt")
    assert model.bucket == "test-bucket"


def test_s3_file_info():
    model = S3FileInfo(
        key="uploads/2025/01/01/photo.png",
        filename="photo.png",
        size=2048,
        last_modified="2025-01-01T00:00:00",
        etag="123etag",
    )

    assert model.filename == "photo.png"
    assert model.size == 2048
    assert model.etag == "123etag"


def test_list_files_response():
    files = [
        S3FileInfo(
            key="uploads/a.txt",
            filename="a.txt",
            size=1,
            last_modified="2025-01-01T00:00:00",
            etag="etag1",
        ),
        S3FileInfo(
            key="uploads/b.txt",
            filename="b.txt",
            size=2,
            last_modified="2025-01-01T00:00:00",
            etag="etag2",
        ),
    ]

    resp = ListFilesResponse(
        files=files,
        total_count=2,
        page=1,
        page_size=20,
        total_pages=1,
    )

    assert resp.total_count == 2
    assert len(resp.files) == 2
    assert resp.page == 1
    assert resp.total_pages == 1
