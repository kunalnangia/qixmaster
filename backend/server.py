import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
logger.info(f"Added to Python path: {current_dir}")

# Print sys.path for debugging
logger.info(f"Python path: {sys.path}")

try:
    # Import the app
    logger.info("Importing app from app.main...")
    from app.main import app
    logger.info("App imported successfully!")
    
    if __name__ == "__main__":
        import uvicorn
        logger.info("Starting uvicorn server on port 8001...")
        uvicorn.run("server:app", host="0.0.0.0", port=8001, reload=True)
        
except Exception as e:
    logger.error(f"Error starting server: {e}")
    import traceback
    traceback.print_exc()