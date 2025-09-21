#!/usr/bin/env python3
"""
Direct asyncpg test to verify PgBouncer compatibility
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

async def test_direct_asyncpg():
    """Test asyncpg connection directly with PgBouncer compatibility settings"""
    
    # Load environment
    load_dotenv()
    
    # Get database URL
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ No DATABASE_URL found in environment variables")
        return False
    
    # Convert to asyncpg URL
    DATABASE_URL_ASYNC = str(DATABASE_URL).replace("postgresql://", "postgresql+asyncpg://")
    
    print(f"Database URL: {DATABASE_URL_ASYNC}")
    
    try:
        # Import SQLAlchemy
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy.pool import NullPool
        from sqlalchemy import text
        
        # Create engine with explicit connect_args
        engine = create_async_engine(
            DATABASE_URL_ASYNC,
            echo=True,  # Enable logging to see what's happening
            poolclass=NullPool,
            connect_args={
                "statement_cache_size": 0,
                "prepared_statement_cache_size": 0,
            },
            execution_options={
                "compiled_cache": None,
            }
        )
        
        print("✅ Engine created successfully")
        
        # Test connection
        async with engine.connect() as conn:
            print("✅ Database connection successful")
            
            # Test multiple queries to trigger prepared statements
            for i in range(3):
                result = await conn.execute(text(f"SELECT 'Test {i}' as message"))
                row = result.fetchone()
                print(f"✅ Query {i+1} successful: {row}")
            
        print("\n🎉 All tests passed! Direct asyncpg connection with PgBouncer compatibility is working.")
        return True
        
    except Exception as e:
        print(f"❌ Direct asyncpg test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_direct_asyncpg())
    sys.exit(0 if success else 1)