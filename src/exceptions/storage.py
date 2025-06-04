class BaseS3Error(Exception):
    """Base class for all S3-related errors."""

    def __init__(self, message=None):
        """
        Initializes the base S3 error with an optional custom message.
        
        Args:
            message: Optional error message. Defaults to a generic S3 storage error message.
        """
        if message is None:
            message = "An S3 storage error occurred."
        super().__init__(message)


class S3ConnectionError(BaseS3Error):
    """Raised when there is an issue connecting to the S3 storage."""

    def __init__(self, message="Failed to connect to S3 storage."):
        """
        Initializes the exception for S3 connection failures with an optional custom message.
        
        Args:
            message: Custom error message describing the connection failure.
        """
        super().__init__(message)


class S3BucketNotFoundError(BaseS3Error):
    """Raised when the specified bucket does not exist."""

    def __init__(self, message="S3 bucket not found."):
        """
        Initializes the exception for a missing S3 bucket with a default error message.
        
        Args:
            message: Optional custom error message describing the missing bucket.
        """
        super().__init__(message)


class S3FileUploadError(BaseS3Error):
    """Raised when a file upload operation fails."""

    def __init__(self, message="Failed to upload file to S3."):
        """
        Initializes the exception for S3 file upload failures with an optional custom message.
        
        Args:
            message: Custom error message describing the upload failure. Defaults to "Failed to upload file to S3."
        """
        super().__init__(message)


class S3FileNotFoundError(BaseS3Error):
    """Raised when the requested file is not found in S3 storage."""

    def __init__(self, message="Requested file not found in S3."):
        """
        Initializes the exception for a missing file in S3 storage with a default message.
        
        Args:
            message: Optional custom error message describing the missing file condition.
        """
        super().__init__(message)


class S3PermissionError(BaseS3Error):
    """Raised when the client lacks permission to access a resource."""

    def __init__(self, message="Insufficient permissions to access S3 resource."):
        """
        Initializes the exception for insufficient permissions to access an S3 resource.
        
        Args:
            message: Optional custom error message describing the permission issue.
        """
        super().__init__(message)
