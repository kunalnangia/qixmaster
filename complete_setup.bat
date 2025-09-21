@echo off
title Complete Java and JMeter Setup

echo ========================================
echo Complete Java and JMeter Setup
echo ========================================
echo.

REM Check if running as administrator (required for some operations)
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges.
) else (
    echo Warning: Some operations may require administrator privileges.
)

echo Step 1: Setting up Java...
echo.

REM Set default Java installation path
set JAVA_DEFAULT_PATH=C:\Program Files\Java\jdk-24

REM Check if Java directory exists at default location
if exist "%JAVA_DEFAULT_PATH%" (
    echo Found Java installation at %JAVA_DEFAULT_PATH%
    echo Setting JAVA_HOME...
    setx JAVA_HOME "%JAVA_DEFAULT_PATH%" >nul
    echo Adding Java to PATH...
    setx PATH "%PATH%;%JAVA_DEFAULT_PATH%\bin" >nul
    echo JAVA_HOME set to %JAVA_DEFAULT_PATH%
    echo Java added to PATH
) else (
    echo Java not found at default location: %JAVA_DEFAULT_PATH%
    echo.
    echo Please:
    echo 1. Download and install Java JDK 24 from https://adoptium.net/
    echo 2. Install to the default location, or
    echo 3. Modify this script with your Java installation path
    echo.
    pause
    exit /b
)

echo.
echo Step 2: Setting up JMeter...
echo.

REM Check if JMeter directory exists
if exist "apache-jmeter-5.6.3" (
    echo Found JMeter installation in apache-jmeter-5.6.3
    echo Setting JMETER_HOME...
    setx JMETER_HOME "%CD%\apache-jmeter-5.6.3" >nul
    echo Adding JMeter to PATH...
    setx PATH "%PATH%;%CD%\apache-jmeter-5.6.3\bin" >nul
    echo JMETER_HOME set to %CD%\apache-jmeter-5.6.3
    echo JMeter added to PATH
) else (
    echo JMeter directory not found.
    echo.
    echo Please:
    echo 1. Download Apache JMeter from https://jmeter.apache.org/download_jmeter.cgi
    echo 2. Extract to a folder named apache-jmeter-5.6.3 in this directory
    echo.
    pause
    exit /b
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Please restart your command prompt/PowerShell for changes to take effect.
echo.
echo Then verify the installation:
echo   java -version
echo   jmeter --version
echo.
echo After verification, you can run performance tests.
echo.
pause