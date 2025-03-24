import gradio as gr
from app.components.chat_interface import create_chat_interface
from app.components.file_upload import create_file_upload
from app.components.teaching_interface import create_teaching_interface
from app.services.syllabus_generator import SyllabusGenerator
from app.services.tutor_bot_service import TutorBotService
from app.utils.vertex_ai_init import initialize_vertex_ai
from app.utils.env_loader import load_environment
from app.utils.gr_logger import setup_logger
from app.utils.const import *
import json

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
    with gr.Blocks(title=APP_TITLE, css=MAIN_CSS) as app:
        gr.Markdown(f"# {APP_TITLE}")
        gr.Markdown(APP_DESCRIPTION)
        
        # Create shared services
        logger.debug("Initializing services")
        syllabus_generator = SyllabusGenerator()
        tutor_bot_service = TutorBotService()
        
        # Create state to track if a valid syllabus has been generated
        syllabus_ready = gr.State(False)
        syllabus_data = gr.State(None)
        
        # Create state to store multiple syllabi
        all_syllabi = gr.State([])
        
        # Create tabs with a selector to track the current tab
        with gr.Tabs(elem_id="main_tabs", selected=0) as tabs:
            # First tab: Generate Syllabus
            with gr.Tab("Generate Syllabus", id="syllabus-tab") as syllabus_tab:
                with gr.Row():
                    with gr.Column(scale=1):
                        # Create description
                        gr.Markdown(SYLLABUS_DESCRIPTION)
                        logger.debug("Setting up file upload component")
                        file_upload = create_file_upload()
                        
                        # Add status message with styling for different states
                        syllabus_status = gr.Markdown(
                            NO_SYLLABUS_STATUS,
                            elem_id="syllabus-status"
                        )
                        
                        # Add collapsible section to display current syllabus details
                        with gr.Accordion("Current Syllabus", open=False, visible=False) as syllabus_details:
                            syllabus_info = gr.JSON(value=None, label="Syllabus Data")
                        
                        # Add start teaching button with enhanced styling
                        with gr.Row():
                            start_teaching_btn = gr.Button(
                                START_TEACHING_BTN_TEXT,
                                variant="primary", 
                                size="lg", 
                                interactive=False,
                                elem_classes="start-teaching-btn"
                            )
                    
                    with gr.Column(scale=2):
                        # Create chat interface for interacting with the syllabus generator
                        logger.debug("Setting up syllabus chat interface")
                        syllabus_chat = create_chat_interface(syllabus_generator)
                
                # Connect file upload to chat component
                logger.debug("Connecting file upload to chat interface")
                
                # Create file upload handler
                def create_file_upload_handler(sg):
                    """Create a handler for file uploads
                    
                    Args:
                        sg: SyllabusGenerator instance
                        
                    Returns:
                        function: A function that handles file uploads
                    """
                    def handle_file_upload(file):
                        return sg.handle_file_upload(file)
                    
                    return handle_file_upload
                
                # Create the handler with the syllabus generator
                file_upload_handler = create_file_upload_handler(syllabus_generator)
                
                file_upload.change(
                    fn=file_upload_handler,
                    inputs=[file_upload],
                    outputs=[syllabus_chat]
                )
            
            # Second tab: Teaching Interface (will be enabled after syllabus generation)
            with gr.Tab("Teaching Session", id="teaching-tab") as teaching_tab:
                # Teaching interface container - initially hidden
                with gr.Row():
                        with gr.Column(scale=1):
                            gr.Markdown(TEACHING_TUTOR_DESCRIPTION)
                        with gr.Column(scale=2):

                            # Create teaching interface
                            logger.info("Setting up teaching interface")
                            teaching_chat, current_stage, stage_progress = create_teaching_interface(tutor_bot_service)
        
        # Modified function to get the syllabus directly from the service
        def create_syllabus_getter(sg):
            """Create a function that gets syllabus from the provided generator
            
            Args:
                sg: SyllabusGenerator instance
                
            Returns:
                function: A function that gets syllabus when called
            """
            def get_syllabus_from_generator(chat_history):
                """Get the syllabus directly from the syllabus generator service
                
                Args:
                    chat_history: Chat history (not used, just for triggering)
                    
                Returns:
                    tuple: (syllabus_ready, syllabus_data, status_message, all_syllabi_updated, syllabus_info, syllabus_details_visible)
                """
                # Get the syllabus directly from the provided syllabus generator
                syllabus_json = sg.current_syllabus
                
                logger.info("Checking for syllabus from generator")
                
                if syllabus_json is None:
                    logger.info("No syllabus is available yet")
                    return (
                        False,                          # syllabus_ready
                        None,                           # syllabus_data
                        NO_SYLLABUS_STATUS,             # status_message
                        None,                           # all_syllabi_updated (no change)
                        None,                           # Empty JSON for JSON component
                        gr.update(visible=False)        # hide syllabus details
                    )
                
                # Basic validation of the syllabus structure
                if ("syllabus_name" in syllabus_json and 
                    "syllabus" in syllabus_json and 
                    isinstance(syllabus_json["syllabus"], list) and 
                    len(syllabus_json["syllabus"]) > 0):
                    
                    logger.info(f"Valid syllabus found with {len(syllabus_json['syllabus'])} stages: {syllabus_json.get('syllabus_name', 'Unknown')}")
                    syllabus_name = syllabus_json.get("syllabus_name", "Unknown")
                    audience = syllabus_json.get("target_audience", "")
                    
                    success_message = SUCCESS_SYLLABUS_TEMPLATE.format(
                        syllabus_name,
                        audience,
                        len(syllabus_json['syllabus'])
                    )
                    
                    # Update all_syllabi state
                    def update_syllabi_list(all_syllabi_list, new_syllabus):
                        # Create a copy of the all_syllabi list
                        updated_list = list(all_syllabi_list.value) if all_syllabi_list is not None and hasattr(all_syllabi_list, "value") else []
                        
                        # Check if this syllabus already exists (by name)
                        exists = False
                        for i, existing_syllabus in enumerate(updated_list):
                            if existing_syllabus.get("syllabus_name") == new_syllabus.get("syllabus_name"):
                                # Replace with newer version
                                updated_list[i] = new_syllabus
                                exists = True
                                break
                        
                        # Add if it doesn't exist
                        if not exists:
                            updated_list.append(new_syllabus)
                        
                        return updated_list
                    
                    # Get updated syllabi list
                    all_syllabi_updated = update_syllabi_list(all_syllabi, syllabus_json)
                    
                    return (
                        True,                             # syllabus_ready
                        syllabus_json,                    # syllabus_data
                        success_message,                  # status_message
                        all_syllabi_updated,              # all_syllabi_updated
                        syllabus_json,                    # Pass JSON directly for display
                        gr.update(visible=True, open=True) # show syllabus details
                    )
                else:
                    logger.warning(f"Found JSON but it's not a valid syllabus. Keys: {list(syllabus_json.keys())}")
                    return (
                        False,                          # syllabus_ready
                        None,                           # syllabus_data
                        ERROR_NO_SYLLABUS,              # status_message
                        None,                           # all_syllabi_updated (no change)
                        None,                           # Empty JSON for JSON component
                        gr.update(visible=False)        # hide syllabus details
                    )
            
            return get_syllabus_from_generator
        
        # Create the function with the syllabus generator as its closure
        get_syllabus_handler = create_syllabus_getter(syllabus_generator)
        
        # Connect chat history to syllabus checking with the new function
        syllabus_chat.change(
            fn=get_syllabus_handler,
            inputs=[syllabus_chat],
            outputs=[
                syllabus_ready, 
                syllabus_data, 
                syllabus_status, 
                all_syllabi,
                syllabus_info,
                syllabus_details
            ]
        )
        
        # Update button interactivity when syllabus_ready state changes
        syllabus_ready.change(
            lambda x: gr.update(interactive=x),
            inputs=[syllabus_ready],
            outputs=[start_teaching_btn]
        )
        
        # Create a handler for updating button state based on syllabus data
        def create_button_update_handler():
            """Create a handler function for updating button state
            
            Returns:
                function: A function that updates button state
            """
            def get_button_update(syllabus_data):
                """Update button interactivity based on syllabus data
                
                Args:
                    syllabus_data: Syllabus data to check
                    
                Returns:
                    gr.update: Update for button interactivity
                """
                is_valid = (syllabus_data is not None and 
                          "syllabus_name" in syllabus_data and 
                          "syllabus" in syllabus_data)
                return gr.update(interactive=is_valid)
            
            return get_button_update
        
        # Create the button update handler
        button_update_handler = create_button_update_handler()
        
        # For immediate button update when syllabus is ready (directly after checking syllabus)
        syllabus_data.change(
            fn=button_update_handler,
            inputs=[syllabus_data],
            outputs=[start_teaching_btn]
        )
        
        # Function to handle the start teaching button click
        def create_teaching_handler(tutor_service):
            """Create a handler function for the start teaching button
            
            Args:
                tutor_service: TutorBotService instance
                
            Returns:
                function: A function that handles the start teaching button click
            """
            def handle_start_teaching(syllabus_ready, syllabus_data):
                # Extract values from State objects if needed 
                syllabus_ready_val = syllabus_ready.value if hasattr(syllabus_ready, "value") else syllabus_ready
                syllabus_data_val = syllabus_data.value if hasattr(syllabus_data, "value") else syllabus_data
                
                logger.info(f"Handling start teaching button click, syllabus_ready: {syllabus_ready_val}")
                
                if syllabus_ready_val and syllabus_data_val:
                    # Set syllabus for tutor bot
                    try:
                        syllabus_name = syllabus_data_val.get('syllabus_name', 'Unknown')
                        stages_count = len(syllabus_data_val.get('syllabus', []))
                        logger.info(f"Setting syllabus for tutor bot: '{syllabus_name}' with {stages_count} stages")
                        
                        tutor_service.set_syllabus(syllabus_data_val)
                        return gr.Tabs(selected='teaching-tab')
                    except Exception as e:
                        logger.error(f"Error setting syllabus from state: {str(e)}", exc_info=True)
                else:
                    logger.warning("Cannot start teaching: No valid syllabus available")
                
                return gr.Tabs(selected='syllabus-tab')
            
            return handle_start_teaching
        
        # Create the handler with the tutor bot service
        teaching_handler = create_teaching_handler(tutor_bot_service)
    
        # Connect start teaching button to the handler function
        start_teaching_btn.click(
            fn=teaching_handler,
            inputs=[syllabus_ready, syllabus_data],
            outputs=tabs
        )
    
    logger.info("Application initialization complete")
    return app

if __name__ == "__main__":
    logger.info("Application startup")
    app = create_app()
    logger.info("Launching Gradio app")
    app.launch(server_name="0.0.0.0", server_port=8006) 