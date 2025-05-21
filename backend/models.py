from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

# Tabela asocjacyjna dla relacji wiele-do-wielu między sprawami a aktami prawnymi
case_legal_act = Table(
    "case_legal_act",
    Base.metadata,
    Column("case_id", Integer, ForeignKey("cases.id")),
    Column("legal_act_id", Integer, ForeignKey("legal_acts.id"))
)

# Tabela asocjacyjna dla relacji wiele-do-wielu między sprawami a orzeczeniami
case_judgment = Table(
    "case_judgment",
    Base.metadata,
    Column("case_id", Integer, ForeignKey("cases.id")),
    Column("judgment_id", Integer, ForeignKey("judgments.id"))
)

class User(Base):
    """Model użytkownika systemu."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacje
    # cases = relationship("User", back_populates="user")

class Case(Base):
    """Model sprawy prawnej."""
    
    __tablename__ = "cases"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    case_number = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Relacje
    owner = relationship("User", back_populates="cases")
    documents = relationship("Document", back_populates="case", cascade="all, delete-orphan")
    legal_acts = relationship("LegalAct", secondary=case_legal_act, back_populates="cases")
    judgments = relationship("Judgment", secondary=case_judgment, back_populates="cases")
    questions = relationship("Question", back_populates="case", cascade="all, delete-orphan")

class Document(Base):
    """Model dokumentu sprawy."""
    
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    file_path = Column(String)
    file_type = Column(String)  # np. pdf, docx, txt
    content_text = Column(Text)  # Tekst wyekstrahowany z dokumentu
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    case_id = Column(Integer, ForeignKey("cases.id"))
    
    # Relacje
    case = relationship("Case", back_populates="documents")
    
class LegalAct(Base):
    """Model aktu prawnego."""
    
    __tablename__ = "legal_acts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    isap_id = Column(String, index=True)  # ID z ISAP
    publication_date = Column(DateTime)
    document_type = Column(String)  # np. ustawa, rozporządzenie
    content = Column(Text)
    pdf_url = Column(String)
    local_path = Column(String)  # Ścieżka do lokalnej kopii
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacje
    cases = relationship("Case", secondary=case_legal_act, back_populates="legal_acts")

class Judgment(Base):
    """Model orzeczenia sądowego."""
    
    __tablename__ = "judgments"
    
    id = Column(Integer, primary_key=True, index=True)
    saos_id = Column(Integer, index=True)  # ID z SAOS
    title = Column(String, index=True)
    case_number = Column(String, index=True)
    judgment_date = Column(DateTime)
    court_name = Column(String)
    court_type = Column(String)  # np. COMMON, SUPREME, CONSTITUTIONAL_TRIBUNAL
    judges = Column(Text)  # Lista sędziów w formie JSON
    keywords = Column(Text)  # Słowa kluczowe w formie JSON
    content = Column(Text)
    source_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacje
    cases = relationship("Case", secondary=case_judgment, back_populates="judgments")

class Question(Base):
    """Model pytania do sprawy."""
    
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text)
    answer_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    case_id = Column(Integer, ForeignKey("cases.id"))
    
    # Relacje
    case = relationship("Case", back_populates="questions")