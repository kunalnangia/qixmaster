@echo off
echo ==========================================
echo Stopping all services and killing processes
echo ==========================================

echo.
echo Killing processes on port 5175 (Frontend)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5175') do taskkill /f /pid %%a 2>nul

echo Killing processes on port 8001 (Backend)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001') do taskkill /f /pid %%a 2>nul

echo Killing processes on port 50000 (JMeter)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :50000') do taskkill /f /pid %%a 2>nul

echo Killing processes on port 51000 (Alternative JMeter)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :51000') do taskkill /f /pid %%a 2>nul

echo Killing processes on port 8002 (LangGraph/AI Perf Tester with OpenAI LLM)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8002') do taskkill /f /pid %%a 2>nul

echo.
echo All processes killed successfully.
echo.

echo ==========================================
echo Initializing Docker Newman for Postman Collections
echo ==========================================

echo.
echo Checking Docker availability...
docker --version >nul 2>&1
if %errorlevel% == 0 (
    echo Docker is available.
    echo.
    echo Pulling postman/newman Docker image...
    docker pull postman/newman
    if %errorlevel% == 0 (
        echo Docker Newman image is ready.
        echo.
        echo Testing Docker Newman...
        docker run --rm -t postman/newman --version >nul 2>&1
        if %errorlevel% == 0 (
            echo Docker Newman is working correctly.
        ) else (
            echo Warning: Docker Newman test failed. Newman tests may not work properly.
        )
    ) else (
        echo Warning: Failed to pull Docker Newman image. Newman tests may not work properly.
    )
) else (
    echo Warning: Docker is not available. Newman tests will not work.
)

echo.
echo ==========================================
echo Starting all services
echo ==========================================

echo.
echo Starting JMeter...
cd /d "c:\Users\kunal\Downloads\qix-master\qix-master"
start "JMeter" /min cmd /c ".\start-jmeter.bat"

echo.
echo Installing AI Requirements and Starting LangGraph/AI Perf Tester Backend...
echo Note: Installing AI requirements to ensure all dependencies are available
cd /d "c:\Users\kunal\Downloads\qix-master\qix-master\ai-perf-tester\backend"
echo Installing AI requirements...
pip install -r ai_requirements.txt

echo.
echo Starting LangGraph/AI Perf Tester Backend with OpenAI LLM Model...
echo Note: Make sure to activate the virtual environment and set OPENAI_API_KEY in .env file
echo For dedicated AI server with virtual environment, use start-ai-llm-server.bat

REM Check if virtual environment exists and activate it
if exist ".venv" (
    echo Activating virtual environment for AI Perf Tester...
    call .venv\Scripts\activate.bat
    start "AI Perf Tester" cmd /c "python start.py"
) else (
    echo Virtual environment not found. Starting without virtual environment...
    echo Please run start-ai-llm-server.bat separately to set up the virtual environment.
    start "AI Perf Tester" cmd /c "python start.py"
)

echo.
echo Starting Backend...
cd /d "c:\Users\kunal\Downloads\qix-master\qix-master\backend"
start "Backend" cmd /c "python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload --log-level debug"

echo.
echo Starting Frontend...
cd /d "c:\Users\kunal\Downloads\qix-master\qix-master\frontend"
set PORT=5175
start "Frontend" cmd /c "npm run dev"

echo.
echo All services started successfully!
echo.
echo Frontend: http://localhost:5175
echo Backend: http://localhost:8001
echo JMeter: Check JMeter GUI or logs
echo AI Perf Tester with OpenAI LLM: http://localhost:8002
echo.
echo Docker Newman: Initialized for Postman collection testing
echo Example: docker run -t postman/newman run "https://api.getpostman.com/collections/47463989-8d6cec84-fb64-48dc-8d71-7c2e6ba45c28?apikey=PMAK-68bc06cf8e88740001889312-b50afdd3066958a44f1a7d8ed5e48cf10d"
echo.
echo Additional AI LLM Server Scripts:
echo - start-ai-llm-server.bat: Dedicated script with virtual environment setup
echo - start-all-services-with-ai.bat: Variant that ensures AI server virtual environment
echo - AI_LLM_SERVER_README.md: Documentation for AI LLM server setup
echo.
echo Press any key to exit...
pause >nul