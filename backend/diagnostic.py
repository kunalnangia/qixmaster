#!/usr/bin/env python3
"""
Diagnostic script to check database URL construction
"""
import os
import sys
from dotenv import load_dotenv

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

def check_urls():
    """Check how the database URLs are constructed"""
    
    # Load environment
    load_dotenv()
    
    # Get database URLs
    DATABASE_URL = os.getenv("DATABASE_URL")
    DATABASE_URL_ASYNC = os.getenv("DATABASE_URL_ASYNC")
    
    print("Database URL Diagnostic")
    print("=" * 30)
    print(f"DATABASE_URL: {DATABASE_URL}")
    print(f"DATABASE_URL_ASYNC: {DATABASE_URL_ASYNC}")
    
    # Check if async URL is constructed properly
    if not DATABASE_URL_ASYNC:
        print("Constructing async URL from sync URL...")
        if DATABASE_URL:
            DATABASE_URL_ASYNC = str(DATABASE_URL).replace("postgresql://", "postgresql+asyncpg://")
            print(f"Constructed DATABASE_URL_ASYNC: {DATABASE_URL_ASYNC}")
        else:
            print("❌ No DATABASE_URL found!")
            return False
    
    # Check for PgBouncer parameters
    pgbouncer_params = [
        "statement_cache_size=0",
        "prepared_statement_cache_size=0"
    ]
    
    print("\nChecking PgBouncer parameters:")
    for param in pgbouncer_params:
        if param in DATABASE_URL_ASYNC:
            print(f"✅ {param} found in DATABASE_URL_ASYNC")
        else:
            print(f"❌ {param} NOT found in DATABASE_URL_ASYNC")
            
        if DATABASE_URL and param in DATABASE_URL:
            print(f"✅ {param} found in DATABASE_URL")
        elif DATABASE_URL:
            print(f"❌ {param} NOT found in DATABASE_URL")
        else:
            print(f"❌ DATABASE_URL not available to check {param}")
    
    return True

if __name__ == "__main__":
    check_urls()