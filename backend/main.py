from fastapi import FastAPI, HTTPException, Depends, status, APIRouter
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
import traceback

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Logs in stdout (wird von DigitalOcean erfasst)
    ]
)
logger = logging.getLogger(__name__)

# Database imports
from database import get_db, init_db, engine
from models import User
from auth import (
    get_password_hash,
    verify_password,
    get_user_by_email,
    get_current_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    oauth2_scheme
)

app = FastAPI(title="RoboAdvisor API", version="1.0.0")

# CORS konfigurieren
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In Produktion spezifische Domains angeben
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: Optional[str]
    email: str
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Startup Event: Erstelle Tabellen beim Start
@app.on_event("startup")
async def startup_event():
    try:
        logger.info("Starting up application...")
        init_db()
        # Prüfe, ob Tabellen existieren
        from sqlalchemy import inspect
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        if 'users' in existing_tables:
            logger.info("Database tables exist, application ready.")
        else:
            logger.warning("Database tables do not exist. Please create them manually using create_tables.sql")
            logger.warning("See DATABASE_SETUP.md for instructions.")
    except Exception as e:
        logger.warning(f"Could not initialize database: {e}")
        logger.warning("Database tables may already exist or connection failed.")

# API Router OHNE Prefix
# DigitalOcean generiert automatisch: /roboadvisor-frontend-backend
# Frontend sendet: /roboadvisor-frontend-backend/api/health
# Backend erhält: /roboadvisor-frontend-backend/api/health
# Router OHNE Prefix + Route /api/health = /api/health
# Aber DigitalOcean sendet /roboadvisor-frontend-backend/api/health
# Lösung: Router OHNE Prefix, Endpoints MIT /api Prefix
api_router = APIRouter()

# Routes ohne Prefix (für Health Checks)
@app.get("/")
async def root():
    return {"message": "RoboAdvisor API", "status": "running"}

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check ohne /api prefix (für direkten Zugriff)"""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# API Routes MIT /api Prefix
# Frontend sendet: /roboadvisor-frontend-backend/api/auth/register
# DigitalOcean leitet an Backend weiter: /roboadvisor-frontend-backend/api/auth/register
# Router OHNE Prefix + Route /api/auth/register = /api/auth/register
# Aber DigitalOcean sendet /roboadvisor-frontend-backend/api/auth/register
# Lösung: Endpoints MIT /api Prefix, damit sie mit /roboadvisor-frontend-backend/api/... funktionieren
@api_router.get("/api/health")
async def health_check_api(db: Session = Depends(get_db)):
    """Health check mit /api prefix"""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@api_router.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f"Registration attempt for email: {user.email}")
        
        # Validierung: Passwort-Länge prüfen (sinnvolle Limits)
        # Argon2 hat kein technisches Limit, aber sehr lange Passwörter sind unpraktisch
        if len(user.password) < 6:
            logger.warning(f"Registration failed: Password too short for {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwort muss mindestens 6 Zeichen lang sein."
            )
        
        if len(user.password) > 128:
            logger.warning(f"Registration failed: Password too long ({len(user.password)} chars) for {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwort ist zu lang. Bitte verwenden Sie maximal 128 Zeichen."
            )
        
        # Prüfe ob User bereits existiert
        db_user = get_user_by_email(db, email=user.email)
        if db_user:
            logger.warning(f"Registration failed: Email already registered - {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Diese E-Mail-Adresse ist bereits registriert"
            )
        
        # Erstelle neuen User
        hashed_password = get_password_hash(user.password)
        db_user = User(
            name=user.name,
            email=user.email,
            password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"User registered successfully: {user.email} (ID: {db_user.id})")
        return UserResponse(
            id=db_user.id,
            name=db_user.name,
            email=db_user.email
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        error_traceback = traceback.format_exc()
        logger.error(f"Registration failed for {user.email}: {str(e)}")
        logger.error(f"Traceback: {error_traceback}")
        # Generische Fehlermeldung für den Benutzer
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registrierung fehlgeschlagen. Bitte versuchen Sie es später erneut."
        )

@api_router.post("/api/auth/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = get_user_by_email(db, email=form_data.username)  # username ist hier die email
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-Mail oder Passwort falsch",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-Mail oder Passwort falsch",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.post("/api/auth/login-json", response_model=Token)
async def login_json(
    user_login: UserLogin,
    db: Session = Depends(get_db)
):
    user = get_user_by_email(db, email=user_login.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-Mail oder Passwort falsch"
        )
    if not verify_password(user_login.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-Mail oder Passwort falsch"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.get("/api/auth/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email
    )

# Globaler Exception Handler für unerwartete Fehler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    error_traceback = traceback.format_exc()
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(f"Traceback: {error_traceback}")
    logger.error(f"Request: {request.method} {request.url}")
    # Generische Fehlermeldung für den Benutzer
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Ein Fehler ist aufgetreten. Bitte versuchen Sie es später erneut."}
    )

# Router zur App hinzufügen
app.include_router(api_router)

# User routes importieren und hinzufügen (nach api_router, um zirkulären Import zu vermeiden)
from user_routes import router as user_router
app.include_router(user_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
