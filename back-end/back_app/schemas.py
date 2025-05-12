# schemas.py
from pydantic import BaseModel, ConfigDict, EmailStr  # type: ignore
from typing import Optional
from datetime import date


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: list[UserPublic]


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class UserOut(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[date] = None

    class Config:
        from_attributes = True


class FilterPage(BaseModel):
    offset: int = 0
    limit: int = 100
