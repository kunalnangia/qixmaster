import os
import sys
import logging
import traceback
from typing import AsyncGenerator
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

# Import Base from base.py to avoid circular imports
from .base import Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
logger.info(f"Loading environment from: {env_path}")

# Load environment variables
load_dotenv(env_path, override=True)

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_URL_ASYNC = os.getenv("DATABASE_URL_ASYNC")

if not DATABASE_URL:
    raise ValueError("No DATABASE_URL found in environment variables")

# Use async URL if available, otherwise construct it from sync URL
if not DATABASE_URL_ASYNC:
    # Construct async URL from sync URL
    DATABASE_URL_ASYNC = str(DATABASE_URL).replace("postgresql://", "postgresql+asyncpg://")

# Ensure comprehensive PgBouncer compatibility by removing any existing cache parameters
# and adding correct ones
if DATABASE_URL_ASYNC and "?" in DATABASE_URL_ASYNC:
    base_url, params = DATABASE_URL_ASYNC.split("?", 1)
    # Remove existing cache parameters
    params_list = [p for p in params.split("&") if not (p.startswith("statement_cache_size") or p.startswith("prepared_statement_cache_size"))]
    # Add correct cache parameters as integers (not strings)
    params_list.extend(["statement_cache_size=0", "prepared_statement_cache_size=0"])
    DATABASE_URL_ASYNC = base_url + "?" + "&".join(params_list)
elif DATABASE_URL_ASYNC:
    DATABASE_URL_ASYNC += "?statement_cache_size=0&prepared_statement_cache_size=0"

# Fix port for PgBouncer compatibility if needed
if ":5432/" in DATABASE_URL_ASYNC:
    DATABASE_URL_ASYNC = DATABASE_URL_ASYNC.replace(":5432/", ":6543/")

logger.info("Database URLs configured")
logger.info(f"Sync URL: {DATABASE_URL[:60]}...")
logger.info(f"Async URL: {DATABASE_URL_ASYNC[:60]}...")

# Create sync engine for migrations and sync operations
if DATABASE_URL.startswith("sqlite"):
    # SQLite configuration
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False},
        echo=True
    )
else:
    # PostgreSQL configuration
    sync_database_url = str(DATABASE_URL).replace("postgresql://", "postgresql+psycopg2://")
    if ":5432/" in sync_database_url:
        sync_database_url = sync_database_url.replace(":5432/", ":6543/")
        
    engine = create_engine(
        sync_database_url,
        echo=True,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_recycle=300,
        pool_timeout=30,
        connect_args={
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 10,
            'keepalives_count': 5
        }
    )

# Create async engine for FastAPI with asyncpg
async_engine = create_async_engine(
    DATABASE_URL_ASYNC,
    echo=False,
    poolclass=NullPool,
    connect_args={
        "statement_cache_size": 0,  # Must be integer, not string
        "prepared_statement_cache_size": 0,  # Must be integer, not string
        "server_settings": {
            "statement_cache_size": "0",  # String for server settings
            "prepared_statement_cache_size": "0"  # String for server settings
        }
    },
    execution_options={
        "compiled_cache": None,
    }
)

# Session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Scoped session for thread safety
ScopedSession = scoped_session(SessionLocal)

# Dependency for getting async database session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            pass

# Sync session for migrations and scripts
@contextmanager
def get_sync_db():
    db = ScopedSession()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()

# Synchronous database dependency
def get_db_sync():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        db.close()

def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

# Simple test user management
TEST_USER_ID = "temp-user-id-for-testing"
TEST_USER_EMAIL = "test@example.com"
TEST_USER_NAME = "Test User"

AI_GENERATOR_USER_ID = "ai-generator"
AI_GENERATOR_EMAIL = "ai-tests@example.com"
AI_GENERATOR_NAME = "AI Test Generator"

def get_ai_generator_user_id() -> str:
    return AI_GENERATOR_USER_ID

def get_test_user_id() -> str:
    return TEST_USER_ID