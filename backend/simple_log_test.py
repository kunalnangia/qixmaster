#!/usr/bin/env python3
"""
Simple test for queue-based logging.
"""

import sys
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
    logger = setup_queue_logging(log_level="INFO", log_dir="logs")
    
    # Get a logger for this module
    test_logger = get_queue_logger("simple_log_test")
    
    # Generate some test log messages
    test_logger.info("Simple logging test started")
    test_logger.warning("This is a warning message")
    test_logger.error("This is an error message")
    
    print("Log messages generated. Check the logs/app.log file for output.")
    test_logger.info("Simple logging test completed")

if __name__ == "__main__":
    test_logging()