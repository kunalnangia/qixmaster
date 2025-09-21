@echo off
REM verify-jmeter.bat
REM Script to verify if JMeter server is running properly

echo Verifying JMeter server status...
echo.

REM Check if JMeter process is running
echo Checking for JMeter processes...
tasklist | findstr java

echo.
echo Checking for JMeter listening ports...
netstat -an | findstr :50000

echo.
echo If you see java processes and ports listening on 50000, JMeter server is running.
echo.
echo To test the performance testing functionality:
echo 1. Make sure this JMeter server is running
echo 2. Start the backend server
echo 3. Start the frontend application
echo 4. Navigate to the Performance Testing page
echo.
pause