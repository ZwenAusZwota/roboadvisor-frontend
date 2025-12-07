from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from urllib.parse import quote_plus

# Database URL aus Environment Variable lesen
# DigitalOcean stellt DATABASE_URL automatisch bereit
DATABASE_URL = os.getenv("DATABASE_URL")

# Falls DATABASE_URL nicht gesetzt ist, verwende lokale Konfiguration
if not DATABASE_URL:
    # Für lokale Entwicklung
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "roboadvisor")
    
    # URL-encode das Passwort für den Connection String
    encoded_password = quote_plus(DB_PASSWORD)
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
else:
    # DigitalOcean stellt oft PostgreSQL bereit
    # Wenn die URL mit postgres:// beginnt, konvertiere zu postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLAlchemy Engine erstellen
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Prüft Verbindung vor Verwendung
    pool_recycle=300,    # Recyclet Verbindungen nach 5 Minuten
    echo=False           # SQL-Queries loggen (für Debugging auf True setzen)
)

# Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base Class für Models
Base = declarative_base()

# Dependency für FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper function für init_db
def init_db():
    """Erstellt alle Tabellen in der Datenbank"""
    from models import User, RiskProfile, Security, TelegramUser
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Error creating database tables: {e}")
        raise

