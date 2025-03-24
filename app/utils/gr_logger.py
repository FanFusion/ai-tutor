import logging
import os
import sys
from logging.handlers import RotatingFileHandler

def setup_logger(name=__name__, log_level=None):
    """
    Configure and return a logger instance with both console and file handlers
    
    Args:
        name (str): Logger name, defaults to module name
        log_level (str, optional): Log level, defaults to environment variable LOG_LEVEL or INFO
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Get log level from environment or use default
    if log_level is None:
        log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level))
    
    # Clear existing handlers to avoid duplicates
    if logger.handlers:
        logger.handlers.clear()
    
    # Create formatters
    console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # Create file handler (rotating log files)
    log_dir = os.environ.get('LOG_DIR', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    file_handler = RotatingFileHandler(
        f"{log_dir}/app.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    return logger 