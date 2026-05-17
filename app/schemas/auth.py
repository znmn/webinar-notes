from pydantic import BaseModel, EmailStr


class RegisterBody(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginBody(BaseModel):
    email: EmailStr
    password: str
