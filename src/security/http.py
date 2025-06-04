from fastapi import Request, HTTPException, status


def get_token(request: Request) -> str:
    """
    Extracts the Bearer token from the Authorization header of a FastAPI request.
    
    Raises an HTTP 401 Unauthorized exception if the header is missing or not in the expected 'Bearer <token>' format.
    
    Returns:
        The extracted token string.
    """
    authorization = request.headers.get("Authorization")

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing"
        )

    scheme, _, token = authorization.partition(" ")

    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Expected 'Bearer <token>'"
        )

    return token
