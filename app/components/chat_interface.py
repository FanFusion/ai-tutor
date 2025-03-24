import gradio as gr
from app.utils.gr_logger import setup_logger
from app.utils.const import *

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
    
    # Add descriptive message
    info_text = gr.Markdown(CHAT_INTERFACE_DESCRIPTION)
    
    # Create message input
    msg = gr.Textbox(
        placeholder=CHAT_PLACEHOLDER,
        container=False
    )
    
    # Create buttons for chat interaction
    with gr.Row():
        send_btn = gr.Button(SEND_BTN_TEXT, variant="primary", scale=3)
        clear = gr.Button(CLEAR_BTN_TEXT, scale=1)
    
    # Add example prompts for users
    examples = CHAT_EXAMPLE_PROMPTS
    logger.debug(f"Configured {len(examples)} example prompts")
    
    # Define chat submit function
    def respond(message, chat_history):
        logger.info(f"User message received: {message}")
        
        if not syllabus_generator.document_uploaded:
            logger.warning("Document not uploaded, prompting user")
            chat_history.append((message, NO_DOCUMENT_ERROR))
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
    send_btn.click(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)
    
    # Add examples
    gr.Examples(
        examples=examples,
        inputs=msg
    )
    
    logger.info("Chat interface created successfully")
    return chatbot 