import asyncio
import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.append('.')

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

async def test_connection_fix():
    """Test the fixed database connection configuration"""
    try:
        print("🔧 Testing AsyncPG connection with corrected PgBouncer configuration...")
        
        # Import database components
        from app.db.session import async_engine
        from sqlalchemy import text
        
        print("✅ Successfully imported database modules")
        
        # Test basic connection
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT 'Connection successful!' as message"))
            message = result.scalar()
            print(f"✅ Database connection test: {message}")
        
        # Test multiple queries (this was failing before due to prepared statement issues)
        print("🧪 Testing multiple sequential queries...")
        for i in range(3):
            async with async_engine.connect() as conn:
                result = await conn.execute(text(f"SELECT {i+1} as query_number"))
                number = result.scalar()
                print(f"  ✅ Query {i+1}: {number}")
        
        print("\n🎉 All database connection tests passed!")
        print("💡 The AI URL test generation should now work correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {str(e)}")
        import traceback
        print("📋 Error details:")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("="*60)
    print("Testing Fixed PgBouncer Configuration")
    print("="*60)
    
    success = asyncio.run(test_connection_fix())
    
    if success:
        print("\n🎯 SUCCESS: Database configuration is now working correctly!")
        print("🚀 You can now restart the server and test the AI URL generation feature.")
    else:
        print("\n⚠️  The configuration still has issues that need to be resolved.")
    
    print("="*60)