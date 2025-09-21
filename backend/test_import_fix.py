#!/usr/bin/env python3
"""
Test script to verify that the force_connection_reset function can be imported
"""
import sys
import os

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Mock the environment variables to avoid database connection issues
os.environ['DATABASE_URL'] = 'sqlite:///test.db'
os.environ['DATABASE_URL_ASYNC'] = 'sqlite+aiosqlite:///test.db'

try:
    from app.db.session import force_connection_reset, reset_database_connections
    print("SUCCESS: Both functions imported correctly")
    print(f"force_connection_reset: {force_connection_reset}")
    print(f"reset_database_connections: {reset_database_connections}")
except ImportError as e:
    print(f"ERROR: Import failed - {e}")
except Exception as e:
    print(f"ERROR: Unexpected error - {e}")