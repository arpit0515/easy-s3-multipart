
import pytest
from moto import mock_aws
import boto3
from datetime import datetime, timedelta

from easy_s3_multipart.handler import S3MultipartHandler
from easy_s3_multipart.exceptions import (
    S3ValidationError,
    S3InitiationError,
    S3UploadError,
    S3DeleteError,
)
from easy_s3_multipart.config import S3Config


BUCKET = "test-bucket"


def create_handler():
    """
    Helper: Initializes handler with test credentials.
    Moto intercepts AWS calls, so no real AWS is used.
    """
    return S3MultipartHandler(
        bucket_name=BUCKET,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region="us-east-1",
    )


# -------------------------------------------------------------------------
# INITIATE UPLOAD
# -------------------------------------------------------------------------
@mock_aws
def test_initiate_upload_success():
    """Ensure multipart upload initiates properly."""
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket=BUCKET)

    handler = create_handler()

    response = handler.initiate_upload(
        filename="myfile.txt",
        file_size=5_000_000,
        content_type="text/plain",
    )

    assert response.upload_id
    assert response.key.endswith("myfile.txt")
    assert response.bucket == BUCKET
    assert response.parts_count > 0


@mock_aws
def test_initiate_upload_file_too_large():
    """File should fail validation if larger than config limit."""
    handler = create_handler()
    handler.config.max_file_size = 10  # Set tiny limit for test

    with pytest.raises(S3ValidationError):
        handler.initiate_upload("big.bin", file_size=999)


# -------------------------------------------------------------------------
# PRESIGNED URL GENERATION
# -------------------------------------------------------------------------
@mock_aws
def test_generate_presigned_url():
    """Ensure presigned URLs are generated for part uploads."""
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket=BUCKET)

    handler = create_handler()
    init = handler.initiate_upload("photo.jpg", 2000)

    url_response = handler.generate_presigned_url(
        upload_id=init.upload_id, key=init.key, part_number=1
    )

    assert "https://" in url_response.url
    assert url_response.part_number == 1


@mock_aws
def test_generate_presigned_url_invalid_part():
    handler = create_handler()

    with pytest.raises(S3ValidationError):
        handler.generate_presigned_url("upload", "key", part_number=0)


# -------------------------------------------------------------------------
# COMPLETE MULTIPART UPLOAD
# -------------------------------------------------------------------------
@mock_aws
def test_complete_upload_success():
    """Moto allows us to simulate completing a multipart upload."""
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket=BUCKET)

    handler = create_handler()
    init = handler.initiate_upload("data.bin", 5000)

    # Fake uploaded parts
    fake_parts = [
        {"PartNumber": 1, "ETag": "etag1"},
        {"PartNumber": 2, "ETag": "etag2"},
    ]

    response = handler.complete_upload(
        upload_id=init.upload_id,
        key=init.key,
        parts=fake_parts,
    )

    assert response.success is True
    assert response.key == init.key
    assert response.bucket == BUCKET


@mock_aws
def test_complete_upload_no_parts():
    handler = create_handler()

    with pytest.raises(S3ValidationError):
        handler.complete_upload("upload", "key", parts=[])


# -------------------------------------------------------------------------
# ABORT UPLOAD
# -------------------------------------------------------------------------
@mock_aws
def test_abort_upload_success():
    """Abort should not throw errors when upload exists."""
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket=BUCKET)

    handler = create_handler()
    init = handler.initiate_upload("temp.bin", 1234)

    # Should not raise exception
    handler.abort_upload(upload_id=init.upload_id, key=init.key)


# -------------------------------------------------------------------------
# LIST FILES
# -------------------------------------------------------------------------
@mock_aws
def test_list_files_paginated():
    """Ensure list_files returns correct pagination."""
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket=BUCKET)

    # Upload example files
    for i in range(5):
        s3.put_object(
            Bucket=BUCKET,
            Key=f"uploads/2025/01/01/file{i}.txt",
            Body=b"hello",
        )

    handler = create_handler()
    resp = handler.list_files(page=1, page_size=2)

    assert resp.total_count == 5
    assert resp.page == 1
    assert resp.page_size == 2
    assert len(resp.files) == 2  # page size
    assert resp.total_pages == 3


# -------------------------------------------------------------------------
# DOWNLOAD URL
# -------------------------------------------------------------------------
@mock_aws
def test_generate_download_url():
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket=BUCKET)

    handler = create_handler()
    url = handler.generate_download_url("myfile.txt")

    assert "https://" in url


# -------------------------------------------------------------------------
# DELETE FILE
# -------------------------------------------------------------------------
@mock_aws
def test_delete_file_success():
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket=BUCKET)

    s3.put_object(Bucket=BUCKET, Key="delete_me.txt", Body=b"data")

    handler = create_handler()
    handler.delete_file("delete_me.txt")  # Should not raise


# -------------------------------------------------------------------------
# CLEANUP INCOMPLETE UPLOADS
# -------------------------------------------------------------------------
@mock_aws
def test_cleanup_incomplete_uploads():
    """Moto supports multipart uploads metadata."""

    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket=BUCKET)

    # Create a multipart upload
    upload = s3.create_multipart_upload(Bucket=BUCKET, Key="stale-file.dat")

    handler = create_handler()

    # Monkeypatch upload date to simulate an old upload
    old_date = datetime.utcnow() - timedelta(days=10)
    s3.list_multipart_uploads()["Uploads"][0]["Initiated"] = old_date

    cleaned_count = handler.cleanup_incomplete_uploads(days_old=7)

    assert cleaned_count == 1
