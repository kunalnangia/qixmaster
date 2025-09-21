# AI-Powered Performance Testing Integration

This document explains how to use the new AI-powered performance testing features that have been integrated into the Qix platform.

## Overview

The AI performance testing solution combines:
- **JMeter** for load testing execution
- **LangGraph** for AI analysis of test results
- **FastAPI** for the backend API
- **React** for the frontend UI

## Features

1. **Advanced Test Configuration**
   - Configure test type (load, stress, spike, endurance)
   - Set concurrent users, duration, and ramp-up time
   - Define performance thresholds for response time, error rate, and throughput

2. **Real-time Metrics**
   - Response time analysis
   - Error rate monitoring
   - Throughput measurements
   - Resource usage tracking

3. **AI-Powered Analysis**
   - Automatic bottleneck identification
   - Performance recommendations
   - Suggestions for next tests
   - Detailed analysis reports

4. **Export Capabilities**
   - Export test results to Excel
   - View detailed JMeter HTML reports

## How to Use

### 1. Configure a Test
1. Navigate to the Performance Testing section
2. Select a test case
3. Enter the URL to test
4. Configure advanced settings:
   - Test Type: Choose from load, stress, spike, or endurance
   - Concurrent Users: Number of simultaneous users
   - Duration: Test duration in seconds
   - Ramp-up Time: Time to reach full concurrent users
   - Thresholds: Performance thresholds for evaluation

### 2. Run the Test
Click "Run Performance Test" to execute the test. The system will:
1. Generate a JMeter test plan
2. Execute the load test
3. Collect and analyze results
4. Run AI analysis in the background

### 3. View Results
After the test completes, you can view:
- Core web vitals metrics
- Detailed performance data
- AI analysis with bottlenecks and recommendations
- JMeter HTML report

### 4. Export Data
Use the "Export to Excel" button to download detailed time-series data.

## API Endpoints

The performance testing backend exposes the following endpoints:

### Run Performance Test
```
POST /run-performance-test
```
Request body:
```json
{
  "test_name": "string",
  "test_type": "load|stress|spike|endurance",
  "url": "string",
  "concurrent_users": "integer",
  "duration": "integer",
  "ramp_up_time": "integer",
  "thresholds": {
    "response_time": "float",
    "error_rate": "float",
    "throughput": "float"
  }
}
```

### Get Performance History
```
GET /performance-history
```

### Get Test Details
```
GET /run-details/{run_id}
```

### Get AI Analysis
```
GET /ai-analysis/{run_id}
```

## Setup and Configuration

### Backend Setup
1. Install dependencies:
   ```bash
   cd ai-perf-tester/backend
   pip install -r requirements.txt
   ```

2. Run the backend:
   ```bash
   python start.py
   ```

### Frontend Setup
1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Run the frontend:
   ```bash
   npm run dev
   ```

### Environment Variables
For AI analysis features, set the following environment variable:
```
OPENAI_API_KEY=your_openai_api_key
```

## Troubleshooting

### Common Issues

1. **JMeter not found**: Ensure JMeter is installed and available in your PATH
2. **AI analysis not working**: Verify your OpenAI API key is set correctly
3. **CORS errors**: Check that the backend is running on port 8001

### Logs
Check the backend console output for detailed error messages and debugging information.