@echo off
REM check-jmeter-ports.bat
REM Script to check if JMeter required ports are available

echo Checking if port 1099 (RMI registry) is in use...
netstat -an | findstr :1099

echo.
echo Checking if ports in range 50000-50100 (RMI callbacks) are in use...
netstat -an | findstr :500

echo.
echo If any ports are in use, you may need to kill the processes or change the ports in jmeter.properties
echo.
echo To kill a process using a specific port, use:
echo taskkill /PID ^<process_id^> /F
echo.
echo Common JMeter ports:
echo - 1099: RMI registry port
echo - 50000-50100: RMI callback ports
echo.
pause