# JMeter Server Setup and Usage Instructions

## Prerequisites
- Java 8 or higher installed
- JMeter 5.6.3 downloaded and extracted to `C:\Users\kunal\Downloads\qix-master\qix-master\apache-jmeter-5.6.3`

## Setup Steps
1. Ensure BeautifulSoup4 is installed: `pip install beautifulsoup4`
2. Run the `create-rmi-keystore.bat` script if `rmi_keystore.jks` doesn't exist
3. Use one of the provided scripts to start the JMeter server

## Available Scripts
- `start-jmeter.bat` - Batch file to start JMeter server in foreground
- `start-jmeter-background.bat` - Batch file to start JMeter server in background
- `start-jmeter.ps1` - PowerShell script to start JMeter server
- `check-jmeter-ports.bat` - Script to check if required ports are available

## Verifying JMeter Server is Running
When the JMeter server starts successfully, you should see output similar to:
```
Using local port: 50000
Created remote object: UnicastServerRef2 [...]
```

## For Performance Testing
Once JMeter server is running, you can use the performance testing features in the application:
1. Start the backend server: `cd c:\Users\kunal\Downloads\qix-master\qix-master\ai-perf-tester\backend ; python start.py`
2. Start the frontend: `cd c:\Users\kunal\Downloads\qix-master\qix-master\frontend ; npm run dev`
3. Navigate to the Performance Testing page in the application
4. Configure your test parameters and run tests

The application will automatically connect to the JMeter server running on localhost.