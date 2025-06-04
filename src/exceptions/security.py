class BaseSecurityError(Exception):
    """Base class for all security-related errors."""

    def __init__(self, message=None):
        """
        Initializes the BaseSecurityError with an optional custom message.
        
        If no message is provided, a default message indicating a security error is used.
        """
        if message is None:
            message = "A security error occurred."
        super().__init__(message)


class TokenExpiredError(BaseSecurityError):
    """Raised when a token has expired."""

    def __init__(self, message="Token has expired."):
        """
        Initializes a TokenExpiredError with an optional custom error message.
        
        Args:
            message: Custom error message describing the token expiration.
        """
        super().__init__(message)


class InvalidTokenError(BaseSecurityError):
    """Raised when a token is invalid."""

    def __init__(self, message="Invalid token."):
        """
        Initializes an InvalidTokenError with an optional custom message.
        
        Args:
            message: The error message to associate with the exception. Defaults to "Invalid token.".
        """
        super().__init__(message)
