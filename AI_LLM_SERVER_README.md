# AI LLM Model Server Setup and Usage

This document explains how to set up and run the OpenAI LLM model server for the IntelliTest AI Automation Platform.

## Overview

The AI Performance Tester backend includes support for OpenAI LLM models through the LangChain integration. The server runs on port 8002 and provides AI-powered performance analysis capabilities.

## Scripts

### 1. start-all-services.bat
This is the main script that starts all services including:
- Frontend (port 5175)
- Backend (port 8001)
- JMeter
- AI Perf Tester with OpenAI LLM support (port 8002)
- Docker Newman initialization for Postman collection testing

### 2. start-ai-llm-server.bat
This is a dedicated script that:
- Activates the virtual environment (creates it if it doesn't exist)
- Installs required AI dependencies
- Starts the AI Perf Tester backend with proper virtual environment isolation

### 3. start-all-services-with-ai.bat (Optional)
A variant of the main script that ensures the AI server is started with virtual environment activation and includes Docker Newman initialization.

## Setup Instructions

### 1. Environment Variables
Before starting the AI server, you need to configure your API keys:

1. Navigate to `ai-perf-tester/backend/`
2. Edit the `.env` file and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

### 2. Docker Newman Setup
The system automatically initializes Docker Newman when you start the services, but you can manually initialize it:

1. Ensure Docker Desktop is installed and running
2. Navigate to the backend directory:
   ```bash
   cd backend
   ```
3. Run the initialization script:
   - On Windows (PowerShell):
     ```bash
     .\scripts\init_newman.ps1
     ```
   - On Windows (Command Prompt):
     ```bash
     scripts\init_newman.bat
     ```

### 3. Running with Virtual Environment
To run the AI server with proper virtual environment isolation:

1. Double-click `start-ai-llm-server.bat`
2. This will:
   - Create a virtual environment if it doesn't exist
   - Activate the virtual environment
   - Install required AI dependencies
   - Start the AI Perf Tester backend

### 4. Running All Services
To start all services including the AI server and Docker Newman:

1. Double-click `start-all-services.bat`
2. The script will:
   - Kill any existing processes on required ports
   - Initialize Docker Newman for Postman collection testing
   - Activate the virtual environment if it exists
   - Start all services (Frontend, Backend, JMeter, AI Perf Tester)

## API Endpoints

Once the AI server is running, you can access:

- Main API: http://localhost:8002
- Documentation: http://localhost:8002/docs

## Troubleshooting

### Virtual Environment Issues
If you encounter issues with the virtual environment:
1. Delete the existing `.venv` folder in `ai-perf-tester/backend/`
2. Run `start-ai-llm-server.bat` again to recreate it

### Missing Dependencies
If you get import errors:
1. Run `start-ai-llm-server.bat` to ensure dependencies are installed
2. Or manually install them with:
   ```bash
   pip install -r ai-perf-tester/backend/ai_requirements.txt
   ```

### API Key Issues
If the AI analysis features don't work:
1. Verify your `.env` file contains a valid `OPENAI_API_KEY`
2. Check that the key has the necessary permissions
3. Ensure you have internet connectivity to reach the OpenAI API

### Docker Newman Issues
If Newman tests are not working:
1. Verify Docker Desktop is installed and running
2. Check that the `postman/newman` Docker image is available:
   ```cmd
   docker image ls | findstr newman
   ```
3. If not available, pull the image manually:
   ```cmd
   docker pull postman/newman
   ```
4. Test Newman directly:
   ```cmd
   docker run --rm -t postman/newman --version
   ```

## Manual Setup (Alternative)

If you prefer to set up manually:

1. Navigate to the AI backend directory:
   ```bash
   cd ai-perf-tester/backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -r ai_requirements.txt
   ```

4. Set your API key in the `.env` file

5. Initialize Docker Newman:
   ```bash
   cd ../..
   cd backend
   .\scripts\init_newman.ps1
   ```

6. Start the server:
   ```bash
   cd ..
   cd ai-perf-tester/backend
   python start.py
   ```