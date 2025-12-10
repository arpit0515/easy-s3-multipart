"""
================================================================================
Package:        easy_s3_multipart
Module:         exceptions.py
Description:    Exception classes

Author:         Arpit
Version:        0.1.0
Git Repo:       https://github.com/arpit0515/easy-s3-multipart
Created On:     12/10/2025 (MM/DD/YYYY)
Last Updated:   12/10/2025 (MM/DD/YYYY)

Notes:
    - Setting up the exceptions for classes
================================================================================

"""

class S3HandlerError(Exception):
    """Base exception for S3 handler errors"""
    pass


class S3InitiationError(S3HandlerError):
    """Raised when multipart upload initiation fails"""
    pass


class S3UploadError(S3HandlerError):
    """Raised when file upload fails"""
    pass


class S3ValidationError(S3HandlerError):
    """Raised when validation fails"""
    pass


class S3DeleteError(S3HandlerError):
    """Raised when file deletion fails"""
    pass

