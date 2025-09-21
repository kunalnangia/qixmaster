#!/usr/bin/env python3
"""
Database Connection Checker Script

This script validates the database connection according to project best practices:
1. Tests connectivity with DATABASE_URL from .env file
2. Verifies PgBouncer compatibility settings
3. Checks both sync and async database connections
4. Validates connection parameters for prepared statement caching
"""

import os
import sys
import asyncio
import logging
import traceback
from pathlib import Path
from sqlalchemy.exc import SQLAlchemyError

# Add the backend directory to the Python path
backend_path = Path(__file__).parent.absolute()
sys.path.insert(0, str(backend_path))

# Configure queue-based logging
try:
    from app.core.logging_config import setup_queue_logging, get_queue_logger
    # Set up logging with queue-based system
    logger = setup_queue_logging(
        log_level="INFO",
        log_dir=str(backend_path / "logs")
    )
    logger = get_queue_logger(__name__)
    logger.info("Using queue-based logging for database check")
except ImportError:
    # Fallback to concurrent log handler if available
    try:
        from concurrent_log_handler import ConcurrentRotatingFileHandler
        # Create logs directory if it doesn't exist
        logs_dir = backend_path / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # Configure root logger
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Create formatters
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # Add console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # Add file handler with concurrent rotation
        file_handler = ConcurrentRotatingFileHandler(
            str(logs_dir / "db_check.log"), 
            maxBytes=5*1024*1024,  # 5 MB
            backupCount=3
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        logger.info("Using ConcurrentRotatingFileHandler for database check logging")
    except ImportError:
        # Fallback to basic logging configuration
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger(__name__)
        logger.warning("concurrent-log-handler not installed, using basic logging configuration")

def check_environment():
    """Check if required environment variables are set"""
    logger.info("Checking environment variables...")
    
    # Load environment variables
    env_path = backend_path / '.env'
    if env_path.exists():
        from dotenv import load_dotenv
        load_dotenv(env_path, override=True)
        logger.info(f"Loaded environment from: {env_path}")
    else:
        logger.warning(f"No .env file found at: {env_path}")
    
    # Check required environment variables
    database_url = os.getenv("DATABASE_URL")
    database_url_async = os.getenv("DATABASE_URL_ASYNC")
    
    if not database_url:
        logger.error("No DATABASE_URL found in environment variables")
        return False
    
    logger.info(f"DATABASE_URL: {database_url[:60]}...")
    
    if database_url_async:
        logger.info(f"DATABASE_URL_ASYNC: {database_url_async[:60]}...")
    else:
        logger.info("DATABASE_URL_ASYNC not set, will construct from DATABASE_URL")
    
    return True

def check_sync_connection():
    """Test synchronous database connection"""
    logger.info("Testing synchronous database connection...")
    
    try:
        from sqlalchemy import create_engine, text
        
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            logger.error("DATABASE_URL not found in environment")
            return False
        
        # Ensure we're using the correct driver for sync connection
        if database_url.startswith("postgresql://"):
            sync_database_url = database_url.replace("postgresql://", "postgresql+psycopg2://")
        else:
            sync_database_url = database_url
        
        # Fix port for PgBouncer compatibility if needed
        if ":5432/" in sync_database_url:
            sync_database_url = sync_database_url.replace(":5432/", ":6543/")
            logger.info("Updated port to 6543 for PgBouncer compatibility")
        
        logger.info(f"Creating sync engine with URL: {sync_database_url[:60]}...")
        
        # Create engine with proper settings for PgBouncer compatibility
        engine = create_engine(
            sync_database_url,
            echo=False,  # Disable SQL query logging in production
            pool_pre_ping=True,
            pool_size=1,
            max_overflow=0,
            pool_recycle=300,
            pool_timeout=30,
            connect_args={
                'keepalives': 1,
                'keepalives_idle': 30,
                'keepalives_interval': 10,
                'keepalives_count': 5
            }
        )
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.scalar()
            logger.info(f"Successfully connected to PostgreSQL: {version}")
            
            # Test a simple query
            result = conn.execute(text("SELECT current_database(), current_user;"))
            row = result.fetchone()
            if row:
                db_name, user_name = row
                logger.info(f"Connected to database: {db_name} as user: {user_name}")
            else:
                logger.warning("Failed to fetch database info")
            
        engine.dispose()
        logger.info("Synchronous database connection test passed")
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error during sync connection test: {str(e)}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during sync connection test: {str(e)}")
        logger.debug(f"Error details: {repr(e)}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        return False

async def check_async_connection():
    """Test asynchronous database connection with comprehensive PgBouncer compatibility"""
    logger.info("Testing asynchronous database connection...")
    
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        from sqlalchemy.pool import NullPool
        
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL")
        database_url_async = os.getenv("DATABASE_URL_ASYNC")
        
        # Use async URL if available, otherwise construct it from sync URL
        if not database_url_async:
            if database_url:
                database_url_async = database_url.replace("postgresql://", "postgresql+asyncpg://")
            else:
                logger.error("No database URL found in environment")
                return False
        
        # Ensure database_url_async is not None before proceeding
        if not database_url_async:
            logger.error("Database URL for async connection is None")
            return False
        
        # Ensure comprehensive PgBouncer compatibility by removing any existing cache parameters
        # and adding correct ones
        if "?" in database_url_async:
            base_url, params = database_url_async.split("?", 1)
            # Ensure params is not None before splitting
            if params:
                # Remove existing cache parameters
                params_list = [p for p in params.split("&") if not (p.startswith("statement_cache_size") or p.startswith("prepared_statement_cache_size"))]
            else:
                params_list = []
            # Add correct cache parameters
            params_list.extend(["statement_cache_size=0", "prepared_statement_cache_size=0"])
            database_url_async = base_url + "?" + "&".join(params_list)
        else:
            database_url_async += "?statement_cache_size=0&prepared_statement_cache_size=0"
        
        # Fix port for PgBouncer compatibility if needed
        if ":5432/" in database_url_async:
            database_url_async = database_url_async.replace(":5432/", ":6543/")
            logger.info("Updated port to 6543 for PgBouncer compatibility")
        
        logger.info(f"Creating async engine with URL: {database_url_async[:60]}...")
        
        # Create async engine with comprehensive PgBouncer compatibility
        async_engine = create_async_engine(
            database_url_async,
            echo=False,
            poolclass=NullPool,  # Let PgBouncer do pooling instead of SQLAlchemy
            # Apply connect_args with correct parameter for PgBouncer compatibility
            connect_args={
                "statement_cache_size": 0,  # Critical for PgBouncer compatibility
                "prepared_statement_cache_size": 0,  # Additional cache disabling
                "server_settings": {
                    "statement_cache_size": "0",
                    "prepared_statement_cache_size": "0"
                }
            },
            # Disable compiled query cache at SQLAlchemy level
            execution_options={
                "compiled_cache": None,  # Disable compiled query cache
            }
        )
        
        # Test connection
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT version();"))
            version = result.scalar()
            logger.info(f"Successfully connected to PostgreSQL (async): {version}")
            
            # Test a simple query
            result = await conn.execute(text("SELECT current_database(), current_user;"))
            row = result.fetchone()
            if row:
                db_name, user_name = row
                logger.info(f"Connected to database (async): {db_name} as user: {user_name}")
            else:
                logger.warning("Failed to fetch database info (async)")
        
        await async_engine.dispose()
        logger.info("Asynchronous database connection test passed")
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error during async connection test: {str(e)}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during async connection test: {str(e)}")
        logger.debug(f"Error details: {repr(e)}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        return False

def check_connection_parameters():
    """Check database connection parameters for PgBouncer compatibility"""
    logger.info("Checking database connection parameters...")
    
    database_url = os.getenv("DATABASE_URL")
    database_url_async = os.getenv("DATABASE_URL_ASYNC")
    
    if not database_url:
        logger.error("DATABASE_URL not found in environment")
        return False
    
    # Check for PgBouncer port
    if ":6543/" in database_url:
        logger.info("✓ Using PgBouncer port (6543)")
    elif ":5432/" in database_url:
        logger.warning("⚠ Using standard PostgreSQL port (5432), should use PgBouncer port (6543)")
    else:
        logger.info("✓ Database URL format appears correct")
    
    # Check sync URL parameters
    if "statement_cache_size=0" in database_url:
        logger.info("✓ statement_cache_size=0 found in DATABASE_URL")
    else:
        logger.warning("⚠ statement_cache_size=0 not found in DATABASE_URL")
    
    # Check async URL parameters
    if database_url_async:
        if "statement_cache_size=0" in database_url_async:
            logger.info("✓ statement_cache_size=0 found in DATABASE_URL_ASYNC")
        else:
            logger.warning("⚠ statement_cache_size=0 not found in DATABASE_URL_ASYNC")
            
        if "prepared_statement_cache_size=0" in database_url_async:
            logger.info("✓ prepared_statement_cache_size=0 found in DATABASE_URL_ASYNC")
        else:
            logger.warning("⚠ prepared_statement_cache_size=0 not found in DATABASE_URL_ASYNC")
    
    return True

def test_prepared_statement_compatibility():
    """Test prepared statement compatibility with PgBouncer"""
    logger.info("Testing prepared statement compatibility...")
    
    try:
        from sqlalchemy import create_engine, text
        
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            logger.error("DATABASE_URL not found in environment")
            return False
        
        # Ensure we're using the correct driver for sync connection
        if database_url.startswith("postgresql://"):
            sync_database_url = database_url.replace("postgresql://", "postgresql+psycopg2://")
        else:
            sync_database_url = database_url
        
        # Fix port for PgBouncer compatibility if needed
        if ":5432/" in sync_database_url:
            sync_database_url = sync_database_url.replace(":5432/", ":6543/")
        
        # Add cache parameters for testing
        if sync_database_url and "?" in sync_database_url:
            sync_database_url += "&statement_cache_size=0"
        elif sync_database_url:
            sync_database_url += "?statement_cache_size=0"
        
        logger.info(f"Testing with URL: {sync_database_url[:60]}...")
        
        # Create engine with proper settings for PgBouncer compatibility
        engine = create_engine(
            sync_database_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=1,
            max_overflow=0,
            connect_args={
                'statement_cache_size': 0,  # Disable statement cache
            }
        )
        
        # Test connection with prepared statements
        with engine.connect() as conn:
            # Test creating and using a prepared statement
            stmt = text("SELECT * FROM information_schema.tables WHERE table_schema = :schema")
            result = conn.execute(stmt, {"schema": "public"})
            tables = result.fetchall()
            logger.info(f"Successfully executed prepared statement, found {len(tables)} tables")
            
        engine.dispose()
        logger.info("Prepared statement compatibility test passed")
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error during prepared statement test: {str(e)}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during prepared statement test: {str(e)}")
        logger.debug(f"Error details: {repr(e)}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        return False

async def main():
    """Main function to run all database connection checks"""
    logger.info("=" * 60)
    logger.info("Database Connection Checker")
    logger.info("=" * 60)
    
    # Check environment
    if not check_environment():
        logger.error("Environment check failed")
        return False
    
    # Check connection parameters
    check_connection_parameters()
    
    # Test synchronous connection
    sync_success = check_sync_connection()
    
    # Test asynchronous connection
    async_success = await check_async_connection()
    
    # Test prepared statement compatibility
    prepared_stmt_success = test_prepared_statement_compatibility()
    
    # Summary
    logger.info("=" * 60)
    logger.info("Database Connection Check Summary")
    logger.info("=" * 60)
    
    if sync_success:
        logger.info("✓ Synchronous database connection: PASSED")
    else:
        logger.error("✗ Synchronous database connection: FAILED")
    
    if async_success:
        logger.info("✓ Asynchronous database connection: PASSED")
    else:
        logger.error("✗ Asynchronous database connection: FAILED")
    
    if prepared_stmt_success:
        logger.info("✓ Prepared statement compatibility: PASSED")
    else:
        logger.error("✗ Prepared statement compatibility: FAILED")
    
    if sync_success and async_success and prepared_stmt_success:
        logger.info("🎉 All database connection tests PASSED")
        return True
    else:
        logger.error("❌ Some database connection tests FAILED")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Database connection check interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.debug(f"Error details: {repr(e)}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)