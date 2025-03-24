import gradio as gr
from app.components.chat_interface import create_chat_interface
from app.components.file_upload import create_file_upload
from app.services.syllabus_generator import SyllabusGenerator
from app.utils.vertex_ai_init import initialize_vertex_ai
from app.utils.env_loader import load_environment
from app.utils.gr_logger import setup_logger

# Setup logger for main module
logger = setup_logger(__name__)

def create_app():
    """Create and configure the Gradio app"""
    logger.info("Starting application initialization")
    
    # Load environment variables
    logger.info("Loading environment variables")
    load_environment()
    
    # Initialize Vertex AI
    logger.info("Initializing Vertex AI")
    initialize_vertex_ai()
    
    logger.info("Creating Gradio application interface")
    with gr.Blocks(title="Teaching Syllabus Generator") as app:
        gr.Markdown("# Teaching Syllabus Generator")
        gr.Markdown("Upload a document (PDF/TXT) to generate a structured teaching syllabus using Gemini AI's multimodal document processing.")
        
        with gr.Tab("Generate Syllabus"):
            with gr.Row():
                with gr.Column(scale=1):
                    # Create description
                    gr.Markdown("""
                    ## Instructions
                    
                    1. Upload your document using the file uploader below
                    2. Ask the AI to generate a syllabus
                    3. Provide instructions to modify the syllabus as needed
                    
                    The document will be processed using Gemini's multimodal capabilities (Part.from_uri),
                    allowing for direct analysis of PDFs and other document formats.
                    
                    The syllabus will be generated in a structured JSON format that follows a specific schema for teaching content.
                    """)
                    
                    # Create file upload component
                    logger.debug("Setting up file upload component")
                    file_upload = create_file_upload()
                    
                    # Add format information
                    gr.Markdown("""
                    ## Syllabus Format
                    
                    The generated syllabus includes:
                    - Course name and target audience
                    - Multiple learning stages with:
                      - Content description
                      - Allowed media types for learning
                      - Target learning objectives
                      - Teaching knowledge points
                      - Evaluation questions and answers
                    
                    Multimedia content can be specified using tags:
                    - `<image>description</image>`
                    - `<video>description</video>`
                    """)
                
                with gr.Column(scale=2):
                    # Create syllabus generator instance
                    logger.debug("Initializing syllabus generator")
                    syllabus_generator = SyllabusGenerator()
                    
                    # Create chat interface for interacting with the syllabus generator
                    logger.debug("Setting up chat interface")
                    chat_interface = create_chat_interface(syllabus_generator)
            
            # Connect file upload to chat component
            logger.debug("Connecting file upload to chat interface")
            file_upload.change(
                fn=syllabus_generator.handle_file_upload,
                inputs=[file_upload],
                outputs=[chat_interface]
            )
    
    logger.info("Application initialization complete")
    return app

if __name__ == "__main__":
    logger.info("Application startup")
    app = create_app()
    logger.info("Launching Gradio app")
    app.launch(server_name="0.0.0.0", server_port=8006) 