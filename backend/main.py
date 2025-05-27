from fastapi import FastAPI, HTTPException, status, Request, APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import timedelta

from database import get_db
import models
from auth import create_access_token, get_current_active_user, get_password_hash, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES
from middleware import cors_middleware, error_middleware
from config import settings

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

# Add our custom middleware
app.middleware("http")(cors_middleware)
app.middleware("http")(error_middleware)

# Create API router
api_router = APIRouter(prefix="/api")

@api_router.post("/users")
async def create_user(request: Request, db: Session = Depends(get_db)):
    """User registration endpoint"""
    try:
        user_data = await request.json()
        db_user = db.query(models.User).filter(models.User.email == user_data["email"]).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email już zarejestrowany")
        
        hashed_password = get_password_hash(user_data["password"])
        db_user = models.User(
            email=user_data["email"],
            hashed_password=hashed_password,
            full_name=user_data.get("full_name", "")
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return {
            "id": db_user.id,
            "email": db_user.email,
            "full_name": db_user.full_name
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@api_router.post("/token")
async def login_for_access_token(request: Request, db: Session = Depends(get_db)):
    """Login endpoint"""
    try:
        form_data = await request.json()
        user = db.query(models.User).filter(models.User.email == form_data["username"]).first()
        if not user or not verify_password(form_data["password"], user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Niepoprawny email lub hasło"
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@api_router.get("/users/me")
async def read_users_me(request: Request, db: Session = Depends(get_db)):
    """Get current user info"""
    user = await get_current_active_user(request, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return user

# Add router to app
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
