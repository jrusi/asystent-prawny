from fastapi import FastAPI, HTTPException, status, Request, APIRouter, Depends, Form, File, UploadFile
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import Dict, Any, List
import json
import os
import shutil
import mimetypes
from pathlib import Path

from database import get_db
import models
import schemas
from auth import create_access_token, get_current_active_user, get_password_hash, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES
from config import settings
from storage import MinioClient

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MinIO client
minio_client = MinioClient(
    endpoint=settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY
)

# Create API router
api_router = APIRouter(prefix="/api")

# Configure maximum upload size (100MB)
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB in bytes

def get_cors_headers(request: Request) -> Dict[str, str]:
    """Get CORS headers for response"""
    origin = request.headers.get("origin")
    if not origin:
        return {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Max-Age": "600",
        }
        
    # Check if origin is allowed
    allowed = False
    for allowed_origin in settings.BACKEND_CORS_ORIGINS:
        if origin.startswith(allowed_origin) or (
            '.app.github.dev' in origin and 
            any(o.endswith('.app.github.dev') for o in settings.BACKEND_CORS_ORIGINS)
        ):
            allowed = True
            break
            
    if not allowed:
        return {}
        
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
        
    # Ensure proper JSON serialization for all types
    if not isinstance(content, (str, int, float, bool, type(None))):
        content = json.loads(json.dumps(content, cls=CustomJSONEncoder))
        
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
async def login_for_access_token(
    request: Request,
    db: Session = Depends(get_db),
    username: str = Form(None),
    password: str = Form(None)
):
    """Login endpoint"""
    if request.method == "OPTIONS":
        return Response(status_code=200, headers=get_cors_headers(request))
        
    try:
        # If form data is not provided, try to get JSON data
        if username is None or password is None:
            form_data = await request.json()
            username = form_data.get("username") or form_data.get("email")
            password = form_data.get("password")
            
        if not username or not password:
            return create_response(
                {"detail": "Email i hasło są wymagane"},
                status_code=status.HTTP_400_BAD_REQUEST,
                headers=get_cors_headers(request)
            )
            
        user = db.query(models.User).filter(models.User.email == username).first()
        if not user or not verify_password(password, user.hashed_password):
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

@api_router.get("/cases", response_model=List[schemas.CaseResponse])
async def get_cases(request: Request, db: Session = Depends(get_db)):
    """Get all cases for the current user"""
    if request.method == "OPTIONS":
        return Response(status_code=200, headers=get_cors_headers(request))
        
    try:
        user = await get_current_active_user(request, db)
        if not user:
            return create_response(
                {"detail": "Not authenticated"},
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers=get_cors_headers(request)
            )
            
        cases = db.query(models.Case).filter(models.Case.owner_id == user.id).all()
        
        # Convert each case to a Pydantic model and then to dict with proper serialization
        response_cases = [schemas.CaseResponse.model_validate(case) for case in cases]
        response_dicts = [case.model_dump() for case in response_cases]
        
        # Use custom JSON encoder for the response
        return create_response(
            json.loads(json.dumps(response_dicts, cls=CustomJSONEncoder)),
            headers=get_cors_headers(request)
        )
    except Exception as e:
        return create_response(
            {"detail": str(e)},
            status_code=status.HTTP_400_BAD_REQUEST,
            headers=get_cors_headers(request)
        )

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

@api_router.post("/cases", response_model=schemas.CaseResponse)
async def create_case(request: Request, db: Session = Depends(get_db)):
    """Create a new case"""
    if request.method == "OPTIONS":
        return Response(status_code=200, headers=get_cors_headers(request))
        
    try:
        user = await get_current_active_user(request, db)
        if not user:
            return create_response(
                {"detail": "Not authenticated"},
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers=get_cors_headers(request)
            )
            
        case_data = await request.json()
        case_create = schemas.CaseCreate(**case_data)
        
        db_case = models.Case(
            title=case_create.title,
            description=case_create.description or "",
            owner_id=user.id,
            documents=[],  # Explicitly initialize documents as empty list
            legal_acts=[],  # Initialize legal_acts as empty list
            judgments=[]  # Initialize judgments as empty list
        )
        
        db.add(db_case)
        db.commit()
        db.refresh(db_case)
        
        # Convert to Pydantic model and then to dict with datetime handling
        response = schemas.CaseResponse.model_validate(db_case)
        response_dict = response.model_dump()
        
        # Use custom JSON encoder for the response
        return create_response(
            json.loads(json.dumps(response_dict, cls=CustomJSONEncoder)),
            headers=get_cors_headers(request)
        )
    except Exception as e:
        return create_response(
            {"detail": str(e)},
            status_code=status.HTTP_400_BAD_REQUEST,
            headers=get_cors_headers(request)
        )

@api_router.delete("/cases/{case_id}")
async def delete_case(case_id: int, request: Request, db: Session = Depends(get_db)):
    """Delete a case and all its associated files"""
    if request.method == "OPTIONS":
        return Response(status_code=200, headers=get_cors_headers(request))
        
    try:
        user = await get_current_active_user(request, db)
        if not user:
            return create_response(
                {"detail": "Not authenticated"},
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers=get_cors_headers(request)
            )
            
        # Get the case and verify ownership
        case = db.query(models.Case).filter(
            models.Case.id == case_id,
            models.Case.owner_id == user.id  # Ensure case belongs to user
        ).first()
        
        if not case:
            return create_response(
                {"detail": "Case not found or access denied"},
                status_code=status.HTTP_404_NOT_FOUND,
                headers=get_cors_headers(request)
            )
            
        # Delete all associated files from MinIO
        try:
            # Delete case directory and all its contents from MinIO
            case_path = f"users/{user.id}/cases/{case.id}"
            minio_client.delete_case_directory(case_path)
        except Exception as e:
            print(f"Error during MinIO cleanup for case {case.id}: {str(e)}")
            # Continue with database deletion even if MinIO cleanup fails
            
        # Delete the case from database (this will cascade delete related records)
        db.delete(case)
        db.commit()
        
        return create_response(
            {"detail": "Case and all associated files deleted successfully"},
            headers=get_cors_headers(request)
        )
    except Exception as e:
        db.rollback()  # Rollback transaction on error
        return create_response(
            {"detail": str(e)},
            status_code=status.HTTP_400_BAD_REQUEST,
            headers=get_cors_headers(request)
        )

@api_router.post("/cases/{case_id}/documents", response_model=schemas.DocumentResponse)
async def upload_document(
    case_id: int,
    file: UploadFile = File(...),
    document_type: str = Form(None),
    description: str = Form(None),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Upload a document to a case"""
    if request.method == "OPTIONS":
        return Response(status_code=200, headers=get_cors_headers(request))
        
    try:
        # Check file size before reading
        file_size = 0
        chunk_size = 1024 * 1024  # 1MB chunks
        content = bytearray()
        
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            file_size += len(chunk)
            if file_size > MAX_UPLOAD_SIZE:
                return create_response(
                    {"detail": f"File size exceeds maximum limit of {MAX_UPLOAD_SIZE // (1024 * 1024)}MB"},
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    headers=get_cors_headers(request)
                )
            content.extend(chunk)
            
        # Reset file position for potential re-read
        await file.seek(0)
        
        user = await get_current_active_user(request, db)
        if not user:
            return create_response(
                {"detail": "Not authenticated"},
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers=get_cors_headers(request)
            )
            
        # Get the case and verify ownership
        case = db.query(models.Case).filter(
            models.Case.id == case_id,
            models.Case.owner_id == user.id  # Ensure case belongs to user
        ).first()
        
        if not case:
            return create_response(
                {"detail": "Case not found or access denied"},
                status_code=status.HTTP_404_NOT_FOUND,
                headers=get_cors_headers(request)
            )
            
        # Generate unique object name for MinIO with user isolation
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        original_filename = file.filename
        file_extension = os.path.splitext(original_filename)[1]
        safe_filename = f"{timestamp}{file_extension}"
        object_path = f"users/{user.id}/cases/{case.id}/documents/{safe_filename}"
        
        # Use the content we've already read
        minio_client.upload_file(object_path, content)
        
        # Determine file type if not provided
        if not document_type:
            mime_type, _ = mimetypes.guess_type(original_filename)
            document_type = mime_type if mime_type else "application/octet-stream"
            
        # Create document record
        db_document = models.Document(
            title=original_filename,
            description=description,
            file_path=object_path,  # Store MinIO object path
            file_type=document_type,
            case_id=case.id
        )
        
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        # Convert to response model
        response = schemas.DocumentResponse.model_validate(db_document)
        response_dict = response.model_dump()
        
        return create_response(
            json.loads(json.dumps(response_dict, cls=CustomJSONEncoder)),
            headers=get_cors_headers(request)
        )
    except Exception as e:
        # If document was created in DB but MinIO upload failed, clean up
        if 'db_document' in locals():
            db.delete(db_document)
            db.commit()
            
        return create_response(
            {"detail": str(e)},
            status_code=status.HTTP_400_BAD_REQUEST,
            headers=get_cors_headers(request)
        )

@api_router.get("/cases/{case_id}/documents/{document_id}")
async def get_document(
    case_id: int,
    document_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get a document from a case"""
    if request.method == "OPTIONS":
        return Response(status_code=200, headers=get_cors_headers(request))
        
    try:
        user = await get_current_active_user(request, db)
        if not user:
            return create_response(
                {"detail": "Not authenticated"},
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers=get_cors_headers(request)
            )
            
        # Get the document and verify ownership through case
        document = db.query(models.Document).join(
            models.Case
        ).filter(
            models.Document.id == document_id,
            models.Document.case_id == case_id,
            models.Case.owner_id == user.id  # Ensure case belongs to user
        ).first()
        
        if not document:
            return create_response(
                {"detail": "Document not found or access denied"},
                status_code=status.HTTP_404_NOT_FOUND,
                headers=get_cors_headers(request)
            )
            
        # Get file content from MinIO
        content = minio_client.download_file(document.file_path)
        
        # Return file content with appropriate headers
        return Response(
            content=content,
            media_type=document.file_type,
            headers={
                **get_cors_headers(request),
                "Content-Disposition": f'attachment; filename="{document.title}"'
            }
        )
    except Exception as e:
        return create_response(
            {"detail": str(e)},
            status_code=status.HTTP_400_BAD_REQUEST,
            headers=get_cors_headers(request)
        )

# Add router to app
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
