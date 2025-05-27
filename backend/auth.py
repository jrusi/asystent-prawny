from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db
import os

# Konfiguracja zabezpieczeń
SECRET_KEY = os.getenv("JWT_SECRET", "supersecret_replace_in_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class CustomOAuth2PasswordBearer(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        # List of endpoints that don't require authentication
        public_endpoints = ["/api/token", "/api/users", "/api/health", "/api"]
        
        # Skip authentication for OPTIONS requests and public endpoints
        if request.method == "OPTIONS" or any(request.url.path.endswith(endpoint.strip("/")) for endpoint in public_endpoints):
            return None
            
        try:
            return await super().__call__(request)
        except HTTPException as e:
            if any(request.url.path.endswith(endpoint.strip("/")) for endpoint in public_endpoints):
                return None
            raise e

oauth2_scheme = CustomOAuth2PasswordBearer(tokenUrl="api/token")

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


async def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Pobieranie aktualnie zalogowanego użytkownika na podstawie JWT"""
    # If no token is provided for public endpoints
    if token is None:
        return None
        
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Nie można zweryfikować poświadczeń",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(current_user: Optional[models.User] = Depends(get_current_user)):
    """Sprawdzanie czy użytkownik jest aktywny"""
    # For public endpoints where current_user is None
    if current_user is None:
        return None
        
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Nieaktywny użytkownik")
    return current_user
