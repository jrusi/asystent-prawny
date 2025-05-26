import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time
from sqlalchemy.sql import text

# Pobranie URL bazy danych z zmiennej środowiskowej
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/legal_assistant")

# Utworzenie silnika SQLAlchemy z obsługą ponownych prób połączenia
def create_db_engine(max_retries=5):
    for attempt in range(max_retries):
        try:
            engine = create_engine(
                DATABASE_URL,
                pool_pre_ping=True,  # Enable connection health checks
                pool_recycle=3600,   # Recycle connections after 1 hour
            )
            # Test connection
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            print(f"Połączenie z bazą danych nawiązane pomyślnie (próba {attempt + 1})")
            return engine
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Błąd połączenia z bazą danych (próba {attempt + 1}): {e}")
                print(f"Ponowna próba za {wait_time} sekund...")
                time.sleep(wait_time)
            else:
                print(f"Nie udało się połączyć z bazą danych po {max_retries} próbach")
                raise

# Utworzenie silnika SQLAlchemy
engine = create_db_engine()

# Utworzenie lokalnej sesji
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Bazowa klasa modeli
Base = declarative_base()

# Funkcja do uzyskania sesji bazy danych
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()