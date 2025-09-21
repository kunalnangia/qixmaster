@echo off
echo ==========================================
echo Starting Backend Server on Port 8001
echo ==========================================

echo.
echo Changing to backend directory...
cd /d "c:\Users\kunal\Downloads\qix-master\qix-master\backend"

echo.
echo Activating virtual environment from root directory...
call ..\.venv\Scripts\activate.bat

echo.
echo Setting PYTHONPATH...
set PYTHONPATH=c:\Users\kunal\Downloads\qix-master\qix-master\backend

echo.
echo Starting server using run_server.py...
python run_server.py

echo.
echo Server stopped.
pause