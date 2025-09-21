@echo off
REM start-jmeter.bat
REM Batch file to start JMeter server properly

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

REM Start JMeter server with custom properties
echo Starting JMeter server with custom configuration...

REM Check if port 50000 is already in use and select an alternative
netstat -a -n -o | find ":50000" > nul
if %ERRORLEVEL% == 0 (
    echo Port 50000 is already in use, using alternative port 51000...
    jmeter-server.bat -Dserver_port=1099 -Dserver.rmi.port=51000 -Djava.rmi.server.hostname=127.0.0.1
) else (
    echo Using default port 50000...
    jmeter-server.bat -Dserver_port=1099 -Dserver.rmi.port=50000 -Djava.rmi.server.hostname=127.0.0.1
)

REM Keep the window open so you can see any error messages
pause