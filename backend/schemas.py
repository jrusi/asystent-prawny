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
from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

# Schematy użytkownika
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

# Schematy dokumentu
class DocumentBase(BaseModel):
    title: str
    description: Optional[str] = None

class DocumentCreate(DocumentBase):
    file_type: Optional[str] = None

class DocumentResponse(DocumentBase):
    id: int
    file_path: str
    file_type: str
    created_at: datetime
    case_id: int
    
    class Config:
        orm_mode = True

class DocumentContent(BaseModel):
    content_text: str

# Schematy aktu prawnego
class LegalActBase(BaseModel):
    title: str
    isap_id: str
    publication_date: datetime
    document_type: str

class LegalActCreate(LegalActBase):
    content: Optional[str] = None
    pdf_url: Optional[str] = None

class LegalActResponse(LegalActBase):
    id: int
    content: Optional[str] = None
    pdf_url: Optional[str] = None
    local_path: Optional[str] = None
    created_at: datetime
    
    class Config:
        orm_mode = True

# Schematy orzeczenia sądowego
class JudgmentBase(BaseModel):
    saos_id: int
    title: str
    case_number: str
    judgment_date: datetime
    court_name: str
    court_type: str

class JudgmentCreate(JudgmentBase):
    judges: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    content: Optional[str] = None
    source_url: Optional[str] = None

class JudgmentResponse(JudgmentBase):
    id: int
    judges: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    content: Optional[str] = None
    source_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        orm_mode = True

# Schematy sprawy
class CaseBase(BaseModel):
    title: str
    description: Optional[str] = None
    case_number: Optional[str] = None

class CaseCreate(CaseBase):
    pass

class CaseUpdate(CaseBase):
    pass

class CaseResponse(CaseBase):
    id: int
    created_at: datetime
    updated_at: datetime
    owner_id: int
    documents: List[DocumentResponse] = []
    legal_acts: List[LegalActResponse] = []
    judgments: List[JudgmentResponse] = []
    
    class Config:
        orm_mode = True

# Schematy pytania i odpowiedzi
class QuestionCreate(BaseModel):
    question_text: str
    case_id: int

class QuestionResponse(BaseModel):
    id: int
    question_text: str
    answer_text: Optional[str] = None
    created_at: datetime
    case_id: int
    
    class Config:
        orm_mode = True

class AnswerCreate(BaseModel):
    answer_text: str

# Schematy do wyszukiwania
class SearchActsRequest(BaseModel):
    query: str
    year: Optional[int] = None
    document_type: Optional[str] = None
    max_results: int = 20

class SearchJudgmentsRequest(BaseModel):
    query: Optional[str] = None
    case_number: Optional[str] = None
    judge_name: Optional[str] = None
    court_type: Optional[str] = None
    from_date: Optional[str] = None
    to_date: Optional[str] = None
    keywords: Optional[List[str]] = None
    legal_bases: Optional[List[str]] = None
    page_size: int = 20
    page_number: int = 0

# Schematy do obsługi autentykacji
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None

# Schematy do obsługi błędów
class ErrorResponse(BaseModel):
    detail: str

# Schematy do obsługi źródeł i wyników wyszukiwania
class SearchResult(BaseModel):
    id: str
    title: str
    url: Optional[str] = None
    description: Optional[str] = None
    type: str  # "legal_act", "judgment", "document"
    
class SourceInfo(BaseModel):
    content: str
    title: str
    type: str
    source: str

class QueryResponse(BaseModel):
    answer: str
    sources: Optional[List[SourceInfo]] = None

# Schemat do obsługi uploadu plików
class FileUploadResponse(BaseModel):
    filename: str
    file_path: str
    file_type: str
    file_size: int
    
# Schemat do analizy dokumentów
class DocumentAnalysisResult(BaseModel):
    keywords: List[str]
    legal_bases: List[str]
    suggested_acts: List[Dict[str, Any]]
    suggested_judgments: List[Dict[str, Any]]