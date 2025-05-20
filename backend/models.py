from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    cases = relationship("Case", back_populates="user")


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="cases")
    documents = relationship("Document", back_populates="case")
    legal_acts = relationship("LegalAct", back_populates="case")
    judgments = relationship("Judgment", back_populates="case")
    questions = relationship("Question", back_populates="case")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    file_path = Column(String)
    document_type = Column(String)  # np. "pozew", "odpowiedź na pozew", "wniosek", itp.
    description = Column(Text, nullable=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    created_at = Column(DateTime, server_default=func.now())

    case = relationship("Case", back_populates="documents")


class LegalAct(Base):
    __tablename__ = "legal_acts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    isap_id = Column(String)
    publication = Column(String)  # np. "Dz.U. 2020 poz. 1740"
    year = Column(Integer)
    content = Column(Text)
    case_id = Column(Integer, ForeignKey("cases.id"))
    created_at = Column(DateTime, server_default=func.now())

    case = relationship("Case", back_populates="legal_acts")


class Judgment(Base):
    __tablename__ = "judgments"

    id = Column(Integer, primary_key=True, index=True)
    court_name = Column(String)
    case_number = Column(String)
    judgment_date = Column(DateTime)
    content = Column(Text)
    saos_id = Column(String)
    case_id = Column(Integer, ForeignKey("cases.id"))
    created_at = Column(DateTime, server_default=func.now())

    case = relationship("Case", back_populates="judgments")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text)
    answer = Column(Text)
    sources = Column(Text)  # JSON jako tekst: lista źródeł użytych do wygenerowania odpowiedzi
    case_id = Column(Integer, ForeignKey("cases.id"))
    created_at = Column(DateTime, server_default=func.now())

    case = relationship("Case", back_populates="questions")
