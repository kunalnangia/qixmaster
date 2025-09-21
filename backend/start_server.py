import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now import and run the server
if __name__ == "__main__":
    import uvicorn
    from app.main import app
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)