from typing import Optional
from datetime import datetime

from pydantic import EmailStr
from sqlmodel import SQLModel, Field


class UserBase(SQLModel):
    username: str = Field(index=True, unique=True, max_length=255, min_length=3)
    email: EmailStr = Field(unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_superuser: bool = Field(default=False)


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    password: str


class UserRead(UserBase):
    id: int


class UserRegister(SQLModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(SQLModel):
    username: str
    password: str


class UserCreate(UserBase):
    password: str
    access_token: str = None
