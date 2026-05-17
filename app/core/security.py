from datetime import timedelta

import jwt

from app.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET,
)
from app.core.utils.datetime import utc_now


def make_token(data: dict) -> str:
    to_encode = data.copy()
    expire = utc_now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)
