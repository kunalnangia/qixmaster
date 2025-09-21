#!/usr/bin/env python3
"""
Comprehensive test for queue-based logging.
"""

import sys
import time
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent.absolute()
sys.path.insert(0, str(backend_path))

def test_logging():
    """Test the logging system."""
    print("Setting up queue-based logging...")
    
    # Import and set up queue-based logging
    from app.core.logging_config import setup_queue_logging, get_queue_logger
    
    # Set up logging
    setup_queue_logging(log_level="INFO", log_dir="logs")
    
    # Get a logger for this module
    test_logger = get_queue_logger("comprehensive_log_test")
    
    # Generate some test log messages
    test_logger.info("Comprehensive logging test started")
    test_logger.debug("This is a debug message")
    test_logger.warning("This is a warning message")
    test_logger.error("This is an error message")
    test_logger.critical("This is a critical message")
    
    # Wait a moment to ensure messages are processed
    time.sleep(1)
    
    print("Log messages generated. Check the logs/app.log file for output.")
    test_logger.info("Comprehensive logging test completed")

if __name__ == "__main__":
    test_logging()