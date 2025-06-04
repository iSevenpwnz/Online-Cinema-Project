import secrets


def generate_secure_token(length: int = 32) -> str:
    """
    Generates a secure, URL-safe random token.
    
    Args:
        length: Number of bytes of randomness to use for the token. Defaults to 32.
    
    Returns:
        A URL-safe base64-encoded string suitable for use as a secure token.
    """
    return secrets.token_urlsafe(length)
