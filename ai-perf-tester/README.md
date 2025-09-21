# AI Perf Tester 🚀

An end-to-end **performance testing platform** powered by:
- **LangGraph** for AI workflows
- **JMeter** for load testing
- **FastAPI** backend
- **React + Tailwind + Recharts** frontend

## Features
✅ Configure & run tests (ramp-up, steady, spike, endurance)  
✅ View summary cards (response time, throughput, errors, CPU, memory)  
✅ Access full **JMeter HTML report**  
✅ Track history + trends across runs  
✅ Drill-down per run → mini-charts (response, errors, throughput)  
✅ Export history as **CSV/Excel**  
✅ **Enhanced AI Workflow** with 5-stage orchestration:
   - Test validation and preprocessing
   - Environment setup and connectivity checks
   - Dynamic test plan generation
   - Real-time monitoring during execution
   - Post-test analysis and reporting

## Prerequisites
- Python 3.8+
- Node.js 16+
- **Java 8+** installed and available in PATH
- **JMeter 5.6+** installed and available in PATH
- OpenAI API key (for AI analysis features - optional)

## Installation

### Java Installation
1. Download OpenJDK from [https://adoptium.net/](https://adoptium.net/)
2. Install Java JDK 24 (recommended) or JDK 21
3. Set the `JAVA_HOME` environment variable to point to your Java installation directory
4. Add `%JAVA_HOME%\bin` to your system PATH
5. Verify installation by running:
   ```bash
   java -version
   ```

### JMeter Installation
1. Download Apache JMeter from [https://jmeter.apache.org/download_jmeter.cgi](https://jmeter.apache.org/download_jmeter.cgi)
2. Extract to a directory (e.g., `C:\apache-jmeter-5.6.2`)
3. Add JMeter to your system PATH:
   - Add `C:\apache-jmeter-5.6.2\bin` to your system PATH environment variable
4. **Alternative**: Set the `JMETER_HOME` environment variable to point to your JMeter installation directory
5. Verify installation by running:
   ```bash
   jmeter --version
   ```

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python start.py
```

The backend will be available at http://127.0.0.1:8002

### Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
```

The frontend will be available at http://localhost:5173

## API Endpoints

### Performance Testing
- `POST /run-performance-test` - Run a performance test
- `GET /performance-history` - Get test history
- `GET /run-details/{run_id}` - Get detailed results for a test run
- `GET /ai-analysis/{run_id}` - Get AI analysis for a test run
- `POST /request-ai-analysis` - Request AI analysis for an existing test run

## Enhanced Workflow Orchestration

The system now includes an enhanced LangGraph-based workflow orchestration with 5 key components:

1. **Test Validation and Preprocessing**
   - AI-powered input validation
   - Configuration optimization
   - Test scenario enhancement

2. **Environment Setup and Connectivity Checks**
   - Infrastructure monitoring setup
   - Test data preparation
   - Endpoint connectivity validation

3. **Dynamic Test Plan Generation**
   - AI-generated test scenarios
   - JMeter test plan creation
   - Custom load pattern generation

4. **Real-time Monitoring During Execution**
   - Continuous performance metrics collection
   - Infrastructure resource tracking
   - Dynamic alerting system

5. **Post-test Analysis and Reporting**
   - Comprehensive AI analysis
   - Bottleneck identification
   - Optimization recommendations
   - Multi-format report generation

## Requirements
- Python 3.8+
- Node.js 16+
- JMeter installed and available in PATH
- OpenAI API key (for AI analysis features)