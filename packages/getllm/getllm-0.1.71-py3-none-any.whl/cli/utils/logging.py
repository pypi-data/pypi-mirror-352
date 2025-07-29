"""Logging utilities for the CLI."""
import os
import logging
import logging.handlers
import datetime
from typing import Optional

def configure_logging(debug: bool = False, log_file: Optional[str] = None) -> None:
    """Configure logging for the CLI.
    
    Args:
        debug: Enable debug logging
        log_file: Path to log file. If None, uses default location.
    """
    # Create logger
    logger = logging.getLogger('getllm')
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Add file handler if log file is specified
    if log_file:
        os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


def get_default_log_file() -> str:
    """Get the default log file path.
    
    Returns:
        str: Path to the default log file
    """
    log_dir = os.path.join(os.path.expanduser('~'), '.getllm', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    return os.path.join(
        log_dir,
        f'getllm_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    )
