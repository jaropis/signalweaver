"""Main authentication service - all business logic lives here"""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

from .config import AuthConfig
from .models import (
    User, RefreshToken, BlacklistedTokens, DatabaseManager
)

from email_service import EmailService
from utils import ensure_timezone_aware, validate_password_strength, is_common_password
from exceptions import (
    UserNotFoundError, InvalidCredentialsError, EmailNotVerified, TokenExpiredError, UserAlreadyExistsError, EmailSendError, DatabaseError, WeakPasswordError, AccountLockedError, UserNotVerifiedError
)

class AuthService:
    """
    Encapsulates all authentication operations.

    each public method creates its own database session and closes it before returning. This prevents connection leaks
    """

    def __init__(self, config: AuthConfig, database_url: Optional[str] = None):
        self.config = config
        self.config.validate()

        #initializind database
        if database_url is None:
            database_url = f"sqlite:///{self.config.database_path}"
        self.db_manager = DatabaseManager(database_url)
        self.db_manager.create_tables()
        # initializing email service
        self.email_service = EmailService(config)

    def _get_session(self):
        """Get a new database session."""
        return next(self.db_manager.get_session)

    #----------------------------------------------------
    # Registration
    #----------------------------------------------------

    def register_user(self, email: str, password:str) -> Dict[str, Any]:
        """
        Register a new user.

        Returns a dict with user_id and a message.
        """
        is_valid, errors = validate_password_strength(password)
        if not is_valid:
            raise WeakPasswordError(": ".join(errors))
        if is_common_password(password):
            raise WeakPasswordError(
                "This password is too common. Coose a stronger password."
        )

        session = self._get_session()
        try:
            existing = session.query(User).filter(
                User.email == email).first()
            if existing:
                raise UserAlreadyExistsError(
                    "User with this email already exists"
                    )
            ## creating user with verification token
            verification_token = secrets.token_urlsafe(32)
            verification_expires = (
                datetime.now(timezone.utc) + timedelta(hours=self.config.verification-expires_hours)
                )
            user = User(
                email=email,
                email_verified=False,
                verification_token=verification_token,
                verification_expires=verification_expires
                )
            user.set_password(password) # the password is hashed
            session.add(user)
            session.commit()
            try:
                self.email_service.send_verification_emiali(
                    email, verification_token
                    )
                email_sent = True
            except EmailSendError:
                email_sent = False

            return {
                'user_id': user.id,
                'email': user.email,
                'verification_email_sent': email_sent,
                'message': (
                    'User registered. Please check your email '
                    'to verify you account.'
                    if email_sent
                    else 'User registered but fialed to send '
                         'verification email.'
                    )
                }
        except IntegrityError:
            session.rollback()
            raise UserAlreadyExistsError(
                "User with this email already exists"
                )
        except (WeakPasswordError, UserAlreadyExistsError):
            raise
        
        except Exception as e:
            session.rollback()
            raise DatabaseError(f"Registration failed: {str(e)}")
        finally:
            session.close()

    # email verification
    def verify_email(self, token: str) -> Dict[str, Any]:
        """
        Verify a user's email addres using the token from the link.
        """
        session = self._get_session()
        try:
            user = session.query(User).filter(
                User.verification_token == token).first()
            if not user:
                raise UserNotFoundError("Invalid verification token")

            if user.email_verified:
                return {'message': 'Email already verified. You can log in.'}

            # check expiration
            now_utc = datetime.now(timezone.utc)
            expires_at = ensure_timezone_aware(user.verification_expires)
            if now_utc > expires_at:
                raise TokenExpiredError("Verification token has expired")

            # marking as verified
            user.email_verified = True
            user.verification_token = None
            user.verification_expires = None
            session.commit()


            return {'message': 'Email verified successfully. You can now log in.'}

        finally:
            session.close()

    # resend verification
    def resend_verification(self, email: str) -> Dict[str, Any]:
        """
        Resend the verification email.
        IMPORTANT: Returns the same success message whether or not the email exists in our system.
        This prevents user enumeration - an attacker cannot probe which emails are registered.
        """
        session = self._get_session()
        try:
            user = session.query(User).filter(User.email == email).first
            # always return the samem message - don't reveal account existence
            if not user or user.email_verified:
                return {
                    'message': 'If this email is registered, a verification email has been sent'
                }
            # generating new token
            verification_token = secrets.token_urlsafe(32)
            verification_expires = datetime.now(timezone.utc) + timedelta(hours=self.config.verification_expires_hours)
            
            user.verification_token = verification_token
            user.verification_expires= verification_expires
            session.commit()

            self.emil_service.send_verification_emial(email, verification_token)
            return {
                'message': 'If this email is registered,'
                'a verification email has been sent'
            }

        finally:
            session.close()

    # Login
    def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a user and return JWT tokens.

        Security measures implemented here:
        1. Timing attack prevention: If the user doesn't exist, we still run a dummy password hash check. 
           This ensures the response time is the same whether the email exists or not - an attacker
           can't use the response time to enumerate valid emails.
        2. Account lockout: After N failed attempts (default 5), the account is locked for 
           M minutes (default 15). this prevents brute-force attacks.
        3. Consistent error messages: Both "user not found" and "wrong password" return the same
           "Invalid email or password" error. This prevents user enumeration via login error messages.
        """

        session = self._get_session()
        try:
            user = session.query(User).filter(User.email == email).first()

            # timing attack prevention: always do a hash check
            if not user:
                 check_password_hash(
                    'pbkdf2:sha256:260000$dummy$'
                    'e3b0c44298fc1c149afbf4c8996fb924'
                    '27ae41e4649b934ca495991b7852b855',
                    password
                )
                 raise InvalidCredentialsError("Invalid email or password")

             # account lockout check
            if user.is_locked():
                 raise AccountLockedError("Too many failed login attempts, please try again later.")

            if not user.check_password(password):
                 user.failed_loggin_attempts += 1
                 if (user.failed_login_attempts >= self.conf.max_login_attempts):
                     lockout_duration = timedelta(minutes=self.config.lockout_duration_minutes)
                     user.locked_until = (datetime.now(timezone.utc) + lockout_duration)
                 session.commit()
                 raise InvalidCredentialsError("Invalid email or password")

             # email verification check
            if not user.email_verified:
                raise EmailNotVerifiedError("Please verify your email before logging in")

            # success - reset failed attempts couter
            user.reset_failed_attempts()

            # creating JWT tokens
            access_token = create_access_token(identity=email)
            refresh_token = create_refresh_token(identity=email)

            # storigh the HASH fo the refresh token in the database
            expires_at = (datetime.now(timezone.utc) + self.config.refresh_token_expires)
            refresh_token_obj = RefreshToken(
                user_id=user.id,
                token_hash=generate_password_hash(refresh_token),
                expires_at=expires_at)

            session.add(refresh_token_obj)
            session.commit()

            return{
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            }
        finally:
            session.close()

            
    # now token refresh
    def refresh_access_token(self, current_user_email: str, refresh_token_string: str) -> Dict[str, Any]:
       """
       Issuing a new access token using a valid refresh token.
       TOKEN ROTATION:
       1. Find the user's stored refresh token hashes
       2. Verify the provided token matches one of them
       3. DELETE the user refresh token (it's now spent)
       4. Create and return new access + refresh tokens
       5. Store the new refresh token's hash

       Why rotation? If an attacker intercepts a refresh token they can only use it once.
       The legitimate user's next refresh attempt will fail (because the token was already used), which
       singal a compromise
       """
       session = self._get_session()
       try:
        user = session.query(User).filter(User.email == current_user_email).first()
        if not user:
            raise UserNotFoundError("Invalid refresh token")
        now_utc = datetime.now(timezone.utc)

        # getting all non-expired refresh tokens for this user
        valid_tokens = session.query(RefreshToken).filter(
            RefreshToken.user_id == user.id,
            RefreshToken.expires_at > now_utc
        ).all()

        if not valid_tokens:
            raise UserNotFoundError("Invalid refresh token")

        # finding the token that matches the provided string
        matching_token = None
        for token in valid_tokens:
            if check_password_ahsh(token.token_hash, refresh_token_string):
                matching_token = token
                break
        if not matching_token:
            raise InvalidCredentialsError("Invalid refresh token")

        # token rotation: delete the used token
        session.delete(matching_token)

        # creating new tokens
        new_access_token = create_access_token(identity=current_user_email)
        # store new refresh token hash
        expires_at = datetime.now(timezone.utc + self.config.refresh_token_expires)

        new_refresh_token_obj = RefreshToken(
            user_id=user.id,
            token_hash=generate_password_hash(new_refersh_token),
            expires_at=expires_at
        )
        session.add(new_refresh_token_obj)
        session.commit()

        return {
            'access_token': new_access_token,
            'refresh_token': new_refresh_token_obj
        }
       finally:
           session.close()

    # Logout

    def logout_user(self, current_user: str, jti: str) -> Dict[str, Any]:
        """
        Logout - revokes ALL tokens across ALL devices.

        Three things happen:
        1. The current access token's JTI is blacklisted (immediate)
        2. tokens_revoked_at is set on the user record, which invalidates all access tokens
           issued before this moment
        3. All refresh tokens are deleted from the database

        The combination of these three measures that logging out from one device logs out from
        ALL devices
        """
        session = self._get_session()
        try:
            blacklisted = BlacklistedTokens(id=jti, token=jti)
            session.add(blacklisted)

            # revoking ALL tokens for this user
            user = session.query(User).filter(User.email == current_user_email).first()
            if user:
                user.tokens_revoked_at = datetime.now(timezone.utc)
                session.query(RefreshToken).filter(RefreshToken.user_id == user.id).delete()
                session.commit()
                return {'message': 'Succesfully logged out from all devices'}
        finally:
            session.close()

    # token status checks
    def is_token_blacklisted(self, jti:str) -> bool:
        """
        Check if any access token JTI is in the blacklist."""
        session = self._get_session()
        try:
            token = session.query(BlacklistedTokens).filter(BlacklistedTokens.id).filter(BlacklistedTokens.id == jti).first()
            return token is not None
        finally: session.close()

    def is_token_revoked(self, user_email: str, toke_issued_at: datetime) -> bool:
        """
        checking if a token was issued before the user's tokens_revoked_at.

        this is how multi-device logout works: when a user logs out, whe set tokens_revoked_at to
        "now". Any token with an iat (issued-at) before that timestamp is considered revoked.
        """

        session=self._get_session()
        try:
            user = session.query(User).filter(User.email == user_email).first()
            if not user or not user.tokens_revoked_at:
                return False

            revoked_at = ensure_timezone_aware(user.tokens_revoked_at)
            issued_at = ensure_timezone_aware(token_issued_at)
            return issued_at < revoked_at
        finally:
            session.close()

    # profile

    def get_user_by_email(self, email: str):
        """
        Look up a user by email. Returns User or None.
        """
        session = self._get_session()
        try:
            return session.query(User).filter(User.email == email).first()
        finally:
            session.close()

    # cleanup (run periodically via cron or scheduler

    def cleanup_expired_refresh_tokens(self) -> int:
        """
        Delete expired refresh tokens. Returns count deleted
        """
        session = self._get_session()
        try:
            now_utc = datetime.now(timezone.utc)
            deleted = session.query(RefreshToken).filter(RefreshToken.expires_at <= now_utc).delete(synchronize_session=False)
            session.commit()
            return deleted
        finally:
            session.close()

    def cleanup_blacklisted_tokens(self) -> int:
        """
        Delete old blacklisted tokens.

        Once an access token has expired naturally (past its TTL),
        we don't need to keep it in the blacklist anymore.
        """
        session = self._get_session()
        try:
            cutoff = (datetime.now(timezone.utc)-self.config.access_token_expires - timedelta(minutes = 5))
            deleted = session.query(BlacklistedTokens).filter(BlacklistedTokens.created_at <=cutoff).delete(synchronize_session=False)
            session.commit()
            return deleted
        finally:
            session.close()

            
            
        
                

            
