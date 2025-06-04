from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    bcrypt__rounds=14,
    deprecated="auto"
)


def hash_password(password: str) -> str:
    """
    Hashes a plain-text password using bcrypt.
    
    Uses the configured password context to generate a bcrypt hash with enhanced security settings.
    
    Args:
        password: The plain-text password to be hashed.
    
    Returns:
        The bcrypt hash of the provided password.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Checks whether a plain-text password matches a given hashed password.
    
    Returns:
        True if the plain-text password corresponds to the hashed password, otherwise False.
    """
    return pwd_context.verify(plain_password, hashed_password)
