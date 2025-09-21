import asyncio
import logging
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(env_path, override=True)

async def test_database_connection():
    """Test the database connection directly"""
    # Using the async URL from your .env file
    DATABASE_URL_ASYNC = os.getenv("DATABASE_URL_ASYNC")
    
    if not DATABASE_URL_ASYNC:
        logger.error("DATABASE_URL_ASYNC environment variable not set")
        return
    
    try:
        logger.info("Creating async engine...")
        # Create engine with proper parameter types
        engine = create_async_engine(
            DATABASE_URL_ASYNC,
            echo=False,
            connect_args={
                "statement_cache_size": 0,  # Integer, not string
                "prepared_statement_cache_size": 0  # Integer, not string
            }
        )
        
        logger.info("Attempting to connect to database...")
        async with engine.connect() as conn:
            # Simple query to test connection
            result = await conn.execute(text("SELECT 1"))
            logger.info(f"Database connection successful: {result.fetchone()}")
            
        await engine.dispose()
        logger.info("Database test completed successfully")
        
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(test_database_connection())