#!/usr/bin/env python3
"""
Test script to verify database connection and PgBouncer compatibility
"""

import asyncio
import os
import sys
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_env_configuration():
    """Test environment configuration"""
    print("Testing environment configuration...")
    
    # Load environment variables
    env_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            env_content = f.read()
        print(f"✓ Environment file found at: {env_path}")
    else:
        print("✗ Environment file not found")
        return False
    
    # Check for database URLs
    database_url = os.getenv('DATABASE_URL')
    database_url_async = os.getenv('DATABASE_URL_ASYNC')
    
    if database_url:
        print(f"✓ DATABASE_URL found: {database_url[:50]}...")
    else:
        print("✗ DATABASE_URL not found in environment")
        return False
        
    if database_url_async:
        print(f"✓ DATABASE_URL_ASYNC found: {database_url_async[:50]}...")
    else:
        print("⚠ DATABASE_URL_ASYNC not found, will construct from DATABASE_URL")
        
    # Check if using PgBouncer
    if 'pooler.supabase.com' in database_url:
        print("✓ Using PgBouncer connection")
        if ':6543' in database_url:
            print("✓ Using correct PgBouncer port (6543)")
        else:
            print("⚠ PgBouncer connection should use port 6543")
    else:
        print("⚠ Not using PgBouncer connection")
        
    return True

async def test_async_connection():
    """Test async database connection with PgBouncer compatibility"""
    print("\nTesting async database connection...")
    
    try:
        # Get the async database URL
        database_url_async = os.getenv('DATABASE_URL_ASYNC')
        if not database_url_async:
            database_url = os.getenv('DATABASE_URL')
            if database_url:
                database_url_async = database_url.replace('postgresql://', 'postgresql+asyncpg://')
            else:
                print("✗ No database URL found")
                return False
        
        # Ensure comprehensive PgBouncer compatibility
        final_url = database_url_async
        
        # Remove any existing cache parameters and add correct ones
        if final_url and "?" in final_url:
            base_url, params = final_url.split("?", 1)
            # Ensure params is not None before splitting
            if params:
                # Remove existing cache parameters
                params_list = [p for p in params.split("&") if not (p.startswith("statement_cache_size") or p.startswith("prepared_statement_cache_size"))]
            else:
                params_list = []
            # Add correct cache parameters
            params_list.extend(["statement_cache_size=0", "prepared_statement_cache_size=0"])
            final_url = base_url + "?" + "&".join(params_list)
        elif final_url:
            final_url += "?statement_cache_size=0&prepared_statement_cache_size=0"
                
        # Fix port if needed
        if ":5432/" in final_url:
            final_url = final_url.replace(":5432/", ":6543/")
            
        print(f"Connecting with URL: {final_url[:60]}...")
        
        # Create engine with comprehensive PgBouncer compatibility
        engine = create_async_engine(
            final_url,
            echo=False,
            poolclass=NullPool,
            connect_args={
                "statement_cache_size": 0,
                "prepared_statement_cache_size": 0,
            },
            execution_options={
                "compiled_cache": None,
            }
        )
        
        # Test connection with multiple queries to trigger prepared statements
        async with engine.connect() as conn:
            # First query
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✓ Connected successfully to: {version}")
            
            # Second query - this might trigger prepared statement issues
            result = await conn.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            print(f"✓ Current database: {db_name}")
            
            # Third query - test with parameters
            result = await conn.execute(text("SELECT current_user"))
            user = result.scalar()
            print(f"✓ Current user: {user}")
            
            # Fourth query - test with same query to trigger cache
            result = await conn.execute(text("SELECT version()"))
            version2 = result.scalar()
            print(f"✓ Version query (cached): {version2}")
            
        await engine.dispose()
        print("✓ Async connection test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Async connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sync_connection():
    """Test sync database connection"""
    print("\nTesting sync database connection...")
    
    try:
        from sqlalchemy import create_engine
        
        # Get the database URL
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("✗ No database URL found")
            return False
            
        # Fix port if needed
        if ":5432/" in database_url:
            database_url = database_url.replace(":5432/", ":6543/")
            
        # Replace protocol if needed
        if database_url.startswith('postgresql://'):
            sync_database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://')
        else:
            sync_database_url = database_url
            
        print(f"Connecting with URL: {sync_database_url[:60]}...")
        
        # Create engine
        engine = create_engine(
            sync_database_url,
            echo=False,
            pool_pre_ping=True,
            connect_args={
                'keepalives': 1,
                'keepalives_idle': 30,
                'keepalives_interval': 10,
                'keepalives_count': 5
            }
        )
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✓ Connected successfully to: {version}")
            
        engine.dispose()
        print("✓ Sync connection test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Sync connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("Database Connection and PgBouncer Compatibility Test")
    print("=" * 50)
    
    # Load environment variables
    env_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
    if os.path.exists(env_path):
        import dotenv
        dotenv.load_dotenv(env_path, override=True)
    
    # Test environment configuration
    if not test_env_configuration():
        return False
    
    # Test sync connection
    sync_success = test_sync_connection()
    
    # Test async connection
    async_success = await test_async_connection()
    
    print("\n" + "=" * 50)
    if sync_success and async_success:
        print("🎉 All tests passed! Database connections are working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the output above.")
        return False

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)