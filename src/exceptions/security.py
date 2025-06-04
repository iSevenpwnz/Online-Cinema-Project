class BaseSecurityError(Exception):
    """Base class for all security-related errors."""

    def __init__(self, message=None):
        """
        Initializes a BaseSecurityError with an optional custom message.
        
        Args:
            message: An optional error message. Defaults to "A security error occurred."
        """
        if message is None:
            message = "A security error occurred."
        super().__init__(message)


class TokenExpiredError(BaseSecurityError):
    """Raised when a token has expired."""

    def __init__(self, message="Token has expired."):
        """
        Initializes a TokenExpiredError with an optional custom message.
        
        Args:
            message: The error message to associate with the exception. Defaults to "Token has expired.".
        """
        super().__init__(message)


class InvalidTokenError(BaseSecurityError):
    """Raised when a token is invalid."""

    def __init__(self, message="Invalid token."):
        """
        Initializes an InvalidTokenError with an optional custom message.
        
        Args:
            message: The error message to associate with the exception. Defaults to "Invalid token."
        """
        super().__init__(message)
