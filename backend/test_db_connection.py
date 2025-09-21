#!/usr/bin/env python3
"""
Simple database connectivity test for Supabase
"""
import os
import sys
from dotenv import load_dotenv
import psycopg2
import asyncpg
import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_database_connection():
    """Test the database connection directly"""
    # Using the async URL from your .env file
    DATABASE_URL_ASYNC = "postgresql+asyncpg://postgres.lflecyuvttemfoyixngi:Ayeshaayesha121@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres?statement_cache_size=0&prepared_statement_cache_size=0"
    
    try:
        logger.info("Creating async engine...")
        engine = create_async_engine(DATABASE_URL_ASYNC)
        
        logger.info("Attempting to connect to database...")
        async with engine.connect() as conn:
            # Simple query to test connection
            result = await conn.execute(text("SELECT 1"))
            logger.info(f"Database connection successful: {result.fetchone()}")
            
        await engine.dispose()
        logger.info("Database test completed successfully")
        
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

def test_sync_connection():
    """Test synchronous database connection"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ Sync connection failed: DATABASE_URL environment variable not set")
        return False
        
    print(f"Testing sync connection to: {database_url}")
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Sync connection successful!")
        if version:
            print(f"Database version: {version[0]}")
        else:
            print("Database version: Unable to retrieve version")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Sync connection failed: {e}")
        return False

async def test_async_connection():
    """Test asynchronous database connection"""
    database_url_async = os.getenv('DATABASE_URL_ASYNC')
    
    if not database_url_async:
        print("❌ Async connection failed: DATABASE_URL_ASYNC environment variable not set")
        return False
    
    # Remove the postgresql+asyncpg:// prefix for asyncpg
    if database_url_async.startswith('postgresql+asyncpg://'):
        database_url_async = database_url_async.replace('postgresql+asyncpg://', 'postgresql://')
    
    print(f"Testing async connection to: {database_url_async}")
    
    try:
        conn = await asyncpg.connect(database_url_async)
        version = await conn.fetchval("SELECT version();")
        print(f"✅ Async connection successful!")
        print(f"Database version: {version}")
        await conn.close()
        return True
    except Exception as e:
        print(f"❌ Async connection failed: {e}")
        return False

def main():
    print("🔍 Testing Supabase Database Connectivity")
    print("=" * 50)
    
    print("\n1. Testing Synchronous Connection...")
    sync_success = test_sync_connection()
    
    print("\n2. Testing Asynchronous Connection...")
    try:
        async_success = asyncio.run(test_async_connection())
    except Exception as e:
        print(f"❌ Async test failed with error: {e}")
        async_success = False
    
    print("\n" + "=" * 50)
    print("📋 Summary:")
    print(f"Sync Connection: {'✅ PASS' if sync_success else '❌ FAIL'}")
    print(f"Async Connection: {'✅ PASS' if async_success else '❌ FAIL'}")
    
    if sync_success and async_success:
        print("\n🎉 All database connections are working!")
        print("You can now restart the backend server.")
        return True
    else:
        print("\n⚠️  Database connection issues detected.")
        print("Please check your network connection and Supabase project status.")
        return False

if __name__ == "__main__":
    asyncio.run(test_database_connection())
    success = main()
    sys.exit(0 if success else 1)