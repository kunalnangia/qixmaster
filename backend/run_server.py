import uvicorn
import sys
import os
import subprocess
import logging
from multiprocessing import freeze_support

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_newman():
    """Initialize Docker Newman before starting the server"""
    try:
        logger.info("Initializing Docker Newman...")
        
        # Check if Docker is available
        try:
            docker_result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if docker_result.returncode != 0:
                logger.warning("Docker is not available. Newman tests will not work.")
                return False
        except subprocess.TimeoutExpired:
            logger.warning("Docker version check timed out.")
            return False
        except FileNotFoundError:
            logger.warning("Docker is not installed. Newman tests will not work.")
            return False
        except Exception as e:
            logger.warning(f"Docker is not available: {str(e)}")
            return False
        
        # Pull the Newman Docker image with a shorter timeout and non-blocking approach
        logger.info("Pulling postman/newman Docker image...")
        try:
            # Use a shorter timeout and don't block execution
            pull_process = subprocess.Popen(
                ["docker", "pull", "postman/newman"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for a short time, then continue regardless
            try:
                stdout, stderr = pull_process.communicate(timeout=30)
                if pull_process.returncode == 0:
                    logger.info("Docker Newman image is ready.")
                else:
                    logger.warning(f"Failed to pull Newman image: {stderr}")
            except subprocess.TimeoutExpired:
                # Kill the process if it's still running
                pull_process.kill()
                stdout, stderr = pull_process.communicate()
                logger.info("Docker pull command timed out, but continuing...")
        except Exception as e:
            logger.warning(f"Error during Docker pull: {str(e)}")
        
        # Test Newman (non-blocking)
        logger.info("Testing Docker Newman...")
        try:
            test_process = subprocess.Popen(
                ["docker", "run", "--rm", "-t", "postman/newman", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            try:
                stdout, stderr = test_process.communicate(timeout=15)
                if test_process.returncode == 0:
                    logger.info(f"Docker Newman is working correctly (version: {stdout.strip()}).")
                    return True
                else:
                    logger.warning(f"Docker Newman test failed: {stderr}")
            except subprocess.TimeoutExpired:
                test_process.kill()
                stdout, stderr = test_process.communicate()
                logger.info("Newman test timed out, but continuing...")
        except Exception as e:
            logger.warning(f"Error testing Docker Newman: {str(e)}")
            
        # Always return True to not block the server startup
        return True
            
    except Exception as e:
        logger.warning(f"Error initializing Docker Newman: {str(e)}")
        # Don't block server startup even if Newman initialization fails
        return True

def run():
    try:
        # Initialize Docker Newman (non-blocking)
        logger.info("Starting Docker Newman initialization (non-blocking)...")
        import threading
        newman_thread = threading.Thread(target=initialize_newman, daemon=True)
        newman_thread.start()
        
        from app.main import app
        
        print("✅ Successfully imported the FastAPI application!")
        print(f"App title: {app.title}")
        print(f"App version: {app.version}")
        
        # Start the server
        print("\nStarting FastAPI server on http://127.0.0.1:8001")
        print("Press Ctrl+C to stop the server\n")
        
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8001,
            reload=True,
            log_level="info"
        )
    
    except ImportError as e:
        print(f"❌ Error importing application: {e}")
        print("\nMake sure you're running this script from the backend directory and all dependencies are installed.")
        print("Try running: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    freeze_support()
    run()