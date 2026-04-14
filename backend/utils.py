"""Utility functions for the auth service."""

from datetime import datetime, timezone
from typing import List, Optional
import re

def ensure_timezone_aware(dt: datetime) -> datetime:
    """
    Ensure a datetime object is timezone-aware.

    SQLite stores datetimes without timezone info. When we compare them with timezone-aware datetime.now(timezone.utc), Python raises an error. This function adds UTC timezone to naive datetimes.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

def validate_password_strength(password: str, min_length: int = 8) -> tuple[bool, Optional[List[str]]]:
    """
    validate password against strength requirements.
    
    Returns (True, None) if valid or (False, [list of errors]) if not.

    Requirements:
    - At least `min_length` characters (default 8)
    - At least one uppercase letter (A-Z)
    - At least one lowercase letter (a-z)
    - At least one digit (0-9)
    - At least one special character
    """
    errors = []

    if len(password) < min_length:
        errors.append(f"(Password must be at least {min_length} characters long")

    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")

    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")

    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append(
            'password must contain at least one special character'
            '([!@#$%^&*(),.?":{}|<>])'
            )
    if errors:
        return False, errors
    return True, None

# Common weak passwords — reject these regardless of complexity rules
COMMON_PASSWORDS = {
    'password', '123456', '12345678', 'qwerty', 'abc123', 'monkey',
    '1234567', 'letmein', 'trustno1', 'dragon', 'baseball', 'iloveyou',
    'master', 'sunshine', 'ashley', 'bailey', 'passw0rd', 'shadow',
    '123123', '654321', 'superman', 'qazwsx', 'michael', 'football',
    'password1', 'password123', 'admin', 'welcome', 'login', 'starwars',
    'hello', 'freedom', 'whatever', 'test', 'test123', '12345', '1234',
    'password1234', 'changeme', 'password12'
}

def is_common_password(password: str) -> bool:
    """Check if a password is on the common/weak password list."""
    return password.lower() in COMMON_PASSWORDS


