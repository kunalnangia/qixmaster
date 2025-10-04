import asyncio
import logging
from app.db.session import initialize_database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_connection():
    try:
        logger.info("Starting database connection test...")
        await initialize_database()
        logger.info("Database connection test completed successfully!")
    except Exception as e:
        logger.error(f"Error during connection test: {e}")
    finally:
        # Ensure the event loop is closed
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.stop()
            loop.close()

if __name__ == "__main__":
    logger.info("Running database connection test...")
    asyncio.run(test_connection())