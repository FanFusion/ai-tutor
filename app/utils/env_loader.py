import os
from dotenv import load_dotenv
from app.utils.gr_logger import setup_logger

# Setup logger for the module
logger = setup_logger(__name__)

def load_environment():
    """Load environment variables from .env file"""
    logger.info("Loading environment variables from .env file")
    load_dotenv()
    
    # Check if required environment variables are set
    required_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'S3_BUCKET_NAME'
    ]
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.warning(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.warning("S3 file upload functionality may not work correctly.")
    else:
        logger.info("All required environment variables are set")
        
    return True 