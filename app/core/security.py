from datetime import timedelta

import bcrypt
import jwt

from app.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET,
)
from app.core.utils.datetime import utc_now


def make_token(token_payload: dict) -> str:
    """Generate a JWT access token with expiration claims."""
    to_encode = token_payload.copy()
    expire = utc_now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)


def get_password_hash(password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    try:
        hashed = hashed_password.encode("utf-8")
        plain = plain_password.encode("utf-8")
    except UnicodeEncodeError:
        return False

    return bcrypt.checkpw(plain, hashed)
