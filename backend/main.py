from fastapi import FastAPI, Depends, HTTPException, status, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
from datetime import timedelta
import os

from database import get_db, engine
import models
import schemas
from auth import create_access_token, get_current_active_user, get_password_hash, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES
from storage import MinioClient
from config import settings

# Inicjalizacja klienta MinIO
minio_client = MinioClient(
    endpoint=settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ROOT_USER,
    secret_key=settings.MINIO_ROOT_PASSWORD
)

# Sprawdzenie połączenia z MinIO
try:
    minio_client.check_connection()
    print("Połączenie z MinIO działa poprawnie")
except Exception as e:
    print(f"Błąd połączenia z MinIO: {e}")

# Funkcja do sprawdzania czy tabela istnieje
def table_exists(table_name):
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

# Tworzenie tabel w bazie danych
def init_db():
    try:
        # Sprawdź czy tabela users istnieje
        if not table_exists("users"):
            # Utwórz wszystkie tabele
            models.Base.metadata.create_all(bind=engine)
            print("Tabele zostały utworzone pomyślnie")
        else:
            print("Tabele już istnieją")
    except Exception as e:
        print(f"Błąd podczas tworzenia tabel: {e}")
        raise e

# Inicjalizacja bazy danych
init_db()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

# Configure CORS first
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600  # Cache preflight response for 10 minutes
)

# Public endpoints that don't require authentication
public_endpoints = [
    "/api/token",
    "/api/users",
    "/api/health",
    "/api",
    "/docs",
    "/openapi.json"
]

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    path = request.url.path
    
    # Always allow OPTIONS requests and public endpoints
    if request.method == "OPTIONS" or any(path.rstrip("/") == endpoint.rstrip("/") for endpoint in public_endpoints):
        response = await call_next(request)
        return response

    # For all other requests, continue with normal flow
    response = await call_next(request)
    return response

# Utworzenie routera API
api_router = APIRouter(prefix="/api")

@api_router.get("")  # Root endpoint for /api
async def root():
    """Endpoint główny"""
    return JSONResponse(
        content={"message": "Asystent Prawny API działa poprawnie"},
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

@api_router.get("/health")  # Remove trailing slash
async def health_check():
    """Endpoint sprawdzający stan usługi"""
    return JSONResponse(
        content={
            "status": "healthy",
            "version": "0.1.0",
            "environment": "test"
        },
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

# Endpointy uwierzytelniania
@api_router.post("/token")  # Remove trailing slash
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Endpoint do logowania i uzyskania tokenu JWT"""
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Niepoprawny email lub hasło",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@api_router.post("/users")  # Remove trailing slash
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


@api_router.get("/users/me")  # Remove trailing slash
async def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    """Pobranie informacji o zalogowanym użytkowniku"""
    return current_user


# Endpointy do zarządzania sprawami
@api_router.get("/cases")
async def get_cases(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Pobranie listy spraw użytkownika"""
    cases = db.query(models.Case).filter(models.Case.owner_id == current_user.id).all()
    return cases

@api_router.post("/cases")
async def create_case(
    case: schemas.CaseCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Utworzenie nowej sprawy"""
    db_case = models.Case(**case.dict(), owner_id=current_user.id)
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    
    # Utworzenie struktury katalogów dla sprawy w MinIO
    minio_client.create_case_directory(f"users/{current_user.id}/cases/{db_case.id}")
    
    return db_case

@api_router.get("/cases/{case_id}")
async def get_case(
    case_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Pobranie szczegółów sprawy"""
    case = db.query(models.Case).filter(
        models.Case.id == case_id,
        models.Case.owner_id == current_user.id
    ).first()
    
    if case is None:
        raise HTTPException(status_code=404, detail="Sprawa nie została znaleziona")
    
    return case

@api_router.put("/cases/{case_id}")
async def update_case(
    case_id: int,
    case_update: schemas.CaseUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Aktualizacja sprawy"""
    db_case = db.query(models.Case).filter(
        models.Case.id == case_id,
        models.Case.owner_id == current_user.id
    ).first()
    
    if db_case is None:
        raise HTTPException(status_code=404, detail="Sprawa nie została znaleziona")
    
    for key, value in case_update.dict(exclude_unset=True).items():
        setattr(db_case, key, value)
    
    db.commit()
    db.refresh(db_case)
    return db_case

@api_router.delete("/cases/{case_id}")
async def delete_case(
    case_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Usunięcie sprawy"""
    db_case = db.query(models.Case).filter(
        models.Case.id == case_id,
        models.Case.owner_id == current_user.id
    ).first()
    
    if db_case is None:
        raise HTTPException(status_code=404, detail="Sprawa nie została znaleziona")
    
    # Usunięcie plików sprawy z MinIO
    try:
        minio_client.delete_case_directory(f"users/{current_user.id}/cases/{case_id}")
    except Exception as e:
        print(f"Błąd podczas usuwania plików sprawy: {e}")
    
    db.delete(db_case)
    db.commit()
    return {"message": "Sprawa została usunięta"}


@api_router.get("/secure-data")  # Remove trailing slash
async def get_secure_data(current_user: models.User = Depends(get_current_active_user)):
    """Przykładowy endpoint wymagający uwierzytelnienia"""
    return JSONResponse(
        content={
            "message": "To są chronione dane",
            "user_id": current_user.id,
            "email": current_user.email
        },
        headers={"Content-Type": "application/json; charset=utf-8"}
    )


@api_router.get("/config")  # Remove trailing slash
async def get_config():
    """Endpoint pokazujący konfigurację (bez wrażliwych danych)"""
    return JSONResponse(
        content={
            "database_connection": "configured",
            "auth_enabled": True,
            "jwt_expiration_minutes": ACCESS_TOKEN_EXPIRE_MINUTES,
            "services": {
                "database": True,
                "authentication": True
            }
        },
        headers={"Content-Type": "application/json; charset=utf-8"}
    )


@api_router.get("/api-info")  # Remove trailing slash
async def api_info():
    """Informacje o dostępnych endpointach API"""
    return JSONResponse(
        content={
            "api_version": "0.1.0",
            "endpoints": [
                {
                    "path": "/",
                    "method": "GET",
                    "description": "Podstawowy endpoint informacyjny"
                },
                {
                    "path": "/health",
                    "method": "GET",
                    "description": "Endpoint sprawdzający stan usługi"
                },
                {
                    "path": "/token",
                    "method": "POST",
                    "description": "Logowanie i uzyskanie tokenu JWT"
                },
                {
                    "path": "/users",
                    "method": "POST",
                    "description": "Rejestracja nowego użytkownika"
                },
                {
                    "path": "/users/me",
                    "method": "GET",
                    "description": "Informacje o zalogowanym użytkowniku (wymaga uwierzytelnienia)"
                },
                {
                    "path": "/cases",
                    "method": "GET",
                    "description": "Lista spraw użytkownika (wymaga uwierzytelnienia)"
                },
                {
                    "path": "/cases",
                    "method": "POST",
                    "description": "Utworzenie nowej sprawy (wymaga uwierzytelnienia)"
                },
                {
                    "path": "/cases/{case_id}",
                    "method": "GET",
                    "description": "Szczegóły sprawy (wymaga uwierzytelnienia)"
                },
                {
                    "path": "/cases/{case_id}",
                    "method": "PUT",
                    "description": "Aktualizacja sprawy (wymaga uwierzytelnienia)"
                },
                {
                    "path": "/cases/{case_id}",
                    "method": "DELETE",
                    "description": "Usunięcie sprawy (wymaga uwierzytelnienia)"
                },
                {
                    "path": "/secure-data",
                    "method": "GET",
                    "description": "Przykładowy chroniony endpoint (wymaga uwierzytelnienia)"
                },
                {
                    "path": "/config",
                    "method": "GET",
                    "description": "Informacje o konfiguracji (bez wrażliwych danych)"
                },
                {
                    "path": "/api-info",
                    "method": "GET",
                    "description": "Informacje o dostępnych endpointach API"
                },
                {
                    "path": "/check-services",
                    "method": "GET",
                    "description": "Sprawdzenie stanu usług"
                }
            ],
            "authentication": {
                "type": "JWT",
                "token_url": "/token",
                "expiration_minutes": ACCESS_TOKEN_EXPIRE_MINUTES
            }
        },
        headers={"Content-Type": "application/json; charset=utf-8"}
    )


@api_router.get("/check-services")  # Remove trailing slash
async def check_services(db: Session = Depends(get_db)):
    """Sprawdzenie stanu połączeń z usługami"""
    services_status = {
        "database": "Nie sprawdzono",
        "authentication": "Nie sprawdzono"
    }
    
    # Sprawdzenie połączenia z bazą danych
    try:
        # Poprawione zapytanie z użyciem text()
        db.execute(text("SELECT 1")).fetchone()
        services_status["database"] = "Działa"
        
        # Sprawdzenie czy tabela users istnieje
        try:
            users_count = db.query(models.User).count()
            services_status["authentication"] = "Działa"
        except Exception as e:
            services_status["authentication"] = f"Błąd: {str(e)}"
    except Exception as e:
        services_status["database"] = f"Błąd: {str(e)}"
    
    return JSONResponse(
        content={
            "status": all(status == "Działa" for status in services_status.values()),
            "services": services_status
        },
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

# Dodanie routera API do głównej aplikacji
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
