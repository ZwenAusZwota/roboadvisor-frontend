"""
Migration Script: Füge sector-Spalte zur portfolio_holdings Tabelle hinzu
Kann manuell ausgeführt werden, falls die automatische Migration nicht funktioniert.
"""
from database import engine
from sqlalchemy import text, inspect

def migrate():
    """Fügt die sector-Spalte zur portfolio_holdings Tabelle hinzu"""
    inspector = inspect(engine)
    
    try:
        # Prüfe, ob portfolio_holdings Tabelle existiert
        if 'portfolio_holdings' not in inspector.get_table_names():
            print("portfolio_holdings table does not exist. Cannot run migration.")
            return False
        
        # Prüfe, ob sector-Spalte bereits existiert
        columns = [col['name'] for col in inspector.get_columns('portfolio_holdings')]
        
        if 'sector' in columns:
            print("sector column already exists in portfolio_holdings table. No migration needed.")
            return True
        
        print("Adding sector column to portfolio_holdings table...")
        
        # Bestimme den SQL-Dialekt
        dialect = engine.dialect.name
        
        if dialect == 'postgresql':
            # PostgreSQL Syntax
            with engine.connect() as conn:
                conn.execute(text('ALTER TABLE portfolio_holdings ADD COLUMN sector VARCHAR(100) NULL'))
                conn.commit()
            print("✓ sector column added successfully to portfolio_holdings table (PostgreSQL).")
            return True
        elif dialect in ['mysql', 'mariadb']:
            # MySQL/MariaDB Syntax
            with engine.connect() as conn:
                conn.execute(text('ALTER TABLE portfolio_holdings ADD COLUMN sector VARCHAR(100) NULL'))
                conn.commit()
            print("✓ sector column added successfully to portfolio_holdings table (MySQL/MariaDB).")
            return True
        else:
            print(f"✗ Unknown database dialect '{dialect}'. Cannot add sector column automatically.")
            print("Please run migrate_add_sector_to_portfolio.sql manually.")
            return False
            
    except Exception as e:
        error_msg = str(e)
        # Wenn die Spalte bereits existiert, ist das OK
        if "duplicate column" in error_msg.lower() or "already exists" in error_msg.lower():
            print("sector column already exists in portfolio_holdings table.")
            return True
        elif "permission denied" in error_msg.lower() or "insufficientprivilege" in error_msg.lower():
            print(f"✗ Error: Cannot add sector column due to insufficient permissions: {e}")
            print("Please run migrate_add_sector_to_portfolio.sql manually with appropriate permissions.")
            return False
        else:
            print(f"✗ Error adding sector column: {e}")
            return False

if __name__ == "__main__":
    print("Running migration: Add sector column to portfolio_holdings")
    print("-" * 60)
    success = migrate()
    print("-" * 60)
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed. Please check the error messages above.")



