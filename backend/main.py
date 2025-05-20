from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import json
from datetime import datetime, timedelta

from database import get_db, engine
import models
import schemas
from auth import create_access_token, get_current_user, get_password_hash, verify_password
from storage import MinioClient
from elasticsearch_client import ElasticsearchClient
from isap_client import ISAPClient
from saos_client import SAOSClient
from rag_engine import RAGEngine

# Tworzenie tabel w bazie danych
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Asystent Prawny")

# Konfiguracja CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # W produkcji należy ograniczyć do konkretnych domen
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicjalizacja klientów
minio_client = MinioClient(
    endpoint=os.getenv("MINIO_ENDPOINT", "minio:9000"),
    access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
    secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
)

elastic_client = ElasticsearchClient(
    url=os.getenv("ELASTIC_URL", "http://elasticsearch:9200")
)

isap_client = ISAPClient()
saos_client = SAOSClient()
rag_engine = RAGEngine(elastic_client)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.on_event("startup")
async def startup_event():
    """Inicjalizacja usług przy starcie aplikacji"""
    # Sprawdzenie połączenia z MinIO
    minio_client.check_connection()
    
    # Sprawdzenie połączenia z Elasticsearch
    elastic_client.check_connection()


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Endpoint do logowania i uzyskania tokenu JWT"""
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Niepoprawny email lub hasło",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/users/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Rejestracja nowego użytkownika"""
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email już zarejestrowany")
    
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password, full_name=user.full_name)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Utworzenie katalogu w MinIO dla nowego użytkownika
    minio_client.create_user_bucket(str(db_user.id))
    
    return db_user


@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    """Pobranie informacji o zalogowanym użytkowniku"""
    return current_user


@app.post("/cases/", response_model=schemas.Case)
async def create_case(
    title: str = Form(...),
    description: str = Form(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Tworzenie nowej sprawy"""
    db_case = models.Case(
        title=title,
        description=description,
        user_id=current_user.id
    )
    
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    
    # Tworzenie ścieżki dla plików tej sprawy w MinIO
    case_path = f"{current_user.id}/{db_case.id}"
    minio_client.create_case_directory(case_path)
    
    # Inicjalizacja indeksu w Elasticsearch dla tej sprawy
    elastic_client.create_case_index(f"case-{db_case.id}")
    
    return db_case


@app.get("/cases/", response_model=List[schemas.Case])
async def list_cases(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista spraw użytkownika"""
    cases = db.query(models.Case).filter(models.Case.user_id == current_user.id).all()
    return cases


@app.get("/cases/{case_id}", response_model=schemas.CaseDetail)
async def get_case(
    case_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Szczegóły sprawy wraz z dokumentami"""
    case = db.query(models.Case).filter(
        models.Case.id == case_id,
        models.Case.user_id == current_user.id
    ).first()
    
    if not case:
        raise HTTPException(status_code=404, detail="Sprawa nie znaleziona")
    
    # Pobieranie dokumentów
    documents = db.query(models.Document).filter(models.Document.case_id == case_id).all()
    
    # Pobieranie aktów prawnych
    legal_acts = db.query(models.LegalAct).filter(models.LegalAct.case_id == case_id).all()
    
    # Pobieranie orzeczeń
    judgments = db.query(models.Judgment).filter(models.Judgment.case_id == case_id).all()
    
    return {
        "id": case.id,
        "title": case.title,
        "description": case.description,
        "created_at": case.created_at,
        "documents": documents,
        "legal_acts": legal_acts,
        "judgments": judgments
    }


@app.post("/cases/{case_id}/documents/", response_model=schemas.Document)
async def upload_document(
    case_id: int,
    file: UploadFile = File(...),
    document_type: str = Form(...),
    description: str = Form(None),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dodawanie dokumentu do sprawy"""
    # Sprawdzenie czy sprawa istnieje i należy do tego użytkownika
    case = db.query(models.Case).filter(
        models.Case.id == case_id,
        models.Case.user_id == current_user.id
    ).first()
    
    if not case:
        raise HTTPException(status_code=404, detail="Sprawa nie znaleziona")
    
    # Przygotowanie ścieżki do zapisu pliku
    file_path = f"{current_user.id}/{case_id}/{file.filename}"
    
    # Zapis pliku w MinIO
    content = await file.read()
    minio_client.upload_file(file_path, content)
    
    # Zapis rekordu w bazie danych
    db_document = models.Document(
        filename=file.filename,
        file_path=file_path,
        document_type=document_type,
        description=description,
        case_id=case_id
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    # Indeksowanie zawartości dokumentu w Elasticsearch
    # W rzeczywistości tutaj należałoby dodać parsowanie dokumentu i ekstrakcję tekstu
    document_text = "Przykładowa treść dokumentu"  # Tu powinna być prawdziwa treść dokumentu
    elastic_client.index_document(
        index_name=f"case-{case_id}",
        document_id=str(db_document.id),
        document={
            "content": document_text,
            "filename": file.filename,
            "document_type": document_type,
            "description": description,
            "timestamp": datetime.now().isoformat()
        }
    )
    
    return db_document


@app.post("/cases/{case_id}/fetch-legal-acts/", response_model=List[schemas.LegalAct])
async def fetch_legal_acts(
    case_id: int,
    keywords: List[str] = Form(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Pobieranie aktów prawnych z ISAP na podstawie słów kluczowych"""
    # Sprawdzenie czy sprawa istnieje i należy do tego użytkownika
    case = db.query(models.Case).filter(
        models.Case.id == case_id,
        models.Case.user_id == current_user.id
    ).first()
    
    if not case:
        raise HTTPException(status_code=404, detail="Sprawa nie znaleziona")
    
    # Wyszukiwanie aktów prawnych w ISAP
    legal_acts = isap_client.search_acts(keywords)
    
    # Zapisywanie wyników w bazie danych
    db_legal_acts = []
    for act in legal_acts:
        db_legal_act = models.LegalAct(
            title=act["title"],
            isap_id=act["isap_id"],
            publication=act["publication"],
            year=act["year"],
            content=act["content"],
            case_id=case_id
        )
        
        db.add(db_legal_act)
        db_legal_acts.append(db_legal_act)
    
    db.commit()
    
    # Indeksowanie aktów prawnych w Elasticsearch
    for act in db_legal_acts:
        elastic_client.index_document(
            index_name=f"case-{case_id}",
            document_id=f"legal-act-{act.id}",
            document={
                "content": act.content,
                "title": act.title,
                "publication": act.publication,
                "year": act.year,
                "type": "legal_act",
                "timestamp": datetime.now().isoformat()
            }
        )
    
    # Odświeżenie obiektów po commicie
    for act in db_legal_acts:
        db.refresh(act)
    
    return db_legal_acts


@app.post("/cases/{case_id}/fetch-judgments/", response_model=List[schemas.Judgment])
async def fetch_judgments(
    case_id: int,
    keywords: List[str] = Form(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Pobieranie orzeczeń z SAOS na podstawie słów kluczowych"""
    # Sprawdzenie czy sprawa istnieje i należy do tego użytkownika
    case = db.query(models.Case).filter(
        models.Case.id == case_id,
        models.Case.user_id == current_user.id
    ).first()
    
    if not case:
        raise HTTPException(status_code=404, detail="Sprawa nie znaleziona")
    
    # Wyszukiwanie orzeczeń w SAOS
    judgments = saos_client.search_judgments(keywords)
    
    # Zapisywanie wyników w bazie danych
    db_judgments = []
    for judgment in judgments:
        db_judgment = models.Judgment(
            court_name=judgment["court_name"],
            case_number=judgment["case_number"],
            judgment_date=judgment["judgment_date"],
            content=judgment["content"],
            saos_id=judgment["saos_id"],
            case_id=case_id
        )
        
        db.add(db_judgment)
        db_judgments.append(db_judgment)
    
    db.commit()
    
    # Indeksowanie orzeczeń w Elasticsearch
    for judgment in db_judgments:
        elastic_client.index_document(
            index_name=f"case-{case_id}",
            document_id=f"judgment-{judgment.id}",
            document={
                "content": judgment.content,
                "court_name": judgment.court_name,
                "case_number": judgment.case_number,
                "judgment_date": judgment.judgment_date,
                "type": "judgment",
                "timestamp": datetime.now().isoformat()
            }
        )
    
    # Odświeżenie obiektów po commicie
    for judgment in db_judgments:
        db.refresh(judgment)
    
    return db_judgments


@app.post("/cases/{case_id}/ask/", response_model=schemas.QuestionResponse)
async def ask_question(
    case_id: int,
    question: str = Form(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Zadawanie pytania do sprawy"""
    # Sprawdzenie czy sprawa istnieje i należy do tego użytkownika
    case = db.query(models.Case).filter(
        models.Case.id == case_id,
        models.Case.user_id == current_user.id
    ).first()
    
    if not case:
        raise HTTPException(status_code=404, detail="Sprawa nie znaleziona")
    
    # Wyszukiwanie relewantnych dokumentów w Elasticsearch
    search_results = elastic_client.search(
        index_name=f"case-{case_id}",
        query=question
    )
    
    # Użycie RAG do generowania odpowiedzi
    answer, sources = rag_engine.generate_answer(question, search_results)
    
    # Zapisanie pytania i odpowiedzi w historii
    db_question = models.Question(
        text=question,
        answer=answer,
        sources=json.dumps(sources),
        case_id=case_id
    )
    
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    
    return {
        "id": db_question.id,
        "question": question,
        "answer": answer,
        "sources": sources,
        "created_at": db_question.created_at
    }


@app.get("/cases/{case_id}/questions/", response_model=List[schemas.Question])
async def list_questions(
    case_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista pytań zadanych do sprawy"""
    # Sprawdzenie czy sprawa istnieje i należy do tego użytkownika
    case = db.query(models.Case).filter(
        models.Case.id == case_id,
        models.Case.user_id == current_user.id
    ).first()
    
    if not case:
        raise HTTPException(status_code=404, detail="Sprawa nie znaleziona")
    
    questions = db.query(models.Question).filter(models.Question.case_id == case_id).all()
    
    return questions


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
