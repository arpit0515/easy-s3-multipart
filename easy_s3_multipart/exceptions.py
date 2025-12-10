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

