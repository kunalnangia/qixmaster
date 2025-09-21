#!/usr/bin/env python3
"""
Simple verification script to check if the force_connection_reset function can be imported
"""
import sys
import os

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

print("Attempting to import force_connection_reset from app.db.session...")

try:
    # Try to import the function directly
    from app.db.session import force_connection_reset
    print("SUCCESS: force_connection_reset imported successfully")
    print(f"Function: {force_connection_reset}")
except ImportError as e:
    print(f"FAILED: Could not import force_connection_reset - {e}")
except Exception as e:
    print(f"ERROR: Unexpected error during import - {e}")

print("\nAttempting to import reset_database_connections from app.db.session...")

try:
    # Try to import the function directly
    from app.db.session import reset_database_connections
    print("SUCCESS: reset_database_connections imported successfully")
    print(f"Function: {reset_database_connections}")
except ImportError as e:
    print(f"FAILED: Could not import reset_database_connections - {e}")
except Exception as e:
    print(f"ERROR: Unexpected error during import - {e}")

print("\nScript completed.")