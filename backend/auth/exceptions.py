"""Custom exceptions for the authentication service"""

class AuthError(Exception):
    """Base Exception for all authentication errors."""
    pass

class UserNotFoundError(AuthError):
    """Raised when the email/password combination is wrong."""
    pass


class InvalidCredentialsError(AuthError):
    """Raised when the email/password combination is wrong."""
    pass

class EmailNotVerifiedError(AuthError):
    """Raised when a user tries to log in without verifying their email."""
    pass

class TokeExpiredError(AuthError):
    """Raised when a verification of reset token has expired."""
    pass

class UserAlreadyExistsError(AuthError):
    """Raised when trying to register an email that is already taken."""
    pass

class EmailSendError(AuthError):
    """Raised when the email service fails to send"""
    pass

class DatabaseError(AuthError):
    """Raised when a database operation fails unexpectedly."""
    pass

class AccountLockedError(AuthError):
    """ Raised when an account is temporarily locked."""
    pass

class WeakPasswordError(AuthError):
    """Raised when a password fails strength validation."""
    pass


class UserNotVerifiedError(AuthError):
    """Raised when a user has not verified their password."""
    pass

