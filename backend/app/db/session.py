import os
import sys
import logging
import certifi
import asyncio
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from urllib.parse import urlparse, parse_qsl, urlunparse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

# Set SSL certificate path for all SSL connections
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for the engines - they will be initialized later
async_engine = None
sync_engine = None

def load_environment_variables():
    """Load environment variables from the .env file."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
    load_dotenv(env_path, override=True)

    global DATABASE_URL, DATABASE_URL_ASYNC
    DATABASE_URL = os.getenv("DATABASE_URL")
    DATABASE_URL_ASYNC = os.getenv("DATABASE_URL_ASYNC")

    if not DATABASE_URL or not DATABASE_URL_ASYNC:
        raise ValueError("DATABASE_URL or DATABASE_URL_ASYNC not found in environment variables")
    
    logger.info("Environment variables loaded")
    logger.info(f"DATABASE_URL: {DATABASE_URL}")
    logger.info(f"DATABASE_URL_ASYNC: {DATABASE_URL_ASYNC}")

# Load environment variables on module import
load_environment_variables()
 
# In app/db/session.py

# Replace the async engine creation with:
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool
import os
from urllib.parse import urlparse, parse_qs


 
 
async def initialize_database():
    global async_engine, sync_engine
    
    # Load environment variables
    DATABASE_URL = os.getenv("DATABASE_URL")
    DATABASE_URL_ASYNC = os.getenv("DATABASE_URL_ASYNC")
    
    logger.info("Environment variables loaded")
    logger.info(f"DATABASE_URL: {DATABASE_URL}")
    logger.info(f"DATABASE_URL_ASYNC: {DATABASE_URL_ASYNC}")

    try:
        # Sync engine (using psycopg2)
        sync_engine = create_engine(
            DATABASE_URL,
            echo=True,
            pool_pre_ping=True
        )
        
        # Parse the async URL to handle SSL
        parsed_url = urlparse(DATABASE_URL_ASYNC)
        query_params = parse_qs(parsed_url.query)
        
        # Prepare connection arguments
        connect_args = {
            "statement_cache_size": 0,
            "prepared_statement_cache_size": 0
        }
        
        # Handle SSL
        if 'sslmode' in query_params and query_params['sslmode'][0] == 'require':
            connect_args['ssl'] = 'require'
        
        # Rebuild URL without sslmode in query
        clean_url = DATABASE_URL_ASYNC.replace('postgresql+asyncpg://', 'postgresql://')
        
        # Create async engine
        async_engine = create_async_engine(
            clean_url,
            echo=True,
            poolclass=NullPool,
            connect_args=connect_args
        )
        
        logger.info("Database engines initialized successfully")
        return async_engine
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise
    
    global async_engine, sync_engine
    
    # Load environment variables
    load_environment_variables()
    
    # Sync engine (using psycopg2)
    sync_engine = create_engine(
        os.getenv("DATABASE_URL"),
        echo=True,
        pool_pre_ping=True
    )
    
    # Async engine (using asyncpg)
    async_engine = create_async_engine(
        os.getenv("DATABASE_URL_ASYNC").replace('postgresql+asyncpg://', 'postgresql://'),
        echo=True,
        poolclass=NullPool,
        connect_args={
            "ssl": "require",
            "statement_cache_size": 0,
            "prepared_statement_cache_size": 0
        }
    )
    
    logger.info("Database engines initialized successfully")
    return async_engine

# NOTE: Dependency for FastAPI. Yields a new session for each request.
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provides a database session for a single request."""
    # Ensure the engine is initialized before use
    if async_engine is None:
        raise RuntimeError("Database engine not initialized. Please run initialize_database() first.")
        
    async_session_local = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session_local() as session:
        yield session

# NOTE: Dependency for synchronous database operations
def get_db_sync():
    """Provides a synchronous database session for a single request."""
    if sync_engine is None:
        raise RuntimeError("Synchronous database engine not initialized.")
    SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=sync_engine))
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

async def force_connection_reset() -> bool:
    """
    Force reset database connections to ensure PgBouncer compatibility.
    Disposes of the async engine to reset connections.
    """
    if async_engine:
        try:
            await async_engine.dispose()
            logger.info("Database connections reset successfully for PgBouncer compatibility")
            return True
        except Exception as e:
            logger.error(f"Failed to reset database connections: {e}")
            return False
    return False
