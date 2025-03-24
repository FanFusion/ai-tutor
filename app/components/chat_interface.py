import gradio as gr
from app.utils.gr_logger import setup_logger

logger = setup_logger(__name__)

def create_chat_interface(syllabus_generator):
    """Create a chat interface component for interacting with the syllabus generator
    
    Args:
        syllabus_generator: Instance of SyllabusGenerator class
        
    Returns:
        Gradio Chatbot component
    """
    logger.info("Creating chat interface")
    
    # Create chatbot component
    chatbot = gr.Chatbot(height=500)
    logger.debug("Initialized chatbot component")
    
    # Create message input
    msg = gr.Textbox(
        placeholder="Chat with the AI about your teaching syllabus...",
        container=False
    )
    
    # Create clear button
    clear = gr.Button("Clear")
    
    # Add descriptive message
    info_text = gr.Markdown("""
    ## Teaching Syllabus Generator
    
    This chatbot can generate and modify teaching syllabuses based on uploaded documents.
    
    **Usage Instructions:**
    1. Upload a document (PDF/TXT) using the file upload component
    2. Ask the chatbot to generate a syllabus from the document
    3. Modify the syllabus by providing specific instructions
    
    The syllabus follows a structured JSON format with stages, each containing:
    - Stage ID and description
    - Allowed media types for evaluation
    - Learning targets and knowledge points
    - Evaluation questions and answers
    """)
    
    # Add example prompts for users
    examples = [
        "Generate a teaching syllabus from my uploaded document",
        "Change the target audience to 'middle school students (12-14 years)'",
        "Add a new stage about advanced topics at the end of the syllabus",
        "Update the teaching knowledge in stage 1 to include 'introduction to basic concepts'",
        "Add more media types like 'video' to stage 2",
        "Make the judge question in stage 3 more challenging",
        "Add an image illustrating the concept in the first stage"
    ]
    logger.debug(f"Configured {len(examples)} example prompts")
    
    # Define chat submit function
    def respond(message, chat_history):
        logger.info(f"User message received: {message}")
        
        if not syllabus_generator.document_uploaded:
            logger.warning("Document not uploaded, prompting user")
            chat_history.append((message, "Please upload a document first to generate a syllabus."))
            return "", chat_history
        
        # Get response from syllabus generator
        logger.debug("Processing message through syllabus generator")
        response = syllabus_generator.process_message(message)
        chat_history.append((message, response))
        logger.debug(f"Response generated, history length: {len(chat_history)}")
        return "", chat_history
    
    # Connect components
    logger.debug("Connecting chat interface components")
    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)
    
    # Add examples
    gr.Examples(
        examples=examples,
        inputs=msg,
    )
    
    logger.info("Chat interface created successfully")
    return chatbot 