@echo off
REM start-jmeter-background.bat
REM Batch file to start JMeter server in the background

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
echo Starting JMeter Server in background...
echo JMeter Directory: %JMETER_DIR%
echo Current Directory: %CD%
echo ----------------------------------------

REM Set the server port environment variable
set SERVER_PORT=54000

REM Start JMeter server with custom properties in background
echo Starting JMeter server with custom configuration on port 54000...
start "JMeter Server" /MIN jmeter-server.bat -Dserver_port=54000 -Jserver.rmi.localport=54000 -Jserver.rmi.port=54000 -Jserver.rmi.create=true -Jclient.rmi.localport=54000 -Jserver_port=54001 -Djava.rmi.server.hostname=127.0.0.1

echo JMeter server started successfully in background on port 54000.
echo You can now run performance tests.
pause