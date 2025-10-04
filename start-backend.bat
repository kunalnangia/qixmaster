@echo off

:: Set error handling
setlocal enabledelayedexpansion

:: Set paths
set "BACKEND_DIR=c:\Users\kunal\Downloads\qix-master\qix-master\backend"
set "PYTHON=python"
set "PORT=8001"
set "MAX_RETRIES=5"
set "RETRY_DELAY=5"
set "retry_count=0"

echo ===================================================
echo           Starting Backend Server on Port %PORT%
echo ===================================================

:: Navigate to backend directory
cd /d "%BACKEND_DIR%"
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to navigate to backend directory: %BACKEND_DIR%
    pause
    exit /b 1
)

:check_db
n:check_db
:: Check database connection
echo.
echo 🔍 Checking database connection...
%PYTHON% check_db_connection.py
set "db_status=!ERRORLEVEL!"
nif "!db_status!"=="0" (
    echo ✅ Database connection successful
) else (
    echo ❌ Database connection failed with status: !db_status!
    
    set /a retry_count+=1
    
    if !retry_count! LEQ %MAX_RETRIES% (
        echo ⏳ Retrying in %RETRY_DELAY% seconds (Attempt !retry_count!/%MAX_RETRIES%)...
        timeout /t %RETRY_DELAY% >nul
        goto check_db
    ) else (
        echo ❌ Maximum retry attempts reached. Please check your database configuration.
        echo.
        echo TROUBLESHOOTING TIPS:
        echo 1. Make sure your database server is running
        echo 2. Verify DATABASE_URL in .env file is correct
        echo 3. Check if the database service is accessible
        echo 4. Review the logs in backend/logs/db_check.log for details
        echo.
        pause
        exit /b 1
    )
)
n:: Check and initialize database tables
echo.
echo 🔍 Checking database tables...
%PYTHON% -c "from app.db.session import init_db; init_db()"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to initialize database tables
    pause
    exit /b 1
)
n:: Verify required tables exist and are populated
echo.
echo 🔍 Verifying required tables and data...
%PYTHON% -c "
import os
import sys
from sqlalchemy import text
from app.db.session import engine, get_db_sync
from app.models.db_models import Base

def check_tables():
    required_tables = [
        'users', 'projects', 'test_cases', 'test_steps',
        'test_plans', 'test_executions', 'comments', 'teams',
        'team_members', 'environments', 'attachments',
        'activity_logs', 'test_plan_test_cases'
    ]
    
    with get_db_sync() as db:
        # Check if tables exist
        inspector = Base.metadata
        existing_tables = inspector.tables.keys()
        missing_tables = [t for t in required_tables if t not in existing_tables]
        
        if missing_tables:
            print(f"❌ Missing tables: {', '.join(missing_tables)}")
            print("🔄 Creating missing tables...")
            Base.metadata.create_all(bind=engine)
            print("✅ Tables created successfully")
        else:
            print("✅ All required tables exist")
            
        # Check if users table has data
        try:
            result = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
            if result == 0:
                print("⚠️  Users table is empty. Creating default admin user...")
                from app.db.init_data import create_initial_data
                create_initial_data()
                print("✅ Default admin user created")
            else:
                print(f"✅ Found {result} user(s) in the database")
        except Exception as e:
            print(f"❌ Error checking users table: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    check_tables()
"

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Database verification failed. Check the logs for details.
    pause
    exit /b 1
)
n:: Start the server
echo.
echo 🚀 Starting server on port %PORT%...
echo ===================================================
n%PYTHON% -m uvicorn app.main:app --host 0.0.0.0 --port %PORT% --reload --log-level debug

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Server stopped with error code: %ERRORLEVEL%
    echo.
    pause
    exit /b %ERRORLEVEL%
) else (
    echo.
    echo ✅ Server stopped normally
)
npause