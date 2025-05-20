from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
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


# Schematy aktów prawnych
class LegalActBase(BaseModel):
    title: str
    isap_id: str
    publication: str
    year: int
    content: str


class LegalActCreate(LegalActBase):
    pass


class LegalAct(LegalActBase):
    id: int
    case_id: int
    created_at: datetime

    class Config:
        orm_mode = True


# Schematy orzeczeń
class JudgmentBase(BaseModel):
    court_name: str
    case_number: str
    judgment_date: datetime
    content: str
    saos_id: str


class JudgmentCreate(JudgmentBase):
    pass


class Judgment(JudgmentBase):
    id: int
    case_id: int
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


class CaseDetail(Case):
    documents: List[Document] = []
    legal_acts: List[LegalAct] = []
    judgments: List[Judgment] = []


# Schematy pytań
class QuestionBase(BaseModel):
    text: str


class QuestionCreate(QuestionBase):
    pass


class Question(QuestionBase):
    id: int
    answer: str
    sources: str  # JSON jako tekst
    case_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class QuestionResponse(BaseModel):
    id: int
    question: str
    answer: str
    sources: List[Dict[str, Any]]
    created_at: datetime


# Schemat tokenu uwierzytelniającego
class Token(BaseModel):
    access_token: str
    token_type: str
