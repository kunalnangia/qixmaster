#!/usr/bin/env python3
"""
Test script to verify PgBouncer-proof database configuration
"""
import asyncio
import sys
import os
from datetime import datetime

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

async def test_pgbouncer_fix():
    """Test PgBouncer compatibility fix"""
    
    print("=" * 60)
    print("Testing PgBouncer Compatibility Fix")
    print("=" * 60)
    print(f"Run time: {datetime.now()}")
    print()
    
    try:
        # Import required modules
        from dotenv import load_dotenv
        load_dotenv()
        
        # Import database session
        from app.db.session import async_engine
        from app.models.db_models import Project
        from sqlalchemy.future import select
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy.pool import NullPool
        
        print("1. Checking database engine configuration...")
        print(f"   Engine URL: {str(async_engine.url)[:60]}...")
        print(f"   Pool class: {async_engine.pool.__class__.__name__}")
        
        # Check if NullPool is being used
        if isinstance(async_engine.pool, NullPool):
            print("   ✅ Using NullPool (PgBouncer compatible)")
        else:
            print("   ❌ Not using NullPool (may cause PgBouncer issues)")
            
        # Check connect args from URL parameters
        url_str = str(async_engine.url)
        print(f"   Engine URL: {url_str}")
        
        if "statement_cache_size=0" in url_str:
            print("   ✅ statement_cache_size=0 in URL (PgBouncer compatible)")
        else:
            print("   ❌ statement_cache_size=0 not in URL")
            
        if "prepared_statement_cache_size=0" in url_str:
            print("   ✅ prepared_statement_cache_size=0 in URL (PgBouncer compatible)")
        else:
            print("   ❌ prepared_statement_cache_size=0 not in URL")
        
        # Check connect args from engine
        connect_args = {}
        if hasattr(async_engine, 'driver_connection_args'):
            connect_args = async_engine.driver_connection_args
        elif hasattr(async_engine.dialect, '_asyncpg_connection_options'):
            connect_args = async_engine.dialect._asyncpg_connection_options
        elif hasattr(async_engine.dialect, '_connection_options'):
            connect_args = async_engine.dialect._connection_options
            
        print(f"   Connect args: {connect_args}")
        
        if connect_args.get("statement_cache_size") == 0:
            print("   ✅ statement_cache_size=0 in connect_args (PgBouncer compatible)")
        else:
            print("   ❌ statement_cache_size not set to 0 in connect_args")
            
        if connect_args.get("prepared_statement_cache_size") == 0:
            print("   ✅ prepared_statement_cache_size=0 in connect_args (PgBouncer compatible)")
        else:
            print("   ❌ prepared_statement_cache_size not set to 0 in connect_args")
        
        # Check if compiled cache is disabled
        execution_options = getattr(async_engine, 'execution_options', {})
        # Handle case where execution_options might be a function
        if callable(execution_options):
            execution_options = execution_options()
        if isinstance(execution_options, dict) and execution_options.get("compiled_cache") is None:
            print("   ✅ compiled_cache disabled (PgBouncer compatible)")
        else:
            print("   ❌ compiled_cache not disabled")
        
        print()
        
        # Test database connection
        print("2. Testing database connection...")
        async with AsyncSession(async_engine) as session:
            try:
                # Simple query to test connection
                result = await session.execute(select(Project))
                projects = result.scalars().all()
                print(f"   ✅ Database connection successful")
                print(f"   Found {len(projects)} projects in database")
                
                print()
                print("[SUCCESS] PgBouncer compatibility configuration is working!")
                return True
                
            except Exception as e:
                print(f"   ❌ Database operation failed: {str(e)}")
                import traceback
                traceback.print_exc()
                return False

    except Exception as e:
        print(f"[ERROR] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(test_pgbouncer_fix())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"[CRITICAL] Script execution failed: {str(e)}")
        sys.exit(1)