"""
Queue-based logging configuration for multiprocess safety.

This module implements a queue-based logging system that is safe for use with multiple workers.
Each worker puts log records into a multiprocessing.Queue, and a single log listener process/thread
writes them to the file, avoiding lock contention entirely.
"""

import os
import logging
import logging.handlers
import multiprocessing
import atexit
import threading
from typing import Optional
from pathlib import Path

# Global variables for the logging queue and listener
_log_queue: Optional[multiprocessing.Queue] = None
_queue_listener: Optional[logging.handlers.QueueListener] = None
_listener_thread: Optional[threading.Thread] = None

# Lock for thread-safe initialization
_init_lock = threading.Lock()

def _get_log_queue() -> multiprocessing.Queue:
    """Get or create the global log queue."""
    global _log_queue
    if _log_queue is None:
        with _init_lock:
            if _log_queue is None:
                _log_queue = multiprocessing.Queue()
    return _log_queue

def _setup_queue_listener(log_dir: str = "logs") -> None:
    """Set up the queue listener to write logs to files."""
    global _queue_listener, _listener_thread
    
    if _queue_listener is not None:
        # Already set up
        return
    
    with _init_lock:
        if _queue_listener is not None:
            # Double-check pattern to avoid race conditions
            return
            
        # Create logs directory if it doesn't exist
        Path(log_dir).mkdir(exist_ok=True)
        
        # Set up file handlers with rotation
        try:
            from concurrent_log_handler import ConcurrentRotatingFileHandler
            file_handler = ConcurrentRotatingFileHandler(
                os.path.join(log_dir, "app.log"),
                maxBytes=10*1024*1024,  # 10 MB
                backupCount=5
            )
            listener_info = "Using ConcurrentRotatingFileHandler for multiprocess-safe logging"
        except ImportError:
            # Fallback to standard RotatingFileHandler
            file_handler = logging.handlers.RotatingFileHandler(
                os.path.join(log_dir, "app.log"),
                maxBytes=10*1024*1024,  # 10 MB
                backupCount=5
            )
            listener_info = "Using RotatingFileHandler (concurrent-log-handler not available)"
        
        # Set up console handler
        console_handler = logging.StreamHandler()
        
        # Create formatters
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(process)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        file_handler.setFormatter(file_formatter)
        console_handler.setFormatter(console_formatter)
        
        # Create and start the queue listener
        log_queue = _get_log_queue()
        _queue_listener = logging.handlers.QueueListener(
            log_queue,
            file_handler,
            console_handler,
            respect_handler_level=True
        )
        
        # Start the listener in a separate thread
        _listener_thread = threading.Thread(target=_queue_listener.start, daemon=True)
        _listener_thread.start()
        
        # Register cleanup function
        atexit.register(stop_queue_listener)
        
        # Log the setup info
        setup_logger = logging.getLogger(__name__)
        queue_handler = logging.handlers.QueueHandler(log_queue)
        setup_logger.addHandler(queue_handler)
        setup_logger.setLevel(logging.INFO)
        setup_logger.info(f"Queue-based logging initialized. {listener_info}")

def stop_queue_listener() -> None:
    """Stop the queue listener gracefully."""
    global _queue_listener, _listener_thread
    
    if _queue_listener is not None:
        _queue_listener.stop()
        _queue_listener = None
        
    if _listener_thread is not None:
        _listener_thread = None

def setup_queue_logging(log_level: str = "INFO", log_dir: str = "logs") -> logging.Logger:
    """
    Set up queue-based logging for the application.
    
    Args:
        log_level: The logging level (e.g., "DEBUG", "INFO", "WARNING", "ERROR")
        log_dir: Directory where log files should be stored
        
    Returns:
        Configured logger instance
    """
    # Set up the queue listener (only once)
    _setup_queue_listener(log_dir)
    
    # Get the log queue
    log_queue = _get_log_queue()
    
    # Create queue handler
    queue_handler = logging.handlers.QueueHandler(log_queue)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Clear any existing handlers from root logger
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add queue handler to root logger
    root_logger.addHandler(queue_handler)
    
    # Also configure this module's logger
    logger = logging.getLogger(__name__)
    logger.addHandler(queue_handler)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    return logger

# Convenience function for getting a logger that uses the queue
def get_queue_logger(name: str) -> logging.Logger:
    """
    Get a logger that uses the queue-based logging system.
    
    Args:
        name: Name of the logger
        
    Returns:
        Logger instance configured to use queue-based logging
    """
    # Get the log queue
    log_queue = _get_log_queue()
    
    # Create queue handler
    queue_handler = logging.handlers.QueueHandler(log_queue)
    
    # Create and configure logger
    logger = logging.getLogger(name)
    logger.addHandler(queue_handler)
    logger.setLevel(logging.getLogger().level)  # Inherit level from root logger
    
    return logger