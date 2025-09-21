#!/usr/bin/env python3
"""
Simple test to verify PgBouncer compatibility configuration
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

async def test_configuration():
    """Test the PgBouncer configuration"""
    
    # Load environment
    load_dotenv()
    
    # Import after loading environment
    from app.db.session import async_engine
    
    print("Testing PgBouncer Configuration")
    print("=" * 40)
    
    # Check engine configuration
    print(f"Engine URL: {async_engine.url}")
    print(f"Pool class: {async_engine.pool.__class__.__name__}")
    
    # Check if NullPool is being used
    from sqlalchemy.pool import NullPool
    if isinstance(async_engine.pool, NullPool):
        print("✅ Using NullPool (PgBouncer compatible)")
    else:
        print("❌ Not using NullPool (may cause PgBouncer issues)")
    
    # Check connect args in URL
    url_str = str(async_engine.url)
    if "statement_cache_size=0" in url_str:
        print("✅ statement_cache_size=0 in URL (PgBouncer compatible)")
    else:
        print("❌ statement_cache_size=0 not in URL")
        
    if "prepared_statement_cache_size=0" in url_str:
        print("✅ prepared_statement_cache_size=0 in URL (PgBouncer compatible)")
    else:
        print("❌ prepared_statement_cache_size=0 not in URL")
    
    # Check execution options
    # The execution_options might be accessed differently depending on SQLAlchemy version
    execution_options = getattr(async_engine, 'execution_options', {})
    
    # Try different ways to access execution options
    if callable(execution_options):
        try:
            execution_options = execution_options()
        except:
            execution_options = {}
    
    # Check if it's a property or attribute
    if hasattr(async_engine, '_execution_options'):
        engine_execution_options = getattr(async_engine, '_execution_options', {})
        if isinstance(engine_execution_options, dict):
            execution_options = engine_execution_options
    
    print(f"Execution options: {execution_options}")
    
    # Check if compiled_cache is disabled
    compiled_cache_disabled = False
    if isinstance(execution_options, dict):
        compiled_cache_value = execution_options.get("compiled_cache")
        if compiled_cache_value is None:
            compiled_cache_disabled = True
    
    if compiled_cache_disabled:
        print("✅ compiled_cache disabled (PgBouncer compatible)")
    else:
        print("ℹ️  compiled_cache status: Check if this is causing issues")
        print("   Note: In some SQLAlchemy versions, this might be handled differently")
    
    print("\nConfiguration check complete!")

if __name__ == "__main__":
    asyncio.run(test_configuration())