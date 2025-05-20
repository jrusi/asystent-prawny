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

# Schematy spraw
class CaseBase(BaseModel):
    title: str
    description: str


class CaseCreate(CaseBase):
    pass


class Case(CaseBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Schematy spraw
class CaseBase(BaseModel):
    title: str
    description: str


class CaseCreate(CaseBase):
    pass


class Case(CaseBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True


# Schematy dokumentów
class DocumentBase(BaseModel):
    filename: str
    document_type: str
    description: Optional[str] = None


class DocumentCreate(DocumentBase):
    pass


class Document(DocumentBase):
    id: int
    file_path: str
    case_id: int
    created_at: datetime

    class Config:
        orm_mode = True
