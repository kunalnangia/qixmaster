#!/usr/bin/env python3
"""
Minimal test to reproduce the asyncpg connection error
"""

import os
import asyncio
import certifi
import traceback
import ssl as ssl_lib
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

async def test_asyncpg_direct():
    """Test asyncpg connection directly"""
    try:
        import asyncpg
        DATABASE_URL_ASYNC = os.getenv("DATABASE_URL_ASYNC") 
        print(f"Database URL: {DATABASE_URL_ASYNC}")
        
        print("\nTesting direct asyncpg connection...")

        # Keep the DSN with parameters for direct asyncpg connection
        clean_dsn = DATABASE_URL_ASYNC.replace("postgresql+asyncpg://", "postgresql://")
        print(f"Cleaned DSN: {clean_dsn}")

        parsed = urlparse(DATABASE_URL_ASYNC)

        print(f"Parsed URL:")
        print(f"  Host: {parsed.hostname}")
        print(f"  Port: {parsed.port}")
        print(f"  Database: {parsed.path.lstrip('/')}")
        print(f"  Username: {parsed.username}")
        print(f"  Password: {'***' if parsed.password else None}")

        print("\nTesting direct asyncpg connection...")
        
        # asyncpg handles sslmode in the DSN directly, so this should pass
        connection = await asyncpg.connect(clean_dsn)
        
        result = await connection.fetchrow("SELECT 1 as test")
        print(f"✅ Direct asyncpg connection successful: {result}")
        
        await connection.close()
        
    except Exception as e:
        print(f"❌ Direct asyncpg connection failed: {e}")
        print("Full traceback:")
        traceback.print_exc()
        raise

async def test_sqlalchemy_asyncpg():
    """Test SQLAlchemy with asyncpg"""
    try:
        DATABASE_URL_ASYNC = os.getenv("DATABASE_URL_ASYNC")
        
        # FIX: Strip all parameters from the URL string
        connection_string = DATABASE_URL_ASYNC.split('?')[0]

        print(f"\nTesting SQLAlchemy with asyncpg...")
        print(f"Connection string: {connection_string}")
        
        engine = create_async_engine(
            connection_string,
            echo=False,
            connect_args={
                # asyncpg does not use sslmode, so we map it to ssl=False
                "ssl": False,
                "statement_cache_size": 0,
            }
        )
        
        print("✅ Engine created successfully")
        
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            print(f"✅ SQLAlchemy asyncpg connection successful: {row}")
            
    except Exception as e:
        print(f"❌ SQLAlchemy asyncpg connection failed: {e}")
        print("Full traceback:")
        traceback.print_exc()

async def test_with_statement_cache():
    """Test with the statement_cache_size parameter"""
    try:
        DATABASE_URL_ASYNC = os.getenv("DATABASE_URL_ASYNC")
        
        # FIX: Clean the connection string of all parameters
        connection_string = DATABASE_URL_ASYNC.split('?')[0]

        print(f"\nTesting SQLAlchemy with statement_cache_size=0...")
        print(f"Connection string: {connection_string}")
        
        # FIX: Pass all parameters via connect_args
        engine = create_async_engine(
            connection_string,
            echo=False,
            connect_args={
                "ssl": False,
                "statement_cache_size": 0
            }
        )
        
        print("✅ Engine with statement_cache_size created successfully")
        
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            print(f"✅ Connection with statement_cache_size successful: {row}")
            
    except Exception as e:
        print(f"❌ Connection with statement_cache_size failed: {e}")
        print("Full traceback:")
        traceback.print_exc()

async def test_with_additional_params():
    """Test with additional connection parameters that might cause the issue"""
    
    test_params = {
        "?statement_cache_size=0": {"statement_cache_size": 0},
        "?statement_cache_size=0&pool_size=5": {"pool_size": 5, "statement_cache_size": 0},
        "?keepalives=1": {},
        "?keepalives_idle=30": {},
    }
    
    for params_str, connect_args in test_params.items():
        try:
            DATABASE_URL_ASYNC = os.getenv("DATABASE_URL_ASYNC")
            base_url = DATABASE_URL_ASYNC.split('?')[0]
            
            # Use the base URL for the engine
            connection_string = base_url
            
            # Separate SQLAlchemy engine params from connect_args
            engine_args = {}
            driver_args = {"ssl": False}
            
            if "pool_size" in connect_args:
                engine_args["pool_size"] = connect_args.pop("pool_size")
            if "statement_cache_size" in connect_args:
                driver_args["statement_cache_size"] = connect_args.pop("statement_cache_size")

            engine = create_async_engine(
                connection_string,
                echo=False,
                connect_args=driver_args,
                **engine_args
            )
            
            async with engine.connect() as conn:
                result = await conn.execute(text("SELECT 1"))
                print(f"✅ Success with {params_str}")
                await engine.dispose()

        except Exception as e:
            print(f"❌ Failed with {params_str}: {e}")
            traceback.print_exc()
            
if __name__ == "__main__":
    print("🔍 Testing asyncpg connection configurations...")
    
    asyncio.run(test_asyncpg_direct())
    asyncio.run(test_sqlalchemy_asyncpg())
    asyncio.run(test_with_statement_cache())
    asyncio.run(test_with_additional_params())
    
    print("\n=== All Tests Complete ===")