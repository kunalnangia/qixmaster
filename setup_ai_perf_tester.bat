@echo off
REM Complete setup script for AI Performance Tester

echo ===================================================
echo AI Performance Tester Setup
echo ===================================================
echo.

cd %~dp0

REM 1. Ensure .env file exists and has AI keys
echo Step 1: Checking .env file configuration...
echo.

if not exist ".env" (
    echo Creating default .env file...
    (
        echo # AI MODEL CONFIGURATION
        echo # For OpenAI (ChatGPT) - Add your API key
        echo OPENAI_API_KEY=your_openai_api_key_here
        echo.
        echo # For Google Gemini - Add your API key if using Gemini instead
        echo # GEMINI_API_KEY=your_gemini_api_key_here
        echo.
        echo # AI model selection - options: gpt-4-turbo, gpt-3.5-turbo, gemini-pro
        echo AI_MODEL=gpt-4-turbo
    ) > .env
    echo Created default .env file. Please edit it to add your API keys.
) else (
    echo .env file exists. Checking for AI configuration...
    
    findstr /C:"OPENAI_API_KEY" .env >nul
    if %ERRORLEVEL% NEQ 0 (
        echo Adding OpenAI configuration to .env file...
        (
            echo.
            echo # AI MODEL CONFIGURATION
            echo # For OpenAI (ChatGPT) - Add your API key
            echo OPENAI_API_KEY=your_openai_api_key_here
            echo.
            echo # For Google Gemini - Add your API key if using Gemini instead
            echo # GEMINI_API_KEY=your_gemini_api_key_here
            echo.
            echo # AI model selection - options: gpt-4-turbo, gpt-3.5-turbo, gemini-pro
            echo AI_MODEL=gpt-4-turbo
        ) >> .env
        echo Added AI configuration to .env file.
    ) else (
        echo AI configuration found in .env file.
    )
)

echo.
echo Step 1 completed.
echo.

REM 2. Link .env file to ai-perf-tester backend
echo Step 2: Linking .env file to AI Performance Tester backend...
echo.

if exist "ai-perf-tester\backend\.env" (
    echo Removing existing .env file in backend directory...
    del "ai-perf-tester\backend\.env"
)

echo Creating symbolic link...
mklink "ai-perf-tester\backend\.env" ".env"

if %ERRORLEVEL% NEQ 0 (
    echo Failed to create symbolic link. Copying file instead...
    copy ".env" "ai-perf-tester\backend\.env"
    echo File copied.
) else (
    echo Symbolic link created successfully.
)

echo.
echo Step 2 completed.
echo.

REM 3. Install AI dependencies
echo Step 3: Installing AI analysis dependencies...
echo.

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

echo Installing packages...
pip install -r ai-perf-tester\backend\ai_requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo Failed to install dependencies. Please check the error messages above.
) else (
    echo Dependencies installed successfully.
)

echo.
echo Step 3 completed.
echo.

REM 4. Final instructions
echo ===================================================
echo Setup Complete!
echo ===================================================
echo.
echo IMPORTANT: Edit the .env file to add your actual API keys.
echo.
echo To start the AI Performance Tester backend:
echo cd ai-perf-tester\backend ^&^& python start.py
echo.
echo The server will be available at: http://127.0.0.1:8002
echo.
pause