@echo off
REM Script to link root .env to ai-perf-tester backend directory

echo Creating symbolic link to root .env file...
cd %~dp0

REM Check if .env exists in ai-perf-tester/backend
if exist "ai-perf-tester\backend\.env" (
    echo .env file already exists in ai-perf-tester/backend
    echo Removing existing file...
    del "ai-perf-tester\backend\.env"
)

REM Create symbolic link using mklink command
mklink "ai-perf-tester\backend\.env" ".env"

if %ERRORLEVEL% EQU 0 (
    echo Environment link created successfully!
    echo Root .env file will now be used for AI Performance Tester.
) else (
    echo Failed to create symbolic link.
    echo Manually copying .env file instead...
    copy ".env" "ai-perf-tester\backend\.env"
    echo File copied.
)

echo.
echo You can now start the AI Performance Tester backend:
echo cd ai-perf-tester\backend ^&^& python start.py
echo.
pause