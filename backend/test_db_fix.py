#!/usr/bin/env python3
"""
Test script to verify the database connection fixes
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(env_path, override=True)

def test_env_loading():
    """Test that environment variables are loaded correctly"""
    print("Testing environment loading...")
    
    database_url = os.getenv('DATABASE_URL')
    database_url_async = os.getenv('DATABASE_URL_ASYNC')
    
    if database_url:
        print(f"✓ DATABASE_URL loaded: {database_url[:50]}...")
    else:
        print("✗ DATABASE_URL not found")
        return False
        
    if database_url_async:
        print(f"✓ DATABASE_URL_ASYNC loaded: {database_url_async[:50]}...")
    else:
        print("⚠ DATABASE_URL_ASYNC not found, will construct from DATABASE_URL")
        
    return True

async def test_session_import():
    """Test importing and using the session module"""
    print("\nTesting session module import...")
    
    try:
        # Import the session module
        from app.db.session import async_engine, AsyncSessionLocal, reset_database_connections
        
        print("✓ Session module imported successfully")
        
        # Test resetting database connections
        print("Testing database connection reset...")
        reset_result = await reset_database_connections()
        if reset_result:
            print("✓ Database connections reset successfully")
        else:
            print("⚠ Database connection reset failed")
            
        return True
        
    except Exception as e:
        print(f"✗ Session module import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("Database Connection Fix Test")
    print("=" * 30)
    
    # Test environment loading
    if not test_env_loading():
        return False
    
    # Test session import
    if not await test_session_import():
        return False
    
    print("\n" + "=" * 30)
    print("🎉 Test completed! Check results above.")
    return True

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)