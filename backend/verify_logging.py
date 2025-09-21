#!/usr/bin/env python3
"""
Simple verification script for queue-based logging.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent.absolute()
sys.path.insert(0, str(backend_path))

def test_queue_logging():
    """Test the queue-based logging system."""
    print("Testing queue-based logging system...")
    
    # Import and set up queue-based logging
    from app.core.logging_config import setup_queue_logging, get_queue_logger
    
    # Set up logging
    setup_queue_logging(log_level="INFO", log_dir="logs")
    logger = get_queue_logger(__name__)
    
    # Generate some test log messages
    logger.info("Queue-based logging system verification started")
    logger.debug("This is a debug message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    print("Log messages generated. Check the logs/app.log file for output.")
    logger.info("Queue-based logging system verification completed")

if __name__ == "__main__":
    test_queue_logging()