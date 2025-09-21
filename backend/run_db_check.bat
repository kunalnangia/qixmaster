@echo off
echo Running Database Connection Checker...
echo ======================================
cd /d "%~dp0"
python check_db_connection.py
echo.
echo Press any key to exit...
pause >nul