from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from enum import Enum


class Role(str, Enum):
    admin = "admin"
    user = "user"


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserInDB(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    email: EmailStr
    hashed_password: str
    role: Role = Role.user


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: Optional[Role] = None
