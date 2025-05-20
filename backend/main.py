import os
import logging
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

from . import models, schemas
from .database import get_db, engine
from .isap_client import ISAPClient
from .saos_client import SAOSClient
from .rag_engine import RAGEngine
from .storage import StorageManager

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Utworzenie tabel w bazie danych
models.Base.metadata.create_all(bind=engine)

# Inicjalizacja aplikacji
app = FastAPI(
    title="Asystent Prawny API",
    description="API do zarządzania dokumentami prawnymi, wyszukiwania aktów prawnych i orzeczeń oraz zadawania pytań",
    version="1.0.0"
)

# Konfiguracja CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Konfiguracja uwierzytelniania
SECRET_KEY = os.getenv("JWT_SECRET", "very_secret_key_change_in_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Narzędzia do hashowania haseł
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Inicjalizacja klientów
isap_client = ISAPClient()
saos_client = SAOSClient()

# Inicjalizacja silnika RAG
rag_engine = RAGEngine(
    api_key=os.getenv("OPENAI_API_KEY"),
    persist_directory="./chroma_db"
)

# Inicjalizacja menedżera przechowywania
storage_manager = StorageManager(
    minio_endpoint=os.getenv("MINIO_ENDPOINT", "minio:9000"),
    minio_access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
    minio_secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
    minio_secure=os.getenv("MINIO_SECURE", "false").lower() == "true"
)

# Funkcje pomocnicze
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Nieprawidłowe dane uwierzytelniające",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user

# Funkcja do analizy dokumentu
async def analyze_document(case_id: int, document_id: int, document_text: str, db: Session):
    try:
        # Ekstrakcja słów kluczowych
        async with ISAPClient() as isap:
            keywords = await isap.extract_keywords_from_document(document_text)
            
            # Wyszukiwanie pasujących aktów prawnych
            suggested_acts = await isap.search_acts(
                query=" ".join(keywords[:5]),
                max_results=10
            )
        
        # Wyszukiwanie podobnych orzeczeń
        async with SAOSClient() as saos:
            legal_bases = await saos.extract_legal_bases(document_text)
            
            # Wyszukiwanie orzeczeń na podstawie słów kluczowych i podstaw prawnych
            suggested_judgments = await saos.find_similar_judgments(
                case_text=document_text,
                keywords=keywords,
                max_results=10
            )
        
        # Można zapisać wyniki analizy do bazy danych lub zwrócić jako wynik
        logger.info(f"Znaleziono {len(suggested_acts)} aktów prawnych i {len(suggested_judgments)} orzeczeń dla dokumentu {document_id}")
        
        return {
            "keywords": keywords,
            "legal_bases": legal_bases,
            "suggested_acts": suggested_acts,
            "suggested_judgments": suggested_judgments
        }
    
    except Exception as e:
        logger.error(f"Błąd podczas analizy dokumentu: {e}")
        return None

# Endpointy API
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nieprawidłowy email lub hasło",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.UserResponse)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Sprawdzenie, czy użytkownik już istnieje
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email już zarejestrowany"
        )
    
    # Tworzenie nowego użytkownika
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/me", response_model=schemas.UserResponse)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# Endpointy dla spraw
@app.post("/cases/", response_model=schemas.CaseResponse)
async def create_case(
    case: schemas.CaseCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_case = models.Case(
        title=case.title,
        description=case.description,
        case_number=case.case_number,
        owner_id=current_user.id
    )
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case

@app.get("/cases/", response_model=List[schemas.CaseResponse])
async def get_cases(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cases = db.query(models.Case).filter(models.Case.owner_id == current_user.id).offset(skip).limit(limit).all()
    return cases

@app.get("/cases/{case_id}", response_model=schemas.CaseResponse)
async def get_case(
    case_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    case = db.query(models.Case).filter(models.Case.id == case_id, models.Case.owner_id == current_user.id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sprawa nie znaleziona"
        )
    return case

@app.put("/cases/{case_id}", response_model=schemas.CaseResponse)
async def update_case(
    case_id: int,
    case: schemas.CaseUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_case = db.query(models.Case).filter(models.Case.id == case_id, models.Case.owner_id == current_user.id).first()
    if not db_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sprawa nie znaleziona"
        )
    
    # Aktualizacja pól
    for key, value in case.dict(exclude_unset=True).items():
        setattr(db_case, key, value)
    
    db.commit()
    db.refresh(db_case)
    return db_case

@app.delete("/cases/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_case(
    case_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_case = db.query(models.Case).filter(models.Case.id == case_id, models.Case.owner_id == current_user.id).first()
    if not db_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sprawa nie znaleziona"
        )
    
    # Usunięcie z bazy wektorowej
    await rag_engine.clear_case_data(str(case_id))
    
    # Usunięcie plików
    for document in db_case.documents:
        await storage_manager.delete_file(document.file_path)
    
    # Usunięcie z bazy danych
    db.delete(db_case)
    db.commit()
    
    return None

# Endpointy dla dokumentów
@app.post("/cases/{case_id}/documents/", response_model=schemas.DocumentResponse)
async def create_document(
    case_id: int,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Sprawdzenie czy sprawa istnieje
    case = db.query(models.Case).filter(models.Case.id == case_id, models.Case.owner_id == current_user.id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sprawa nie znaleziona"
        )
    
    # Zapisanie pliku
    file_content = await file.read()
    file_type = file.content_type
    file_path = f"cases/{case_id}/documents/{file.filename}"
    
    # Upload pliku do MinIO
    success = await storage_manager.upload_file(file_path, file_content)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Błąd podczas zapisywania pliku"
        )
    
    # Ekstrakcja tekstu z dokumentu
    content_text = await storage_manager.extract_text(file_path, file_type)
    
    # Utworzenie dokumentu w bazie danych
    db_document = models.Document(
        title=title,
        description=description,
        file_path=file_path,
        file_type=file_type,
        content_text=content_text,
        case_id=case_id
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    # Dodanie dokumentu do bazy wektorowej
    await rag_engine.add_documents([{
        "id": str(db_document.id),
        "title": db_document.title,
        "content": content_text,
        "type": "document"
    }], str(case_id))
    
    # Analiza dokumentu i wyszukanie aktów prawnych i orzeczeń
    await analyze_document(case_id, db_document.id, content_text, db)
    
    return db_document

@app.get("/cases/{case_id}/documents/", response_model=List[schemas.DocumentResponse])
async def get_case_documents(
    case_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Sprawdzenie czy sprawa istnieje
    case = db.query(models.Case).filter(models.Case.id == case_id, models.Case.owner_id == current_user.id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sprawa nie znaleziona"
        )
    
    documents = db.query(models.Document).filter(models.Document.case_id == case_id).all()
    return documents

@app.get("/documents/{document_id}", response_model=schemas.DocumentResponse)
async def get_document(
    document_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    document = db.query(models.Document).join(models.Case).filter(
        models.Document.id == document_id,
        models.Case.owner_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dokument nie znaleziony"
        )
    
    return document

@app.get("/documents/{document_id}/content", response_model=schemas.DocumentContent)
async def get_document_content(
    document_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    document = db.query(models.Document).join(models.Case).filter(
        models.Document.id == document_id,
        models.Case.owner_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dokument nie znaleziony"
        )
    
    return {"content_text": document.content_text}

@app.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    document = db.query(models.Document).join(models.Case).filter(
        models.Document.id == document_id,
        models.Case.owner_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dokument nie znaleziony"
        )
    
    # Usuń plik z MinIO
    await storage_manager.delete_file(document.file_path)
    
    # Usunięcie z bazy wektorowej
    case_id = document.case_id
    await rag_engine.clear_case_data(str(case_id))
    
    # Usuń z bazy danych
    db.delete(document)
    db.commit()
    
    # Ponowne dodanie pozostałych dokumentów do bazy wektorowej
    remaining_docs = db.query(models.Document).filter(models.Document.case_id == case_id).all()
    for doc in remaining_docs:
        await rag_engine.add_documents([{
            "id": str(doc.id),
            "title": doc.title,
            "content": doc.content_text,
            "type": "document"
        }], str(case_id))
    
    return None

# Endpointy dla aktów prawnych
@app.post("/isap/search", response_model=List[Dict[str, Any]])
async def search_isap(
    search_request: schemas.SearchActsRequest,
    current_user: models.User = Depends(get_current_user)
):
    async with ISAPClient() as client:
        results = await client.search_acts(
            query=search_request.query,
            year=search_request.year,
            document_type=search_request.document_type,
            max_results=search_request.max_results
        )
    return results

@app.post("/cases/{case_id}/legal_acts", response_model=schemas.LegalActResponse)
async def add_legal_act(
    case_id: int,
    act: schemas.LegalActCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Sprawdzenie czy sprawa istnieje
    case = db.query(models.Case).filter(models.Case.id == case_id, models.Case.owner_id == current_user.id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sprawa nie znaleziona"
        )
    
    # Sprawdzenie czy akt prawny już istnieje w bazie
    existing_act = db.query(models.LegalAct).filter(models.LegalAct.isap_id == act.isap_id).first()
    
    if existing_act:
        # Sprawdź czy jest już powiązany ze sprawą
        if existing_act in case.legal_acts:
            return existing_act
        
        # Dodanie powiązania
        case.legal_acts.append(existing_act)
        db.commit()
        return existing_act
    
    # Pobranie szczegółów aktu prawnego z ISAP jeśli potrzebne
    if not act.content or not act.pdf_url:
        async with ISAPClient() as client:
            details = await client.get_act_details(act.isap_id)
            if details:
                act.content = details.get("text", "")
                act.pdf_url = details.get("pdf_url", "")
    
    # Pobranie PDF jeśli dostępny
    local_path = None
    if act.pdf_url:
        pdf_filename = f"{act.isap_id}.pdf"
        local_path = f"legal_acts/{pdf_filename}"
        
        async with ISAPClient() as client:
            # Tymczasowe zapisanie pliku lokalnie
            temp_path = f"/tmp/{pdf_filename}"
            success = await client.download_act_pdf(act.pdf_url, temp_path)
            
            if success:
                # Odczyt pliku i zapis do MinIO
                with open(temp_path, "rb") as f:
                    content = f.read()
                    await storage_manager.upload_file(local_path, content)
                
                # Usunięcie tymczasowego pliku
                os.remove(temp_path)
    
    # Utworzenie aktu prawnego w bazie danych
    db_legal_act = models.LegalAct(
        title=act.title,
        isap_id=act.isap_id,
        publication_date=act.publication_date,
        document_type=act.document_type,
        content=act.content,
        pdf_url=str(act.pdf_url) if act.pdf_url else None,
        local_path=local_path
    )
    db.add(db_legal_act)
    
    # Powiązanie ze sprawą
    case.legal_acts.append(db_legal_act)
    db.commit()
    db.refresh(db_legal_act)
    
    # Dodanie do bazy wektorowej
    if act.content:
        await rag_engine.add_documents([{
            "id": f"legal_act_{db_legal_act.id}",
            "title": db_legal_act.title,
            "content": act.content,
            "type": "legal_act"
        }], str(case_id))
    
    return db_legal_act

@app.get("/cases/{case_id}/legal_acts", response_model=List[schemas.LegalActResponse])
async def get_case_legal_acts(
    case_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Sprawdzenie czy sprawa istnieje
    case = db.query(models.Case).filter(models.Case.id == case_id, models.Case.owner_id == current_user.id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sprawa nie znaleziona"
        )
    
    return case.legal_acts

# Endpointy dla orzeczeń sądowych
@app.post("/saos/search", response_model=Dict[str, Any])
async def search_saos(
    search_request: schemas.SearchJudgmentsRequest,
    current_user: models.User = Depends(get_current_user)
):
    async with SAOSClient() as client:
        results = await client.search_judgments(
            query=search_request.query,
            case_number=search_request.case_number,
            judge_name=search_request.judge_name,
            court_type=search_request.court_type,
            from_date=search_request.from_date,
            to_date=search_request.to_date,
            keywords=search_request.keywords,
            legal_bases=search_request.legal_bases,
            page_size=search_request.page_size,
            page_number=search_request.page_number
        )
    return results

@app.post("/cases/{case_id}/judgments", response_model=schemas.JudgmentResponse)
async def add_judgment(
    case_id: int,
    judgment: schemas.JudgmentCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Sprawdzenie czy sprawa istnieje
    case = db.query(models.Case).filter(models.Case.id == case_id, models.Case.owner_id == current_user.id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sprawa nie znaleziona"
        )
    
    # Sprawdzenie czy orzeczenie już istnieje w bazie
    existing_judgment = db.query(models.Judgment).filter(models.Judgment.saos_id == judgment.saos_id).first()
    
    if existing_judgment:
        # Sprawdź czy jest już powiązane ze sprawą
        if existing_judgment in case.judgments:
            return existing_judgment
        
        # Dodanie powiązania
        case.judgments.append(existing_judgment)
        db.commit()
        return existing_judgment
    
    # Pobranie szczegółów orzeczenia z SAOS jeśli potrzebne
    if not judgment.content:
        async with SAOSClient() as client:
            details = await client.get_judgment_details(judgment.saos_id)
            if details:
                judgment.content = details.get("textContent", "")
                judgment.source_url = f"https://www.saos.org.pl/judgments/{judgment.saos_id}"
    
    # Utworzenie orzeczenia w bazie danych
    db_judgment = models.Judgment(
        saos_id=judgment.saos_id,
        title=judgment.title,
        case_number=judgment.case_number,
        judgment_date=judgment.judgment_date,
        court_name=judgment.court_name,
        court_type=judgment.court_type,
        judges=str(judgment.judges) if judgment.judges else None,
        keywords=str(judgment.keywords) if judgment.keywords else None,
        content=judgment.content,
        source_url=judgment.source_url
    )
    db.add(db_judgment)
    
    # Powiązanie ze sprawą
    case.judgments.append(db_judgment)
    db.commit()
    db.refresh(db_judgment)
    
    # Dodanie do bazy wektorowej
    if judgment.content:
        await rag_engine.add_documents([{
            "id": f"judgment_{db_judgment.id}",
            "title": db_judgment.title,
            "content": judgment.content,
            "type": "judgment"
        }], str(case_id))
    
    return db_judgment

@app.get("/cases/{case_id}/judgments", response_model=List[schemas.JudgmentResponse])
async def get_case_judgments(
    case_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Sprawdzenie czy sprawa istnieje
    case = db.query(models.Case).filter(models.Case.id == case_id, models.Case.owner_id == current_user.id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sprawa nie znaleziona"
        )
    
    return case.judgments

# Endpointy dla pytań i odpowiedzi
@app.post("/cases/{case_id}/questions", response_model=schemas.QuestionResponse)
async def create_question(
    case_id: int,
    question: schemas.QuestionCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Sprawdzenie czy sprawa istnieje
    case = db.query(models.Case).filter(models.Case.id == case_id, models.Case.owner_id == current_user.id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sprawa nie znaleziona"
        )
    
    # Utworzenie pytania w bazie danych
    db_question = models.Question(
        question_text=question.question_text,
        case_id=case_id
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    
    # Generowanie odpowiedzi za pomocą RAG
    response = await rag_engine.query(
        query=question.question_text,
        case_id=str(case_id),
        return_sources=True
    )
    
    # Zapisanie odpowiedzi
    db_question.answer_text = response["answer"]
    db.commit()
    db.refresh(db_question)
    
    return db_question

@app.get("/cases/{case_id}/questions", response_model=List[schemas.QuestionResponse])
async def get_case_questions(
    case_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Sprawdzenie czy sprawa istnieje
    case = db.query(models.Case).filter(models.Case.id == case_id, models.Case.owner_id == current_user.id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sprawa nie znaleziona"
        )
    
    questions = db.query(models.Question).filter(models.Question.case_id == case_id).all()
    return questions

@app.get("/questions/{question_id}", response_model=schemas.QuestionResponse)
async def get_question(
    question_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    question = db.query(models.Question).join(models.Case).filter(
        models.Question.id == question_id,
        models.Case.owner_id == current_user.id
    ).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pytanie nie znalezione"
        )
    
    return question

@app.get("/questions/{question_id}/sources", response_model=List[schemas.SourceInfo])
async def get_question_sources(
    question_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    question = db.query(models.Question).join(models.Case).filter(
        models.Question.id == question_id,
        models.Case.owner_id == current_user.id
    ).first()
    
    if not question:
        raise HTTP