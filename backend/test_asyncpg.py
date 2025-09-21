#!/usr/bin/env python3
"""
Minimal test to reproduce the asyncpg connection error
"""

import os
import asyncio
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_asyncpg_direct():
    """Test asyncpg connection directly"""
    
    try:
        import asyncpg
        
        DATABASE_URL = os.getenv("DATABASE_URL")
        print(f"Database URL: {DATABASE_URL}")
        
        # Parse the URL manually
        from urllib.parse import urlparse
        parsed = urlparse(DATABASE_URL)
        
        print(f"Parsed URL:")
        print(f"  Host: {parsed.hostname}")
        print(f"  Port: {parsed.port}")
        print(f"  Database: {parsed.path.lstrip('/')}")
        print(f"  Username: {parsed.username}")
        print(f"  Password: {'***' if parsed.password else None}")
        
        # Try to connect with asyncpg directly
        print("\nTesting direct asyncpg connection...")
        
        connection = await asyncpg.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path.lstrip('/'),
            user=parsed.username,
            password=parsed.password,
        )
        
        # Test a simple query
        result = await connection.fetchrow("SELECT 1 as test")
        print(f"✅ Direct asyncpg connection successful: {result}")
        
        await connection.close()
        
    except Exception as e:
        print(f"❌ Direct asyncpg connection failed: {e}")
        print("Full traceback:")
        traceback.print_exc()

async def test_sqlalchemy_asyncpg():
    """Test SQLAlchemy with asyncpg"""
    
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        
        DATABASE_URL = os.getenv("DATABASE_URL")
        
        # Convert to asyncpg URL
        connection_string = str(DATABASE_URL).replace("postgresql://", "postgresql+asyncpg://")
        
        print(f"\nTesting SQLAlchemy with asyncpg...")
        print(f"Connection string: {connection_string}")
        
        # Try creating the engine
        engine = create_async_engine(
            connection_string,
            echo=False  # Disable echo to reduce noise
        )
        
        print("✅ Engine created successfully")
        
        # Try to connect
        async with engine.connect() as conn:
            result = await conn.execute("SELECT 1 as test")
            row = result.fetchone()
            print(f"✅ SQLAlchemy asyncpg connection successful: {row}")
            
    except Exception as e:
        print(f"❌ SQLAlchemy asyncpg connection failed: {e}")
        print("Full traceback:")
        traceback.print_exc()

async def test_with_statement_cache():
    """Test with the statement_cache_size parameter"""
    
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        
        DATABASE_URL = os.getenv("DATABASE_URL")
        
        # Convert to asyncpg URL and add statement_cache_size
        connection_string = str(DATABASE_URL).replace("postgresql://", "postgresql+asyncpg://")
        connection_string += "?statement_cache_size=0"
        
        print(f"\nTesting SQLAlchemy with statement_cache_size=0...")
        print(f"Connection string: {connection_string}")
        
        # Try creating the engine
        engine = create_async_engine(
            connection_string,
            echo=False
        )
        
        print("✅ Engine with statement_cache_size created successfully")
        
        # Try to connect
        async with engine.connect() as conn:
            result = await conn.execute("SELECT 1 as test")
            row = result.fetchone()
            print(f"✅ Connection with statement_cache_size successful: {row}")
            
    except Exception as e:
        print(f"❌ Connection with statement_cache_size failed: {e}")
        print("Full traceback:")
        traceback.print_exc()

async def test_with_additional_params():
    """Test with additional connection parameters that might cause the issue"""
    
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        
        DATABASE_URL = os.getenv("DATABASE_URL")
        
        # Convert to asyncpg URL and add various parameters
        connection_string = str(DATABASE_URL).replace("postgresql://", "postgresql+asyncpg://")
        
        # Test different parameters that might cause issues
        test_params = [
            "?statement_cache_size=0",
            "?statement_cache_size=0&pool_size=5",
            "?statement_cache_size=0&pool_size=5&pool_timeout=30",
            "?keepalives=1",  # This might cause the issue
            "?keepalives_idle=30",  # This might cause the issue
        ]
        
        for params in test_params:
            test_string = connection_string + params
            print(f"\nTesting with params: {params}")
            
            try:
                engine = create_async_engine(test_string, echo=False)
                async with engine.connect() as conn:
                    result = await conn.execute("SELECT 1")
                    print(f"✅ Success with {params}")
            except Exception as e:
                print(f"❌ Failed with {params}: {e}")
                if "'<' not supported between instances of 'str' and 'int'" in str(e):
                    print("🎯 FOUND THE PROBLEMATIC PARAMETER!")
                    return params
                    
    except Exception as e:
        print(f"❌ Test with additional params failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print("🔍 Testing asyncpg connection configurations...")
    
    # Run the tests
    asyncio.run(test_asyncpg_direct())
    asyncio.run(test_sqlalchemy_asyncpg())
    asyncio.run(test_with_statement_cache())
    asyncio.run(test_with_additional_params())
    
    print("\n=== All Tests Complete ===")