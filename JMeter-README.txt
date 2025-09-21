# JMeter Server Setup Instructions

## Prerequisites
- Java 8 or higher installed
- JMeter 5.6.3 downloaded and extracted to `C:\Users\kunal\Downloads\qix-master\qix-master\apache-jmeter-5.6.3`

## Setup Steps
1. Ensure BeautifulSoup4 is installed: `pip install beautifulsoup4`
2. Run the `create-rmi-keystore.bat` script if `rmi_keystore.jks` doesn't exist
3. Use one of the provided scripts to start the JMeter server

## Available Scripts
- `start-jmeter-server.bat` - Basic script to start JMeter server
- `start-jmeter-server-updated.bat` - Script with custom port configuration
- `start-jmeter-server-updated.ps1` - PowerShell version with custom port configuration
- `check-jmeter-ports.bat` - Script to check if required ports are available

## Troubleshooting
1. If you get "Port already in use" errors:
   - Run `check-jmeter-ports.bat` to see which ports are in use
   - Either kill the processes using those ports or modify the ports in `jmeter.properties`

2. If you get SSL/keystore errors:
   - Run `create-rmi-keystore.bat` in the JMeter bin directory
   - Make sure `rmi_keystore.jks` exists in the bin directory

3. If you get binding errors:
   - Try changing `java.rmi.server.hostname` in `jmeter.properties` to `127.0.0.1`
   - Or try using a different port for `server_port`

## Making Scripts Run on Startup
To make the JMeter server start automatically on system restart:
1. Press Win + R, type `shell:startup`, and press Enter
2. Copy one of the batch files to the startup folder
3. The script will run automatically when Windows starts