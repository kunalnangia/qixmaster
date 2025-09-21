@echo off
title Add Java and JMeter to PATH

echo Adding Java and JMeter to system PATH...
echo.

REM Set default paths
set JAVA_PATH=C:\Program Files\Java\jdk-24\bin
set JMETER_PATH=%CD%\apache-jmeter-5.6.3\bin

echo Adding paths to system PATH:
echo   %JAVA_PATH%
echo   %JMETER_PATH%
echo.

REM Get current PATH
for /f "skip=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH') do set REGPATH=%%b

REM Add new paths to PATH
set NEWPATH=%REGPATH%;%JAVA_PATH%;%JMETER_PATH%

REM Update system PATH
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH /t REG_EXPAND_SZ /d "%NEWPATH%" /f >nul

echo Paths added successfully!
echo.
echo Please restart your command prompt/PowerShell for changes to take effect.
echo.
echo Then verify the installation:
echo   java -version
echo   jmeter --version
echo.
pause