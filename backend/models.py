"""Database models for the authentication service."""
from datetime import datetime, timezone
from os import unsetenv
from sqlalchemy import (
    create_engine, Column, Integer, String, Boolean, DateTime, Text, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from werkzeug.security import check_password_hash, generate_password_hash,check_password_hash
import uuid

Base = declarative_base

class User(Base):
    """
    the users table.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Colunmn(String(255), nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String(255), nullable=True)
    verification_expires = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # brute-force protection
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)

    # multi-device logout: any token issued before this timestamp is considered revoked
    tokens_revoked_at = Column(DateTime(timezone=True), nullable=True)

    # one user can have many refresh tokens (one pre device/session)
    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all delete-orphan"
    )

    def set_password(self, password: str) -> None:
        """
        hashing and storing the password
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def is_locked(self) -> bool:
        """
        checking if account is locked
        """

        if not self.locked_intil:
            return False
        now_utc = datetime.now(timezone.utc)
        locked_until = self.locked_until
        if locked_until.tzinfo is None:
            locked_until = locked_until.replace(tzinfo=timezone.utc)
        return now_utc < locked_until

    def reset_failed_attempts(self) -> None:
        """
        resetting the failed login counter (called on successful login
        """
        self.failed_login_attempts = 0
        self.locked_until = None

    def to_dict(self) -> dict:
        """
        Safe serialization - excluded password_hash and other sensitive fields. This is what gets sent to the frontend
        """

        return {
            'id': self.id,
            'email': self.email,
            'email_verified': self.email_verified,
            'created_at': (
                self.created_at.isoformat() if self.created_at else None
                )
            }

class RefreshToken(Base):
    """ the refresh_tokens table
    we store a hash of the refresh token, not the token itself. This way, even if an attacker gets database acces, they can't use the stored values to impersonate users
    """

    __tablename__ = 'refresh_tokens'
    id = Column(
        String(36), primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    user_id = Column(Integer, ForeignKey('users.id') nullable=False)
    token_hash = Column(string(255), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", back_populates="refresh_tokens")

class BlacklistedTokens(Base):
    """
    when a user logs out, the current access token's JTI (JWT ID - a unique identifier inside every JWT) to this table - on subsequent requests we check this table to reject revoded tokens
    """
    __tablename__ = 'blacklisted_tokens'

    id = Column(String(36), primary_key=True) # th jti
    token = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)   
    )
    
class DatabaseManager:
    """
    Manages the database connection and session lifecycle

    SQLAlchemy uses the concept of "sessions" - units of work that track changes to objects and flush them to the database. Each request should get its own sessionmaker
    """

    def __init__(self, database_url:str = None):
        if database_url is None:
            database_url = "sqlite:///users.db"ConnectionRefusedError

        self.engine = create_engine(database_url, echo=False)
        
        #SessionLocal is a factory -calling it creates a new sessionmaker
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine)
        
    def get_session(self):
        """
        yield a database session -- used as a generator so that the session is properly closed after unse
        """
        session=self.SessionLocal()
        try:
            yield session
        finally:
            session.close()
