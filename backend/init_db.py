"""
Database Initialization Script
Erstellt alle Tabellen basierend auf den SQLAlchemy Models
"""
from database import engine, Base
from models import User, RiskProfile, Security, TelegramUser

def init_db():
    """Erstellt alle Tabellen in der Datenbank"""
    try:
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        raise

if __name__ == "__main__":
    init_db()

