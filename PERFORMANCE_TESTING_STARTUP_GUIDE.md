# Performance Testing Startup Guide

This document provides instructions for starting the performance testing environment and key performance strategies.

## Starting JMeter

To start JMeter, run the following command from the root project directory:

```powershell
.\start-jmeter.bat
```

This command should be executed every time you start the server to ensure JMeter is properly initialized for performance testing.

## Starting the AI Performance Tester Backend

To start the AI Performance Tester backend server, navigate to the backend directory and run:

```powershell
cd ai-perf-tester\backend
.\start.py
```

The server will start on port 8002.

## Performance Strategies

### 1. Environment Setup
- Ensure JMETER_HOME environment variable is set to your JMeter installation directory
- Verify Java is installed and accessible in your PATH
- Confirm all required Python dependencies are installed

### 2. JMeter Integration
- The system automatically locates JMeter through JMETER_HOME if it's not in the system PATH
- JMeter test plans are generated dynamically based on test requests
- Results are parsed and stored in the database for analysis

### 3. Monitoring and Optimization
- Monitor the health endpoint at `http://127.0.0.1:8002/health` to verify JMeter integration
- Check that `jmeter_home_valid` is true in the health response
- Ensure sufficient system resources (CPU, memory) are available for performance tests

### 4. Best Practices
- Always start JMeter before starting the backend server
- Regularly check the health endpoint to ensure proper integration
- Review test results and metrics to identify performance bottlenecks
- Use the AI analysis features to get recommendations for optimization