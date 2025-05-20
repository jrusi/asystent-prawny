from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Schematy użytkownika
class UserBase(BaseModel):
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True


# Schema tokenu uwierzytelniającego
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
