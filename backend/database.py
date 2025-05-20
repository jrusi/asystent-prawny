import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Pobranie URL bazy danych z zmiennej środowiskowej
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/legal_assistant")

# Utworzenie silnika SQLAlchemy
engine = create_engine(DATABASE_URL)

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