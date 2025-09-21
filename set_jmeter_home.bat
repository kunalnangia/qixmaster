@echo off
title Set JMETER_HOME

echo Setting JMETER_HOME environment variable
echo.

REM Check if JMeter directory exists
if exist "apache-jmeter-5.6.3" (
    echo Found JMeter installation in apache-jmeter-5.6.3
    setx JMETER_HOME "%CD%\apache-jmeter-5.6.3"
    echo JMETER_HOME has been set to: %CD%\apache-jmeter-5.6.3
    echo.
) else (
    echo JMeter directory not found in the current location.
    echo Please extract JMeter to apache-jmeter-5.6.3 folder or adjust this script accordingly.
    echo.
)

echo Please also ensure Java is installed and JAVA_HOME is set:
echo 1. Download Java from https://adoptium.net/
echo 2. Install Java JDK 24
echo 3. Set JAVA_HOME environment variable to your Java installation directory
echo 4. Add %%JAVA_HOME%%\bin to your system PATH
echo.
echo After setting up Java, run set_java_home.bat to set JAVA_HOME.
echo.
echo Finally, restart your terminal/command prompt for all changes to take effect.
echo.
pause