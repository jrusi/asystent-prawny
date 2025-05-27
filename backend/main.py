from fastapi import FastAPI, HTTPException, status, Request, APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Dict, Any

from database import get_db
import models
from auth import create_access_token, get_current_active_user, get_password_hash, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES
from config import settings

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

# Create API router
api_router = APIRouter(prefix="/api")

def get_cors_headers(request: Request) -> Dict[str, str]:
    """Get CORS headers for response"""
    origin = request.headers.get("origin", "*")
    return {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Max-Age": "600",
    }

def create_response(content: Any, status_code: int = 200, headers: Dict[str, str] = None) -> Response:
    """Create a response with CORS headers"""
    if headers is None:
        headers = {}
    return JSONResponse(
        content=content,
        status_code=status_code,
        headers=headers
    )

@api_router.options("/{path:path}")
async def options_route(request: Request):
    """Handle all OPTIONS requests"""
    return Response(status_code=200, headers=get_cors_headers(request))

@api_router.post("/users")
async def create_user(request: Request, db: Session = Depends(get_db)):
    """User registration endpoint"""
    if request.method == "OPTIONS":
        return Response(status_code=200, headers=get_cors_headers(request))
        
    try:
        user_data = await request.json()
        db_user = db.query(models.User).filter(models.User.email == user_data["email"]).first()
        if db_user:
            return create_response(
                {"detail": "Email już zarejestrowany"},
                status_code=400,
                headers=get_cors_headers(request)
            )
        
        hashed_password = get_password_hash(user_data["password"])
        db_user = models.User(
            email=user_data["email"],
            hashed_password=hashed_password,
            full_name=user_data.get("full_name", "")
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return create_response(
            {
                "id": db_user.id,
                "email": db_user.email,
                "full_name": db_user.full_name
            },
            headers=get_cors_headers(request)
        )
    except Exception as e:
        return create_response(
            {"detail": str(e)},
            status_code=status.HTTP_400_BAD_REQUEST,
            headers=get_cors_headers(request)
        )

@api_router.post("/token")
async def login_for_access_token(request: Request, db: Session = Depends(get_db)):
    """Login endpoint"""
    if request.method == "OPTIONS":
        return Response(status_code=200, headers=get_cors_headers(request))
        
    try:
        form_data = await request.json()
        user = db.query(models.User).filter(models.User.email == form_data["username"]).first()
        if not user or not verify_password(form_data["password"], user.hashed_password):
            return create_response(
                {"detail": "Niepoprawny email lub hasło"},
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers=get_cors_headers(request)
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        return create_response(
            {"access_token": access_token, "token_type": "bearer"},
            headers=get_cors_headers(request)
        )
    except Exception as e:
        return create_response(
            {"detail": str(e)},
            status_code=status.HTTP_400_BAD_REQUEST,
            headers=get_cors_headers(request)
        )

@api_router.get("/users/me")
async def read_users_me(request: Request, db: Session = Depends(get_db)):
    """Get current user info"""
    if request.method == "OPTIONS":
        return Response(status_code=200, headers=get_cors_headers(request))
        
    user = await get_current_active_user(request, db)
    if not user:
        return create_response(
            {"detail": "Not authenticated"},
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers=get_cors_headers(request)
        )
    return create_response(
        {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name
        },
        headers=get_cors_headers(request)
    )

# Add router to app
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
