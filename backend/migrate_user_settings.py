"""
Migration Script: Add user_settings table if missing
Run this script to add the user_settings table to an existing database
"""
from database import engine, Base
from models import UserSettings
from sqlalchemy import inspect

def migrate():
    """Fügt die user_settings Tabelle hinzu, falls sie fehlt"""
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if 'user_settings' in existing_tables:
            print("user_settings table already exists. No migration needed.")
            return
        
        print("Creating user_settings table...")
        # Erstelle nur die user_settings Tabelle
        UserSettings.__table__.create(bind=engine, checkfirst=True)
        print("user_settings table created successfully!")
    except Exception as e:
        print(f"Error creating user_settings table: {e}")
        raise

if __name__ == "__main__":
    migrate()



