from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Request
from sqlalchemy.orm import Session
import os

import models
from database import get_db

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET", "supersecret_replace_in_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """Weryfikacja hasła"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Hashowanie hasła"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Tworzenie tokenu JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(request: Request, db: Session) -> Optional[models.User]:
    """Get current user from JWT token in Authorization header"""
    # Always allow OPTIONS requests
    if request.method == "OPTIONS":
        return None
        
    # Public endpoints don't require authentication
    public_paths = ["/token", "/users", "/health", "", "/docs", "/openapi.json"]
    current_path = request.url.path.replace("/api", "").rstrip("/")
    if current_path in public_paths:
        return None

    # Get token from header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None

    user = db.query(models.User).filter(models.User.email == email).first()
    return user

async def get_current_active_user(request: Request, db: Session) -> Optional[models.User]:
    """Get current active user"""
    # Always allow OPTIONS requests
    if request.method == "OPTIONS":
        return None
        
    user = await get_current_user(request, db)
    if user and not user.is_active:
        return None
    return user
