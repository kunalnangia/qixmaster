#!/usr/bin/env python3
"""
Startup script for the AI Performance Tester backend
"""

import uvicorn
import os
import sys

if __name__ == "__main__":
    # Add the current directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Run the FastAPI application on port 8002 to avoid conflicts with main backend
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8002,
        reload=True,
        log_level="info"
    )