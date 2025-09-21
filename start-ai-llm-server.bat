@echo off
echo ==========================================
echo Starting OpenAI LLM Model Server
echo ==========================================

echo.
echo Activating virtual environment and starting AI Perf Tester Backend...
echo Make sure you have set your OPENAI_API_KEY in the .env file
echo.

cd /d "c:\Users\kunal\Downloads\qix-master\qix-master\ai-perf-tester\backend"

REM Check if virtual environment exists
if exist ".venv" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Creating one...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    echo Installing required dependencies...
    pip install -r ai_requirements.txt
    echo.
    echo Please make sure to set your OPENAI_API_KEY in the .env file
    echo.
)

echo.
echo Installing/Updating AI requirements...
pip install -r ai_requirements.txt

echo.
echo Starting AI Perf Tester Backend with OpenAI LLM Model support...
echo Server will be available at http://localhost:8002
echo.

python start.py

echo.
echo Press any key to exit...
pause >nul