import os
from datetime import timedelta
from typing import Optional

class AuthConfig:
    """
    Values can be passed explicitly or read from envirnoment variables.
    """

    def __init__(
            self,
            jwt_secret_key: Optional[str] = None,
            access_token_expires: Optional[timedelta] = None,
            refresh_token_expires: Optional[timedelta] = None,
            mail_server: str = 'smtp.gmail.com',
            mail_port: int = 587,
            mail_use_tls: bool = True,
            mail_username: Optional[str] = None,
            mail_password: Optional[str] = None,
            frontend_url: str= 'http://localhost:5173',
            database_path: Optional[str] = None,
            verification_expires_hours: int = 48,
            max_login_attempts: int = 5,
            lockout_duration_minutes: int = 15,
            cors_allowed_origins: Optional[list] = None,
    ): 
        self.jwt_secret_key = jwt_secret_key or os.environ.get('JWT_SECRET_KEY')
        if not self.jwt_secret_key:
            raise ValueError("JWT_SECRET_KEY is required")
    
        # token lifetimes
        self.access_token_expires = access_token_expires or timedelta(hours=24)
        self.refresh_token_expires = refresh_token_expires or timedelta(days=30)

        # email configuration -- sending
        self.mail_server = mail_server
        self.mail_port = mail_port
        self.mail_use_tls = mail_use_tls
        self.mail_username = mail_username or os.environ.get('MAIL_USERNAME', '')
        self.mail_password = mail_password or os.environ.get('MAIL_PASSWORD', '')

        # vue app
        self.frontend_url = frontend_url or os.environ.get('FRONTEND_URL', 'http://localhost:5173')

        # sqlite
        self.database_path = database_path or os.environ.get('DATABASE_PATH', 'users.db')

        # how long verification links remain valid
        self.verification_expires_hours = verification_expires_hours

        # brute-force

        self.max_login_attempts = max_login_attempts
        self.lockout_duration_minutes = lockout_duration_minutes

        # cors
        if cors_allowed_origins is None:
            cors_env = os.environ.get('CORS_ALLOWED_ORIGINS', '')
            if cors_env:
                self.cors_allowed_origins = [
                    origin.strip() for origin in cors_env.split(',')]
            else:
                self.cors_allowed_origins = None
        else:
            self.cors_allowed_origins = cors_allowed_origins


    @classmethod
    def from_env(cls) -> 'AuthConfig':
        """Create configuration entirely from environment variables"""
        return cls()

    def validate(self) -> None:
        """raise Value error if any required settings are missing."""
        if not self.jwt_secret_key:
            raise ValueError("JWT_SECRET_KEY is required")
        if self.mail_username and not self.mail_password:
            raise ValueError("MAIL_PASSWORD is required when MAIL_USERNAME is set")
        if not self.frontend_url:
            raise ValueError("FRONTEND_URL is required")
