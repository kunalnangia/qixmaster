#!/usr/bin/env python3
"""
Final test to verify PgBouncer compatibility with the actual application setup
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

async def test_actual_setup():
    """Test using the actual application setup"""
    
    # Load environment
    load_dotenv()
    
    try:
        # Import the actual session setup
        from app.db.session import async_engine
        from sqlalchemy import text
        
        print("Testing Actual Application Setup")
        print("=" * 40)
        print(f"Engine URL: {async_engine.url}")
        
        # Test connection using the same approach as the application
        async with async_engine.connect() as conn:
            print("✅ Database connection successful")
            
            # Test multiple queries to trigger prepared statements
            for i in range(3):
                result = await conn.execute(text(f"SELECT 'Test {i}' as message"))
                row = result.fetchone()
                print(f"✅ Query {i+1} successful: {row}")
                
                # Add a small delay to ensure proper connection handling
                await asyncio.sleep(0.1)
            
        print("\n🎉 All tests passed! Actual application setup is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_actual_setup())
    sys.exit(0 if success else 1)