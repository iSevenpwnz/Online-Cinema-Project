import secrets


def generate_secure_token(length: int = 32) -> str:
    """
    Generates a secure, URL-safe random token string.
    
    Args:
        length: Number of bytes to use for token generation. Defaults to 32.
    
    Returns:
        A securely generated, URL-safe token string.
    """
    return secrets.token_urlsafe(length)
