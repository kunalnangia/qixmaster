#!/usr/bin/env python3
"""
PgBouncer Diagnostic and Fix Utility
"""
import asyncio
import sys
import os
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def diagnose_pgbouncer_issue():
    """Diagnose and fix PgBouncer prepared statement issues"""
    
    print("[INFO] PgBouncer Diagnostic Tool")
    print("="*50)
    
    try:
        # Check environment
        from dotenv import load_dotenv
        load_dotenv()
        
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            print(f"[INFO] Database URL: {database_url[:50]}...")
            
            # Check if using pgbouncer
            if "pooler.supabase.com" in database_url or "pgbouncer" in database_url.lower():
                print("[WARNING] PgBouncer detected in connection string")
        else:
            print("[WARNING] DATABASE_URL environment variable not set")
            return False
        
        # Import database components
        from app.db.session import async_engine, AsyncSessionLocal
        from sqlalchemy import text
        
        print("\n[1] Testing basic connection...")
        
        # Test basic connection
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            if version:
                print(f"[SUCCESS] Connected to: {version[:50]}...")
            else:
                print("[SUCCESS] Connected to database (version info not available)")
        
        print("\n[2] Testing session creation...")
        
        # Test session creation
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            print("[SUCCESS] Session creation successful")
        
        print("\n[3] Testing prepared statement issue...")
        
        # Test the specific query that's failing
        from app.models.db_models import Project as DBProject
        from sqlalchemy.future import select
        
        try:
            async with AsyncSessionLocal() as session:
                # This is the query that's causing the prepared statement error
                result = await session.execute(select(DBProject).where(DBProject.id == "test-project"))
                project = result.scalars().first()
                print("[SUCCESS] Query executed successfully (no prepared statement error)")
                
                # Try the same query again to see if it triggers the error
                result2 = await session.execute(select(DBProject).where(DBProject.id == "test-project-2"))
                project2 = result2.scalars().first()
                print("[SUCCESS] Second query executed successfully")
                
        except Exception as e:
            if "DuplicatePreparedStatementError" in str(e):
                print("[ERROR] Prepared statement error detected!")
                print("[INFO] Applying advanced fix...")
                
                # Apply the advanced fix
                await apply_advanced_pgbouncer_fix()
                return False
            else:
                raise e
        
        print("\n[4] Testing multiple transactions...")
        
        # Test multiple transactions (this often triggers the issue)
        for i in range(3):
            async with AsyncSessionLocal() as session:
                result = await session.execute(text(f"SELECT {i+1} as test_number"))
                number = result.scalar()
                print(f"[SUCCESS] Transaction {i+1}: {number}")
        
        print("\n[SUCCESS] All tests passed! PgBouncer compatibility is working.")
        return True
        
    except Exception as e:
        print(f"[ERROR] Diagnostic failed: {str(e)}")
        if "DuplicatePreparedStatementError" in str(e):
            print("[INFO] Applying advanced PgBouncer fix...")
            await apply_advanced_pgbouncer_fix()
        return False

async def apply_advanced_pgbouncer_fix():
    """Apply advanced PgBouncer compatibility fixes"""
    
    print("\n[INFO] Applying Advanced PgBouncer Fix")
    print("-"*40)
    
    try:
        # Import and reset connections
        from app.db.session import reset_database_connections
        
        print("1. Disposing existing connections...")
        success = await reset_database_connections()
        
        if success:
            print("[SUCCESS] Advanced fix applied successfully")
            
            # Test the fix
            print("2. Testing the fix...")
            from app.db.session import AsyncSessionLocal
            from sqlalchemy import text
            
            async with AsyncSessionLocal() as session:
                result = await session.execute(text("SELECT 'Fix test successful' as message"))
                message = result.scalar()
                print(f"[SUCCESS] {message}")
                
            return True
        else:
            print("[ERROR] Failed to apply advanced fix")
            return False
            
    except Exception as e:
        print(f"[ERROR] Advanced fix failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("PgBouncer Diagnostic & Fix Utility")
    print(f"Run time: {datetime.now()}")
    print("="*60)
    
    try:
        success = asyncio.run(diagnose_pgbouncer_issue())
        
        if success:
            print("\n[SUCCESS] RESULT: PgBouncer compatibility confirmed!")
            print("[INFO] Your generate test cases button should work now")
        else:
            print("\n[WARNING] RESULT: Issues still need to be resolved")
            print("[INFO] Try restarting the server after running this diagnostic")
            
    except Exception as e:
        print(f"\\n❌ Diagnostic tool failed: {str(e)}")
    
    print("="*60)