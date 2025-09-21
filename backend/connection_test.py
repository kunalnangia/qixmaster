#!/usr/bin/env python3
"""
Simple database connection test to verify PgBouncer compatibility
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

async def test_database_connection():
    """Test the database connection with PgBouncer compatibility"""
    
    # Load environment
    load_dotenv()
    
    # Import after loading environment
    from app.db.session import async_engine
    from sqlalchemy import text
    
    print("Testing Database Connection with PgBouncer Compatibility")
    print("=" * 60)
    
    try:
        # Test a simple connection and query
        print("Attempting to connect to database...")
        async with async_engine.connect() as conn:
            print("✅ Database connection successful")
            
            # Test a simple query
            result = await conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            print(f"✅ Simple query successful: {row}")
            
            # Test another query to make sure prepared statements work
            result = await conn.execute(text("SELECT 'PgBouncer test' as message"))
            row = result.fetchone()
            print(f"✅ Second query successful: {row}")
            
        print("\n🎉 All database tests passed! PgBouncer configuration is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_database_connection())
    sys.exit(0 if success else 1)