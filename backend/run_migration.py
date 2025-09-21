#!/usr/bin/env python3
"""
Script to run database migrations for adding comprehensive test case fields
"""
import asyncio
import sys
import os
from alembic.config import Config
from alembic import command

# Add the backend directory to the Python path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

def run_migration():
    """Run the database migration to add comprehensive test case fields"""
    try:
        # Create alembic config
        alembic_cfg = Config(os.path.join(backend_path, "alembic.ini"))
        alembic_cfg.set_main_option("script_location", os.path.join(backend_path, "alembic"))
        
        # Run the migration
        print("Running database migration...")
        command.upgrade(alembic_cfg, "head")
        print("Database migration completed successfully!")
        
    except Exception as e:
        print(f"Error running migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_migration()