@echo off
REM Script to install AI analysis dependencies

echo Installing AI Performance Analysis dependencies...
cd %~dp0

REM Make sure we have the virtual environment activated if it exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

echo Installing packages from ai-perf-tester\backend\ai_requirements.txt...
pip install -r ai-perf-tester\backend\ai_requirements.txt

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Dependencies installed successfully!
    echo.
    echo Now you can start the AI Performance Tester backend:
    echo cd ai-perf-tester\backend ^&^& python start.py
) else (
    echo.
    echo Failed to install dependencies. Please check the error messages above.
)

echo.
pause