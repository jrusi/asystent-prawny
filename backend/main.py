from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import timedelta
import os

from database import get_db, engine
import models
import schemas
from auth import create_access_token, get_current_active_user, get_password_hash, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES

# Tworzenie tabel w bazie danych
try:
    models.Base.metadata.create_all(bind=engine)
    print("Tabele zostały utworzone pomyślnie")
except Exception as e:
    print(f"Błąd podczas tworzenia tabel: {e}")

app = FastAPI(title="Asystent Prawny")

# Konfiguracja CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Podstawowe endpointy
@app.get("/")
async def root():
    """Endpoint główny"""
    return JSONResponse(
        content={"message": "Asystent Prawny API działa poprawnie"},
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

@app.get("/health")
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
@app.post("/token")
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


@app.post("/users/")
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
    
    return db_user


@app.get("/users/me/")
async def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    """Pobranie informacji o zalogowanym użytkowniku"""
    return current_user


# Chroniony endpoint przykładowy
@app.get("/secure-data/")
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


@app.get("/config")
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


@app.get("/api-info")
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
                    "path": "/users/",
                    "method": "POST",
                    "description": "Rejestracja nowego użytkownika"
                },
                {
                    "path": "/users/me/",
                    "method": "GET",
                    "description": "Informacje o zalogowanym użytkowniku (wymaga uwierzytelnienia)"
                },
                {
                    "path": "/secure-data/",
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


@app.get("/check-services")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
