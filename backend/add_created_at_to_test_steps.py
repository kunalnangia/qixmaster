#!/usr/bin/env python3
"""
Script to add missing created_at column to test_steps table
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent.absolute()
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine, text
from app.db.session import DATABASE_URL

def add_created_at_column():
    """Add created_at column to test_steps table"""
    try:
        # Create sync engine for database operations
        # Use psycopg2 driver for sync operations
        sync_url = str(DATABASE_URL).replace("postgresql://", "postgresql+psycopg2://")
        engine = create_engine(sync_url)
        
        with engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'test_steps' AND column_name = 'created_at'
            """))
            
            if result.fetchone():
                print("Column 'created_at' already exists in test_steps table")
                return True
            
            # Add the missing column
            print("Adding 'created_at' column to test_steps table...")
            conn.execute(text("ALTER TABLE test_steps ADD COLUMN created_at TIMESTAMP WITHOUT TIME ZONE"))
            conn.commit()
            print("Successfully added 'created_at' column to test_steps table")
            
            # Also add updated_at column if it doesn't exist
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'test_steps' AND column_name = 'updated_at'
            """))
            
            if not result.fetchone():
                print("Adding 'updated_at' column to test_steps table...")
                conn.execute(text("ALTER TABLE test_steps ADD COLUMN updated_at TIMESTAMP WITHOUT TIME ZONE"))
                conn.commit()
                print("Successfully added 'updated_at' column to test_steps table")
            
            return True
            
    except Exception as e:
        print(f"Error adding column: {e}")
        return False

if __name__ == "__main__":
    print("Starting database migration to add created_at column to test_steps table...")
    success = add_created_at_column()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
        sys.exit(1)