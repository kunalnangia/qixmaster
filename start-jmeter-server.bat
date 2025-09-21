@echo off
REM start-jmeter-server.bat
REM Batch file to start JMeter server from the correct directory

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

REM Start the JMeter server
jmeter-server.bat

REM Keep the window open so you can see any error messages
pause