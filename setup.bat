@echo off
title AI Perf Tester Setup

echo Setting up AI Perf Tester...
echo.

REM Check if JMeter is installed
echo Checking for JMeter installation...
jmeter --version >nul 2>&1
if %errorlevel% == 0 (
    echo JMeter is already installed.
) else (
    echo JMeter is not installed or not in PATH.
    echo.
    echo Option 1: Download and run the automated setup script:
    echo   python setup_jmeter.py
    echo.
    echo Option 2: Manual installation:
    echo   1. Download JMeter from https://jmeter.apache.org/download_jmeter.cgi
    echo   2. Extract to a directory named apache-jmeter-5.6.3 in this folder
    echo   3. Run set_jmeter_home.bat to set the JMETER_HOME environment variable
    echo   4. Or add apache-jmeter-5.6.3\bin to your system PATH
    echo.
    echo After installation, restart your command prompt and run this setup script again.
    echo.
    pause
    exit /b
)

REM Setup backend
echo Setting up backend dependencies...
cd ai-perf-tester\backend
pip install -r requirements.txt

REM Setup frontend
echo Setting up frontend dependencies...
cd ..\..\frontend
npm install

REM Install xlsx for Excel export
echo Installing additional frontend dependencies...
npm install xlsx

echo.
echo Setup complete!
echo.
echo To run the application:
echo 1. Start the backend: cd ai-perf-tester\backend && python start.py
echo 2. Start the frontend: cd frontend && npm run dev
echo.
echo Make sure to set your OPENAI_API_KEY environment variable for AI features.
pause