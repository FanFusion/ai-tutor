import os
import vertexai
from app.utils.gr_logger import setup_logger

# Setup logger for the module
logger = setup_logger(__name__)

def initialize_vertex_ai():
    """Initialize Vertex AI with project and location from environment variables"""
    project_id = os.environ.get('VERTEX_PROJECT_ID', 'funplus-ai')
    location = os.environ.get('VERTEX_LOCATION', 'asia-east2')
    
    logger.info(f"Initializing Vertex AI with project: {project_id}, location: {location}")
    vertexai.init(project=project_id, location=location)
    logger.info("Vertex AI initialization complete") 