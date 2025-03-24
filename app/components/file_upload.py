import gradio as gr
from app.utils.gr_logger import setup_logger

logger = setup_logger(__name__)

def create_file_upload():
    """Create a file upload component for handling document uploads
    
    Returns:
        Gradio File component: The file upload component
    """
    logger.info("Creating file upload component")
    
    # Create file upload component
    file_upload = gr.File(
        label="Upload Document",
        file_types=[".pdf", ".txt"],
        file_count="single",
        type="filepath",
        elem_id="document-upload"
    )
    
    logger.debug("File upload component configured with types: [.pdf, .txt]")
    
    # Add guidance about supported file types
    gr.Markdown("""
    ### Supported Document Formats
    
    - PDF documents (recommended for best results)
    - Text files (.txt)
    
    """)
    
    logger.info("File upload component created successfully")
    return file_upload 