#!/usr/bin/env python3
"""
Tests the database connection with various configurations and timeouts
to ensure stability and proper handling of PgBouncer.
"""

import os
import asyncio
import sys
import traceback
from contextlib import asynccontextmanager
from pathlib import Path

# Add the parent directory to Python path to allow importing from 'app'
# This is a good practice for structured projects.
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Load environment variables from the .env file
from dotenv import load_dotenv
load_dotenv()

# --- Context Manager for Connection with Timeout ---
# This is a good pattern for ensuring connections are closed and
# operations don't hang indefinitely.
@asynccontextmanager
async def get_connection_with_timeout(engine, timeout: float = 30):
    """
    Asynchronously gets a database connection with a specified timeout.

    Args:
        engine: The SQLAlchemy async engine instance.
        timeout: The maximum time in seconds to wait for a connection.

    Yields:
        A database connection object from the engine's pool.
    """
    try:
        # Use asyncio.wait_for to add a timeout to the connection attempt
        conn = await asyncio.wait_for(engine.connect(), timeout=timeout)
        try:
            yield conn
        finally:
            # The 'finally' block ensures the connection is always released
            # back to the pool, even if an error occurs within the 'with' block.
            await conn.close()
    except asyncio.TimeoutError:
        print(f"❌ Connection attempt timed out after {timeout} seconds")
        raise
    except Exception as e:
        print(f"❌ Failed to get database connection: {e}")
        raise

# --- Main Test Function ---
async def test_connection_fix():
    """
    Runs a series of tests to verify the database connection and transaction handling.
    """
    try:
        print("🔧 Testing AsyncPG connection with corrected PgBouncer configuration...")
        
        # Import database components from your application's session module.
        from app.db.session import async_engine, force_connection_reset
        from sqlalchemy import text
        
        print("✅ Successfully imported database modules")
        
        # Reset any existing connections first
        print("🔄 Resetting database connections...")
        await force_connection_reset()
        
        # Test basic connection with timeout
        print("🔌 Testing basic database connection...")
        try:
            async with get_connection_with_timeout(async_engine, timeout=10) as conn:
                result = await conn.execute(text("SELECT 'Connection successful!' as message"))
                message = result.scalar()
                print(f"✅ Database connection test: {message}")
        except Exception as e:
            print(f"❌ Basic connection test failed: {e}")
            return False
        
        # Test multiple queries with individual timeouts
        print("\n🧪 Testing multiple sequential queries...")
        for i in range(3):
            try:
                # Use a smaller timeout for sequential queries to test responsiveness
                async with get_connection_with_timeout(async_engine, timeout=5) as conn:
                    # Use a small sleep to simulate a query taking time
                    query = text(f"SELECT {i+1} as query_number, pg_sleep(0.1) as delay")
                    result = await conn.execute(query)
                    row = result.first()
                    print(f"  ✅ Query {i+1}: {row[0]} (delay: {row[1]}s)")
            except Exception as e:
                print(f"❌ Query {i+1} failed: {e}")
                return False
        
        # Test transaction handling
        print("\n🔀 Testing transaction handling...")
        try:
            async with get_connection_with_timeout(async_engine, timeout=10) as conn:
                async with conn.begin():
                    # A simple transaction test
                    await conn.execute(text("SELECT 1"))
                    print("  ✅ Transaction test passed")
        except Exception as e:
            print(f"❌ Transaction test failed: {e}")
            return False
        
        print("\n🎉 All database connection tests passed!")
        print("💡 The AI URL test generation should now work correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ A critical error occurred during the test: {e}")
        print("\n📋 Error details:")
        traceback.print_exc()
        return False

# --- Entry Point ---
if __name__ == "__main__":
    print("="*60)
    print(f"{'Testing Fixed PgBouncer Configuration':^60}")
    print("="*60)
    
    # Run the async test with proper event loop handling
    import platform
    if platform.system() == 'Windows':
        # Use Windows-specific event loop policy for compatibility
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        success = asyncio.run(test_connection_fix())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        success = False
    
    if success:
        print("\n🎯 SUCCESS: Database configuration is now working correctly!")
        print("🚀 You can now restart the server and test the AI URL generation feature.")
    else:
        print("\n⚠️  The configuration still has issues that need to be resolved.")
    
    print("="*60)
