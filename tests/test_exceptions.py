"""
================================================================================
Package:        easy_s3_multipart
Module:         test_exceptions.py
Description:    Testing the exceptions

Author:         Arpit
Version:        0.1.0
Git Repo:       https://github.com/arpit0515/easy-s3-multipart
Created On:     12/10/2025 (MM/DD/YYYY)
Last Updated:   12/10/2025 (MM/DD/YYYY)

Notes:
    - Very simple tests — verifying that custom exceptions
    - Can be instantiated and are subclasses of Exception.
================================================================================
"""

from easy_s3_multipart.exceptions import (
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
