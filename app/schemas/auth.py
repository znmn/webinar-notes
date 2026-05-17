from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, StringConstraints

NameStr = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)
]
PasswordStr = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=8, max_length=128)
]


class RegisterBody(BaseModel):
    name: NameStr
    email: EmailStr
    password: PasswordStr


class LoginBody(BaseModel):
    email: EmailStr
    password: PasswordStr


class UserPublic(BaseModel):
    id: int
    name: str
    email: EmailStr


class RegisteredUserPublic(UserPublic):
    created_at: datetime | None


class RegisterResponse(BaseModel):
    message: str
    user: RegisteredUserPublic


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserPublic
