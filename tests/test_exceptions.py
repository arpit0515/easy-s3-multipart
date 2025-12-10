"""
Very simple tests — verifying that custom exceptions
can be instantiated and are subclasses of Exception.
"""

from fastapi_s3_multipart.exceptions import (
    S3InitiationError,
    S3UploadError,
    S3ValidationError,
    S3DeleteError,
)


def test_s3_initiation_error():
    err = S3InitiationError("init failed")
    assert isinstance(err, Exception)
    assert "failed" in str(err)


def test_s3_upload_error():
    err = S3UploadError("upload failed")
    assert isinstance(err, Exception)
    assert "upload" in str(err)


def test_s3_validation_error():
    err = S3ValidationError("invalid file")
    assert isinstance(err, Exception)
    assert "invalid" in str(err)


def test_s3_delete_error():
    err = S3DeleteError("delete failed")
    assert isinstance(err, Exception)
    assert "delete" in str(err)
