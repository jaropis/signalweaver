"""Flask blueprint for authentication endpoints."""
from flask import Blueprint, request, jsonify
from backend.auth.exceptions import AccountLockedError, DatabaseError, EmailSendError, UserAlreadyExistsError, WeakPasswordError
from flask_jwt_extend import jwt_required, get_jwt_identity, get_jwt

from auth import AuthService
from exceptionsEmailNotVerifiedError,  importInvalidCredentialsError,  (
    UserNotFoundError, InvalidCredentialsError, EmailNotVerifiedError,
    TokenExpiredError, UserAlreadyExistsError, EmailSendError,
    AccountLockedError, WeakPasswordError, DatabaseError
)

def create_auth_blueprint(auth_service: AuthService, name: str = 'auth', limiter=None) -> Blueprint:
    """
    Factory function that creates a Flask blueprint with auth endpoints.

    Why a factory? Because it receives the AuthServiceInstance as a parameter, which means we can confugure different services for different environments (test vs. production) and use dependency injection.

    Args:
       auth_service: The AuthService instance to handle business logic
       name: Blueprint name (also used as URL prefix)
       limiter: Optional Flask-limiter for rate limiting
    """

    bp = Blueprint(name, __name__)
    # Helper to conditionally apply rate limiting
    def apply_limit(limit_string):
        def decorator(f):
            if limiter:
                return limiter.limit(limit_string)(f)
            return f
        return decorator
    # POST /auth/register 
    @bp.route('/register', methods=['POST'])
    @apply_limit("3 per minute")
    def register():
        """
        Register a new user account
        Request body: {"email": "...", "password": "..."}

        Responses:
        - 201: User created, verification email sent
        - 202: User created, but email sending failed
        - 400: Missing fields or weak password
        - 409: Email already registered
