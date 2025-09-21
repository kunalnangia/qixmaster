import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI

# Create a minimal FastAPI app without database dependencies
app = FastAPI(title="IntelliTest Minimal API", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "IntelliTest API is running", "status": "ok"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "IntelliTest API"}

@app.get("/api/v1/projects-test")
async def get_projects_test():
    # Return mock data to test the frontend
    return [
        {"id": "1", "name": "Sample Project 1", "description": "A sample project for testing"},
        {"id": "2", "name": "Sample Project 2", "description": "Another sample project for testing"}
    ]

@app.get("/api/v1/test-cases")
async def get_test_cases():
    # Return mock data to test the frontend
    return [
        {"id": "1", "title": "Sample Test Case 1", "description": "A sample test case"},
        {"id": "2", "title": "Sample Test Case 2", "description": "Another sample test case"}
    ]

if __name__ == "__main__":
    import uvicorn
    print("Starting minimal IntelliTest API server...")
    print("Access the API at: http://localhost:8002")
    uvicorn.run(app, host="0.0.0.0", port=8002)  # Changed to port 8002 to avoid conflicts
