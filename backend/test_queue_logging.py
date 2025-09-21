#!/usr/bin/env python3
"""
Test script for queue-based logging configuration.
"""

import os
import sys
import time
import logging
import threading
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent.absolute()
sys.path.insert(0, str(backend_path))

def test_worker(worker_id: int, logger: logging.Logger) -> None:
    """Simulate a worker that generates log messages."""
    for i in range(5):
        logger.info(f"Worker {worker_id} - Log message {i+1}")
        logger.debug(f"Worker {worker_id} - Debug message {i+1}")
        logger.warning(f"Worker {worker_id} - Warning message {i+1}")
        time.sleep(0.1)

def main() -> None:
    """Test the queue-based logging system with multiple threads."""
    print("Testing queue-based logging system...")
    
    # Import and set up queue-based logging
    from app.core.logging_config import setup_queue_logging, get_queue_logger
    
    # Set up logging
    setup_queue_logging(log_level="DEBUG", log_dir="logs")
    logger = get_queue_logger(__name__)
    
    logger.info("Starting queue-based logging test")
    
    # Create multiple worker threads
    threads = []
    for i in range(3):
        thread = threading.Thread(target=test_worker, args=(i, get_queue_logger(f"worker-{i}")))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    logger.info("Queue-based logging test completed")
    print("Test completed. Check the logs/app.log file for output.")

if __name__ == "__main__":
    main()