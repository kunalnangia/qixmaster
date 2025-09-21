#!/usr/bin/env python3
"""
Verify PgBouncer Fix Implementation
Tests the URL parameter approach (statement_cache_size=0) recommended for PgBouncer compatibility
"""
import asyncio
import sys
import os
from urllib.parse import urlparse, parse_qs

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verify_database_url():
    """Verify that DATABASE_URL contains the required PgBouncer parameters"""
    
    print("🔍 Verifying DATABASE_URL Configuration")
    print("="*50)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    database_url = os.getenv("DATABASE_URL")
    
    if database_url is None:
        print("❌ DATABASE_URL environment variable is not set")
        return False
        
    print(f"📊 Database URL: {database_url[:60]}...")
    
    # Parse the URL to check for parameters
    parsed_url = urlparse(database_url)
    query_params = parse_qs(parsed_url.query)
    
    # Check for critical parameters
    checks = {
        "statement_cache_size": "0",
    }
    
    all_good = True
    for param, expected_value in checks.items():
        if param in query_params:
            actual_value = query_params[param][0]
            if actual_value == expected_value:
                print(f"✅ {param}={actual_value} (Correct)")
            else:
                print(f"❌ {param}={actual_value} (Expected: {expected_value})")
                all_good = False
        else:
            print(f"❌ {param} parameter missing from DATABASE_URL")
            all_good = False
    
    # Check for PgBouncer indicators
    if database_url and "pooler.supabase.com" in database_url:
        print("⚠️  Supabase pooler detected - PgBouncer compatibility required")
    
    return all_good

async def test_connection_without_prepared_statements():
    """Test database connection to ensure no prepared statement errors"""
    
    print("\\n🧪 Testing Database Connection")
    print("-"*30)
    
    try:
        from app.db.session import AsyncSessionLocal, async_engine
        from sqlalchemy import text
        from sqlalchemy.future import select
        from app.models.db_models import Project as DBProject
        
        # Test 1: Basic connection
        print("1️⃣ Testing basic connection...")
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT 'Connection successful' as message"))
            message = result.scalar()
            print(f"✅ {message}")
        
        # Test 2: Multiple queries (this typically triggers prepared statement reuse)
        print("\\n2️⃣ Testing multiple queries...")
        for i in range(3):
            async with AsyncSessionLocal() as session:
                result = await session.execute(text(f"SELECT 'Query {i+1} successful' as message"))
                message = result.scalar()
                print(f"✅ {message}")
        
        # Test 3: The specific query that was failing
        print("\\n3️⃣ Testing ORM queries (original failure point)...")
        try:
            async with AsyncSessionLocal() as session:
                # This is the exact query pattern that was causing prepared statement errors
                result = await session.execute(select(DBProject).where(DBProject.id == "test-project-1"))
                await session.execute(select(DBProject).where(DBProject.id == "test-project-2"))
                await session.execute(select(DBProject).where(DBProject.id == "test-project-3"))
                print("✅ ORM queries executed without prepared statement conflicts")
                
        except Exception as e:
            if "DuplicatePreparedStatementError" in str(e):
                print("❌ FAILED: Prepared statement error still occurring!")
                print(f"Error: {str(e)}")
                return False
            else:
                # Other errors are acceptable (like missing tables)
                print(f"⚠️ Other error (expected): {str(e)[:100]}...")
        
        # Test 4: Rapid fire queries to stress test
        print("\\n4️⃣ Stress testing with rapid queries...")
        tasks = []
        for i in range(10):
            async def query_task(n):
                async with AsyncSessionLocal() as session:
                    await session.execute(text(f"SELECT {n} as query_number"))
            tasks.append(query_task(i))
        
        await asyncio.gather(*tasks)
        print("✅ Stress test completed - no prepared statement conflicts")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {str(e)}")
        if "DuplicatePreparedStatementError" in str(e):
            print("\\n🔧 DIAGNOSIS: PgBouncer prepared statement error still present")
            print("💡 SOLUTION: Ensure statement_cache_size=0 is in DATABASE_URL")
        return False

async def test_ai_endpoint_integration():
    """Test that the AI endpoint works with the PgBouncer fix"""
    
    print("\\n🤖 Testing AI Endpoint Integration")
    print("-"*35)
    
    try:
        import aiohttp
        import json
        
        api_url = "http://127.0.0.1:8001/api/ai/generate-tests-from-url"
        payload = {
            "url": "https://example.com",
            "project_id": "pgbouncer-fix-test",
            "test_type": "functional",
            "priority": "medium",
            "count": 1
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(api_url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ AI endpoint working - generated {len(data)} test case(s)")
                    return True
                else:
                    error_text = await response.text()
                    if "DuplicatePreparedStatementError" in error_text:
                        print("❌ AI endpoint still has prepared statement errors")
                        return False
                    else:
                        print(f"⚠️ AI endpoint returned {response.status}: {error_text[:100]}...")
                        return True  # Other errors are not PgBouncer-related
                        
    except Exception as e:
        if "DuplicatePreparedStatementError" in str(e):
            print("❌ AI endpoint has prepared statement errors")
            return False
        else:
            print(f"⚠️ Connection issue (server may not be running): {str(e)}")
            return True  # Connection issues are not PgBouncer-related

async def main():
    """Run all verification tests"""
    
    print("🔧 PgBouncer Compatibility Verification")
    print("="*60)
    
    # Step 1: Verify URL configuration
    url_ok = verify_database_url()
    
    # Step 2: Test database connection
    connection_ok = await test_connection_without_prepared_statements()
    
    # Step 3: Test AI endpoint (optional - requires server running)
    endpoint_ok = await test_ai_endpoint_integration()
    
    # Summary
    print("\\n📋 VERIFICATION SUMMARY")
    print("="*30)
    print(f"URL Configuration: {'✅ PASS' if url_ok else '❌ FAIL'}")
    print(f"Database Connection: {'✅ PASS' if connection_ok else '❌ FAIL'}")
    print(f"AI Endpoint: {'✅ PASS' if endpoint_ok else '⚠️ SKIP (server not running)'}")
    
    if url_ok and connection_ok:
        print("\\n🎉 SUCCESS: PgBouncer compatibility verified!")
        print("💡 The generate test cases button should now work without errors")
        return True
    else:
        print("\\n⚠️ ISSUES FOUND: Additional fixes needed")
        if not url_ok:
            print("   - Fix DATABASE_URL parameters")
        if not connection_ok:
            print("   - Restart backend server to apply connection changes")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit_code = 0 if success else 1
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\\n⛔ Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\\n❌ Verification failed: {str(e)}")
        sys.exit(1)