from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
import os

from database import get_db, engine
import models

# Tworzenie tabel w bazie danych
models.Base.metadata.create_all(bind=engine)

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

@app.get("/check-services")
async def check_services(db: Session = Depends(get_db)):
    """Sprawdzenie stanu połączeń z usługami"""
    services_status = {
        "database": "Błąd",
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
        except:
            services_status["authentication"] = "Tabela nie istnieje"
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
