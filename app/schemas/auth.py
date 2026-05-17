from datetime import datetime

from pydantic import BaseModel, EmailStr


class RegisterBody(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginBody(BaseModel):
    email: EmailStr
    password: str


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
