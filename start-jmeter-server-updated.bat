@echo off
REM start-jmeter-server-updated.bat
REM Batch file to start JMeter server from the correct directory with custom configuration

REM Use JMETER_HOME environment variable if set, otherwise use default
if defined JMETER_HOME (
    set JMETER_DIR=%JMETER_HOME%
    echo Using JMETER_HOME: %JMETER_HOME%
) else (
    set JMETER_DIR=C:\Users\kunal\Downloads\qix-master\qix-master\apache-jmeter-5.6.3
    echo Using default JMeter directory: %JMETER_DIR%
)

REM Change to the JMeter bin directory
cd /d "%JMETER_DIR%\bin"

REM Set the server port environment variable
set SERVER_PORT=54000

REM Start the JMeter server with custom properties including RMI configuration
jmeter-server.bat -Dserver_port=54000 -Jserver.rmi.localport=54000 -Jserver.rmi.port=54000 -Jserver.rmi.create=true -Jclient.rmi.localport=54000 -Jserver_port=54001 -Djava.rmi.server.hostname=127.0.0.1

REM Keep the window open so you can see any error messages
pause