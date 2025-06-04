import re

import email_validator


def validate_password_strength(password: str) -> str:
    """
    Validates that a password meets minimum strength requirements.
    
    Checks that the password is at least 8 characters long and contains at least one uppercase letter, one lowercase letter, one digit, and one special character from the set: @, $, !, %, *, ?, #, &. Raises a ValueError with a descriptive message if any requirement is not met.
    
    Args:
        password: The password string to validate.
    
    Returns:
        The original password string if all strength requirements are satisfied.
    
    Raises:
        ValueError: If the password does not meet any of the required criteria.
    """
    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters.")
    if not re.search(r'[A-Z]', password):
        raise ValueError("Password must contain at least one uppercase letter.")
    if not re.search(r'[a-z]', password):
        raise ValueError("Password must contain at least one lower letter.")
    if not re.search(r'\d', password):
        raise ValueError("Password must contain at least one digit.")
    if not re.search(r'[@$!%*?&#]', password):
        raise ValueError("Password must contain at least one special character: @, $, !, %, *, ?, #, &.")
    return password


def validate_email(user_email: str) -> str:
    """
    Validates and normalizes an email address.
    
    Attempts to validate the provided email address without checking deliverability. Raises a ValueError if the email is invalid.
    
    Args:
        user_email: The email address to validate.
    
    Returns:
        The normalized, validated email address.
    
    Raises:
        ValueError: If the email address is not valid.
    """
    try:
        email_info = email_validator.validate_email(user_email, check_deliverability=False)
        email = email_info.normalized
    except email_validator.EmailNotValidError as error:
        raise ValueError(str(error))
    else:
        return email
