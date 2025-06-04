from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    bcrypt__rounds=14,
    deprecated="auto"
)


def hash_password(password: str) -> str:
    """
    Hashes a plain-text password using bcrypt.
    
    Uses the configured password context to generate a bcrypt hash of the provided password.
    Returns the hashed password as a string.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Checks whether a plain-text password matches a given hashed password.
    
    Args:
        plain_password: The plain-text password to verify.
        hashed_password: The bcrypt-hashed password to compare against.
    
    Returns:
        True if the plain-text password matches the hashed password, otherwise False.
    """
    return pwd_context.verify(plain_password, hashed_password)
