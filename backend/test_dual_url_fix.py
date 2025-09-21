#!/usr/bin/env python3
"""
Test script to verify dual URL approach fixes the psycopg2/asyncpg compatibility issue
"""
import asyncio
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_environment_config():
    """Test that environment variables are properly configured"""
    
    print("🔍 Testing Environment Configuration")
    print("="*45)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    database_url = os.getenv("DATABASE_URL")
    database_url_async = os.getenv("DATABASE_URL_ASYNC")
    
    print(f"📊 DATABASE_URL (sync): {database_url[:70] if database_url else 'NOT SET'}...")
    print(f"📊 DATABASE_URL_ASYNC: {database_url_async[:70] if database_url_async else 'NOT SET'}...")
    
    # Check if URLs are different drivers
    sync_driver = "psycopg2" if database_url and "postgresql://" in database_url else "unknown"
    async_driver = "asyncpg" if database_url_async and "+asyncpg" in database_url_async else "unknown"
    
    print(f"🔧 Sync driver: {sync_driver}")
    print(f"🔧 Async driver: {async_driver}")
    
    # Check for statement_cache_size in async URL only
    has_cache_param = "statement_cache_size=0" in (database_url_async or "")
    print(f"🔧 AsyncPG cache disabled: {'✅ YES' if has_cache_param else '❌ NO'}")
    
    return bool(database_url and database_url_async and has_cache_param)

def test_sync_engine():
    """Test sync engine (should work with standard psycopg2)"""
    
    print("\\n🧪 Testing Sync Engine (psycopg2)")
    print("-"*35)
    
    try:
        from app.db.session import engine
        from sqlalchemy import text
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 'Sync connection successful' as message"))
            message = result.scalar()
            print(f"✅ {message}")
            return True
            
    except Exception as e:
        print(f"❌ Sync engine error: {str(e)}")
        return False

async def test_async_engine():
    """Test async engine (should work with AsyncPG + PgBouncer settings)"""
    
    print("\\n🧪 Testing Async Engine (AsyncPG)")
    print("-"*35)
    
    try:
        from app.db.session import async_engine, AsyncSessionLocal
        from sqlalchemy import text
        
        # Test 1: Basic async connection
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT 'Async connection successful' as message"))
            message = result.scalar()
            print(f"✅ {message}")
        
        # Test 2: Session-based query (the problematic case)
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 'Session query successful' as message"))
            message = result.scalar()
            print(f"✅ {message}")
        
        # Test 3: Multiple queries to test prepared statement handling
        for i in range(3):
            async with AsyncSessionLocal() as session:
                result = await session.execute(text(f"SELECT 'Query {i+1} successful' as message"))
                message = result.scalar()
                print(f"✅ {message}")
        
        return True
        
    except Exception as e:
        print(f"❌ Async engine error: {str(e)}")
        if "DuplicatePreparedStatementError" in str(e):
            print("🔧 ISSUE: PgBouncer prepared statement error still present")
        elif "statement_cache_size" in str(e):
            print("🔧 ISSUE: statement_cache_size parameter problem")
        return False

async def main():
    """Run all tests"""
    
    print("🔧 Database Driver Compatibility Test")
    print("="*50)
    
    # Test 1: Environment configuration
    env_ok = test_environment_config()
    
    # Test 2: Sync engine
    sync_ok = test_sync_engine()
    
    # Test 3: Async engine  
    async_ok = await test_async_engine()
    
    # Summary
    print("\\n📋 TEST RESULTS")
    print("="*20)
    print(f"Environment Config: {'✅ PASS' if env_ok else '❌ FAIL'}")
    print(f"Sync Engine (psycopg2): {'✅ PASS' if sync_ok else '❌ FAIL'}")
    print(f"Async Engine (AsyncPG): {'✅ PASS' if async_ok else '❌ FAIL'}")
    
    if env_ok and sync_ok and async_ok:
        print("\\n🎉 SUCCESS: All database connections working!")
        print("💡 The backend should now start without driver compatibility errors")
        return True
    else:
        print("\\n⚠️ ISSUES: Some tests failed")
        if not env_ok:
            print("   - Check .env file configuration")
        if not sync_ok:
            print("   - Sync engine has connection issues")
        if not async_ok:
            print("   - Async engine has PgBouncer compatibility issues")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\\n⛔ Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\\n❌ Test failed: {str(e)}")
        sys.exit(1)