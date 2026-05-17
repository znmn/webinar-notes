from datetime import timedelta

import bcrypt
import jwt

from app.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET,
)
from app.core.logger import get_logger
from app.core.utils.datetime import utc_now

logger = get_logger(__name__)


def make_token(token_payload: dict) -> str:
    """Generate a JWT access token with expiration claims."""
    to_encode = token_payload.copy()
    expire = utc_now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    try:
        return jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)
    except Exception as exc:
        logger.exception("Failed to generate JWT token")
        raise RuntimeError("failed to generate token") from exc


def get_password_hash(password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    try:
        return bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
    except ValueError as exc:
        logger.exception("Failed to hash password")
        raise RuntimeError("failed to hash password") from exc


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    try:
        hashed = hashed_password.encode("utf-8")
        plain = plain_password.encode("utf-8")
    except UnicodeEncodeError:
        logger.warning("Password verification failed due to encoding error")
        return False

    try:
        return bcrypt.checkpw(plain, hashed)
    except ValueError:
        logger.warning(
            "Password verification failed due to invalid hash format"
        )
        return False
