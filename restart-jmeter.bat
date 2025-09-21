@echo off
REM restart-jmeter.bat
REM Batch file to kill existing JMeter processes and start a new JMeter server

echo Stopping any existing JMeter processes...
taskkill /F /FI "IMAGENAME eq java.exe" /FI "WINDOWTITLE eq *JMeter*" > nul 2>&1
timeout /t 2 /nobreak > nul

REM Use JMETER_HOME environment variable if set, otherwise use default
if defined JMETER_HOME (
    set JMETER_DIR=%JMETER_HOME%
    echo Using JMETER_HOME: %JMETER_HOME%
) else (
    set JMETER_DIR=C:\Users\kunal\Downloads\qix-master\qix-master\apache-jmeter-5.6.3
    echo Using default JMeter directory: %JMETER_DIR%
)

REM Check if JMeter directory exists
if not exist "%JMETER_DIR%" (
    echo Error: JMeter directory not found at %JMETER_DIR%
    echo Please make sure JMeter is installed at the correct location.
    pause
    exit /b 1
)

REM Change to the JMeter bin directory
cd /d "%JMETER_DIR%\bin"

REM Check if jmeter-server.bat exists
if not exist "jmeter-server.bat" (
    echo Error: jmeter-server.bat not found in %JMETER_DIR%\bin
    pause
    exit /b 1
)

REM Display startup message
echo Starting JMeter Server...
echo JMeter Directory: %JMETER_DIR%
echo Current Directory: %CD%
echo ----------------------------------------

REM Start JMeter server with alternative port
echo Starting JMeter server on port 51000...
jmeter-server.bat -Dserver_port=1099 -Dserver.rmi.port=51000 -Djava.rmi.server.hostname=127.0.0.1

REM Keep the window open so you can see any error messages
pause