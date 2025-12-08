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
    from models import User, RiskProfile, Security, TelegramUser, UserSettings, PortfolioHolding
    from sqlalchemy import inspect
    
    try:
        # Prüfe, welche Tabellen bereits existieren
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        # Definiere alle erwarteten Tabellen
        expected_tables = ['users', 'risk_profiles', 'securities', 'telegram_users', 'user_settings', 'portfolio_holdings']
        missing_tables = [table for table in expected_tables if table not in existing_tables]
        
        if missing_tables:
            print(f"Creating missing tables: {', '.join(missing_tables)}")
            # SQLAlchemy's create_all() erstellt nur fehlende Tabellen
            # und ignoriert bereits existierende
            Base.metadata.create_all(bind=engine)
            print("Database tables created/updated successfully!")
        else:
            print("All database tables already exist.")
        
        # Führe Migrationen für bestehende Tabellen aus
        migrate_add_sector_column()
        
    except Exception as e:
        error_msg = str(e)
        # Bei PostgreSQL-Berechtigungsfehlern: Warnung statt Fehler
        if "permission denied" in error_msg.lower() or "insufficientprivilege" in error_msg.lower():
            print(f"Warning: Cannot create tables due to insufficient permissions: {e}")
            print("Please create tables manually or grant CREATE privileges to the database user.")
            print("See DATABASE_SETUP.md for instructions.")
            # Prüfe, ob Tabellen trotzdem existieren
            try:
                inspector = inspect(engine)
                existing_tables = inspector.get_table_names()
                if 'users' in existing_tables:
                    print("Some tables exist, application can continue.")
                    print("Note: Missing tables may cause errors. Please run create_tables.sql manually.")
                    return
            except:
                pass
            # Wir werfen den Fehler nicht, damit die App trotzdem starten kann
            # wenn die Tabellen bereits existieren
        else:
            print(f"Error creating database tables: {e}")
            raise

def migrate_add_sector_column():
    """Fügt die sector-Spalte zur portfolio_holdings Tabelle hinzu, falls sie nicht existiert"""
    from sqlalchemy import inspect
    
    try:
        inspector = inspect(engine)
        
        # Prüfe, ob portfolio_holdings Tabelle existiert
        if 'portfolio_holdings' not in inspector.get_table_names():
            print("portfolio_holdings table does not exist. Skipping sector column migration.")
            return
        
        # Prüfe, ob sector-Spalte bereits existiert
        columns = [col['name'] for col in inspector.get_columns('portfolio_holdings')]
        
        if 'sector' not in columns:
            print("Adding sector column to portfolio_holdings table...")
            
            # Bestimme den SQL-Dialekt
            dialect = engine.dialect.name
            
            if dialect == 'postgresql':
                # PostgreSQL Syntax
                with engine.connect() as conn:
                    conn.execute(text('ALTER TABLE portfolio_holdings ADD COLUMN sector VARCHAR(100) NULL'))
                    conn.commit()
                print("sector column added successfully to portfolio_holdings table (PostgreSQL).")
            elif dialect in ['mysql', 'mariadb']:
                # MySQL/MariaDB Syntax
                with engine.connect() as conn:
                    conn.execute(text('ALTER TABLE portfolio_holdings ADD COLUMN sector VARCHAR(100) NULL'))
                    conn.commit()
                print("sector column added successfully to portfolio_holdings table (MySQL/MariaDB).")
            else:
                print(f"Warning: Unknown database dialect '{dialect}'. Cannot add sector column automatically.")
                print("Please run migrate_add_sector_to_portfolio.sql manually.")
        else:
            print("sector column already exists in portfolio_holdings table.")
            
    except Exception as e:
        error_msg = str(e)
        # Wenn die Spalte bereits existiert, ist das OK
        if "duplicate column" in error_msg.lower() or "already exists" in error_msg.lower():
            print("sector column already exists in portfolio_holdings table.")
        elif "permission denied" in error_msg.lower() or "insufficientprivilege" in error_msg.lower():
            print(f"Warning: Cannot add sector column due to insufficient permissions: {e}")
            print("Please run migrate_add_sector_to_portfolio.sql manually.")
        else:
            print(f"Warning: Error checking/adding sector column: {e}")
            print("The application will continue, but portfolio sector functionality may not work.")
            print("Please run migrate_add_sector_to_portfolio.sql manually.")

