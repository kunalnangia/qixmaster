@echo off
title Set JAVA_HOME

echo Setting JAVA_HOME environment variable
echo.

REM You need to modify this path to match your Java installation directory
set JAVA_INSTALL_PATH=C:\Program Files\Java\jdk-24

REM Check if Java directory exists
if exist "%JAVA_INSTALL_PATH%" (
    echo Found Java installation in %JAVA_INSTALL_PATH%
    setx JAVA_HOME "%JAVA_INSTALL_PATH%"
    echo JAVA_HOME has been set to: %JAVA_INSTALL_PATH%
    
    REM Also add Java to PATH
    setx PATH "%PATH%;%JAVA_INSTALL_PATH%\bin"
    echo Java has been added to PATH
    
    echo.
    echo Please restart your terminal/command prompt for the changes to take effect.
) else (
    echo Java directory not found at %JAVA_INSTALL_PATH%.
    echo.
    echo Please:
    echo 1. Download and install Java from https://adoptium.net/
    echo 2. Install JDK 24 to %JAVA_INSTALL_PATH% or modify this script with the correct path
    echo 3. Run this script again
)

echo.
pause