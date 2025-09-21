import asyncio
import os
import sys
from dotenv import load_dotenv

# Add backend directory to Python path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

# Load environment variables
env_path = os.path.join(backend_dir, '.env')
load_dotenv(env_path)

async def test_database_connection():
    """Test database connection"""
    try:
        print("Testing database connection...")
        
        # Import database session
        from app.db.session import AsyncSessionLocal, init_db
        
        # Initialize database
        init_db()
        print("✅ Database initialization successful!")
        
        # Try to create a session
        async with AsyncSessionLocal() as session:
            print("✅ Database connection successful!")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting database connection test...")
    result = asyncio.run(test_database_connection())
    if result:
        print("Database test completed successfully!")
    else:
        print("Database test failed!")