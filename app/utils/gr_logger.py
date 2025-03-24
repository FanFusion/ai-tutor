import logging
import os
import sys
from datetime import datetime

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure the root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"logs/app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)

def setup_logger(name):
    """Set up a logger for a module
    
    Args:
        name (str): Name of the module
        
    Returns:
        logging.Logger: Logger instance
    """
    logger = logging.getLogger(name)
    return logger 