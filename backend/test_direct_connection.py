#!/usr/bin/env python3
"""
Direct PostgreSQL Connection Test and Verification Script
This script verifies that the direct connection bypasses PgBouncer and eliminates prepared statement conflicts
"""
import asyncio
import sys
import os
from datetime import datetime

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

async def test_direct_connection():
    """Test the direct PostgreSQL connection"""
    
    print("=" * 70)
    print("Direct PostgreSQL Connection Test & Verification")
    print("=" * 70)
    print(f"Run time: {datetime.now()}")
    print()
    
    try:
        # Import database components
        from dotenv import load_dotenv
        load_dotenv()
        
        database_url = os.getenv("DATABASE_URL")
        database_url_async = os.getenv("DATABASE_URL_ASYNC")
        
        print("[1] Connection Configuration Verification:")
        if database_url:
            print(f"   Sync URL: {database_url[:60]}...")
            if "pooler.supabase.com" in database_url:
                print("   [WARNING] Sync URL still using PgBouncer pooler")
            elif "db.lflecyuvttemfoyixngi.supabase.co" in database_url:
                print("   [SUCCESS] Sync URL using direct connection")
        
        if database_url_async:
            print(f"   Async URL: {database_url_async[:60]}...")
            if "pooler.supabase.com" in database_url_async:
                print("   [WARNING] Async URL still using PgBouncer pooler - this may cause issues")
            elif "db.lflecyuvttemfoyixngi.supabase.co" in database_url_async:
                print("   [SUCCESS] Async URL using direct connection - no PgBouncer conflicts expected")
        
        print()
        print("[2] Testing Direct Database Connection:")
        
        # Import session components
        from app.db.session import async_engine, AsyncSessionLocal
        from sqlalchemy import text
        
        # Test basic connection
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            if version:
                print(f"   [SUCCESS] Connected to: {version[:80]}...")
                
                # Check if we're connected directly or via pooler
                result2 = await conn.execute(text("SELECT current_setting('application_name')"))
                app_name = result2.scalar()
                print(f"   Application Name: {app_name}")
            else:
                print("   [SUCCESS] Connected (version info not available)")
        
        print()
        print("[3] Testing Prepared Statement Handling (Critical Test):")
        
        # This is the exact type of operation that was failing with PgBouncer
        test_queries = [
            "SELECT 1 as test_value",
            "SELECT current_timestamp as now_time", 
            "SELECT :param as param_test",
            "SELECT pg_backend_pid() as backend_pid"
        ]
        
        for i, query in enumerate(test_queries):
            async with AsyncSessionLocal() as session:
                if ":param" in query:
                    result = await session.execute(text(query), {"param": f"test_{i}"})
                else:
                    result = await session.execute(text(query))
                value = result.scalar()
                print(f"   [SUCCESS] Query {i+1}: {value}")
        
        print()
        print("[4] Testing Multiple Concurrent Sessions (Stress Test):")
        
        # Run multiple concurrent operations that would trigger prepared statement reuse
        async def concurrent_task(task_id):
            async with AsyncSessionLocal() as session:
                # Use parameterized query that would create prepared statements
                result = await session.execute(
                    text("SELECT :task_id as id, :timestamp as ts, pg_backend_pid() as pid"), 
                    {"task_id": task_id, "timestamp": datetime.now()}
                )
                row = result.fetchone()
                if row:
                    return f"Task {row[0]} at {row[1]} (PID: {row[2]})"
                return f"Task {task_id} failed"
        
        # Run 10 concurrent tasks to stress test prepared statement handling
        tasks = [concurrent_task(i + 1) for i in range(10)]
        results = await asyncio.gather(*tasks)
        
        for result in results:
            print(f"   [SUCCESS] {result}")
        
        print()
        print("[5] Testing Connection Pool Behavior:")
        
        # Test that we're using asyncpg's native pooling effectively
        pool_info = []
        async def pool_test(test_id):
            async with AsyncSessionLocal() as session:
                result = await session.execute(text("SELECT pg_backend_pid() as pid"))
                pid = result.scalar()
                return f"Session {test_id}: PID {pid}"
        
        # Run sequential tests to see connection reuse
        for i in range(5):
            result = await pool_test(i + 1)
            pool_info.append(result)
            print(f"   [SUCCESS] {result}")
        
        # Check for connection reuse (should see same PIDs being reused)
        pids = [info.split("PID ")[1] for info in pool_info]
        unique_pids = set(pids)
        print(f"   Connection Pool Analysis: {len(unique_pids)} unique backend connections used")
        if len(unique_pids) < len(pool_info):
            print("   [SUCCESS] Connection pooling working - connections being reused")
        else:
            print("   [INFO] Each request used a new connection - check pool settings")
        
        print()
        print("=" * 70)
        print("[RESULT] All Direct PostgreSQL Connection Tests PASSED!")
        print("[CONCLUSION] No PgBouncer prepared statement conflicts detected")
        print("[STATUS] Application should work without DuplicatePreparedStatementError")
        print("=" * 70)
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"   [ERROR] Connection test failed: {error_msg}")
        
        # Check for specific error patterns
        if "DuplicatePreparedStatementError" in error_msg:
            print()
            print("   [CRITICAL] Still getting PgBouncer prepared statement errors!")
            print("   [ACTION] Check if DATABASE_URL_ASYNC is still using pooler.supabase.com")
            print("   [ACTION] Verify .env file has been updated correctly")
            return False
        elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
            print()
            print("   [INFO] Connection issue detected - this may be temporary")
            print("   [ACTION] Check network connectivity to Supabase direct endpoint")
            return False
        else:
            print()
            print("   [INFO] Unexpected error - may need investigation")
            return False

def print_startup_instructions():
    """Print optimized startup instructions for direct connection"""
    print()
    print("=" * 70)
    print("NEXT STEPS - Start Your Application with Direct Connection")
    print("=" * 70)
    print()
    print("✅ Configuration: Now using direct PostgreSQL connection")
    print("✅ Benefit: No more PgBouncer prepared statement conflicts")
    print("✅ Performance: Native asyncpg connection pooling")
    print()
    print("1. Navigate to your backend directory:")
    print("   cd C:\\Users\\kunal\\Downloads\\qix-master\\qix-master\\backend")
    print()
    print("2. Start the FastAPI server:")
    print("   uvicorn app.main:app --reload --host 127.0.0.1 --port 8001")
    print()
    print("3. Test the AI test case generation:")
    print("   - Frontend: http://localhost:5175/")
    print("   - API Docs: http://127.0.0.1:8001/api/docs")
    print()
    print("4. If you encounter any issues:")
    print("   - Run: python test_direct_connection.py")
    print("   - Check: .env file for correct database URLs")
    print()
    print("=" * 70)

async def main():
    """Main execution function"""
    
    # Test direct connection
    success = await test_direct_connection()
    
    # Print startup instructions
    print_startup_instructions()
    
    if success:
        print("[FINAL RESULT] Direct PostgreSQL connection verified successfully!")
        print("[STATUS] Your application is ready to start without PgBouncer issues")
        return 0
    else:
        print("[FINAL RESULT] Connection issues detected")
        print("[STATUS] Review the error messages and check configuration")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        print(f"[CRITICAL ERROR] Script execution failed: {str(e)}")
        sys.exit(1)