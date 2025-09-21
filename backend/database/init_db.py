import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Import database configuration
from app.db.session import Base, engine, get_db, SessionLocal

# Import all SQLAlchemy models to ensure they are registered with SQLAlchemy
from app.models.db_models import *

def database_exists(engine, database_name):
    """Check if database exists by trying to connect to it"""
    try:
        # Try to connect to the database
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

def create_database(engine):
    """Create database - simplified implementation"""
    # For PostgreSQL, we would need to connect to a different database first
    # For now, we'll just try to create tables directly
    print("Attempting to create database tables...")
    return True

def init_db():
    """Initialize the database and create all tables."""
    print("Initializing database...")
    
    # Check if database exists (simplified check)
    db_exists = database_exists(engine, engine.url.database)
    if not db_exists:
        print(f"Attempting to create database: {engine.url.database}")
        create_database(engine)
    
    # Create all tables
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    print("Database initialization complete!")

def drop_db():
    """
    Drop all tables in the database.
    WARNING: This will delete all data in the database!
    """
    confirmation = input("WARNING: This will drop all tables in the database. Continue? (y/n): ")
    if confirmation.lower() == 'y':
        print("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        print("All tables dropped.")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database initialization utility")
    parser.add_argument(
        "--drop", 
        action="store_true", 
        help="Drop all tables before initializing"
    )
    
    args = parser.parse_args()
    
    if args.drop:
        drop_db()
    
    init_db()