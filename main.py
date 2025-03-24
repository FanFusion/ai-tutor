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
                        gr.Markdown(SYLLABUS_FORMAT)
                        
                        # Add status message with styling for different states
                        syllabus_status = gr.Markdown(
                            NO_SYLLABUS_STATUS,
                            elem_id="syllabus-status"
                        )
                        
                        # Add syllabus selector dropdown (initially empty)
                        with gr.Row():
                            syllabus_dropdown = gr.Dropdown(
                                label="Select Syllabus", 
                                choices=[], 
                                interactive=True,
                                elem_id="syllabus-dropdown",
                                visible=False
                            )
                        
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
                file_upload.change(
                    fn=syllabus_generator.handle_file_upload,
                    inputs=[file_upload],
                    outputs=[syllabus_chat]
                )
            
            # Second tab: Teaching Interface (will be enabled after syllabus generation)
            with gr.Tab("Teaching Session", id="teaching-tab") as teaching_tab:
                # Placeholder message when no syllabus is available
                placeholder_message = gr.Markdown(
                    PLACEHOLDER_MESSAGE,
                    visible=True, 
                    elem_id="placeholder_message"
                )
                
                # Teaching status indicator - initially hidden
                teaching_status = gr.Markdown(
                    SYLLABUS_LOADED_STATUS,
                    visible=False,
                    elem_id="teaching_status"
                )
                
                # Teaching interface container - initially hidden
                with gr.Row():
                        with gr.Column(scale=1):
                            gr.Markdown(TEACHING_TUTOR_DESCRIPTION)
                            
                            # Display current stage and progress
                            current_stage_display = gr.Markdown(TEACHING_STAGE_NOT_STARTED)
                            progress_display = gr.Markdown(TEACHING_PROGRESS_NOT_STARTED)
                            
                        with gr.Column(scale=2):

                            # Create teaching interface
                            logger.info("Setting up teaching interface")
                            teaching_chat, current_stage, stage_progress = create_teaching_interface(tutor_bot_service)
                        
                # Ensure stage indicators update properly
                current_stage.change(lambda x: x, current_stage, current_stage_display)
                stage_progress.change(lambda x: x, stage_progress, progress_display)
        
        # Modified function to update button interactive state and manage syllabi
        def check_for_syllabus_and_update_button(chat_history):
            """Check if chat history contains a valid syllabus and update button state
            
            Args:
                chat_history (list): Chat history from syllabus generator
                
            Returns:
                tuple: (syllabus_ready, syllabus_data, status_message, all_syllabi_updated, dropdown_update)
            """
            syllabus_json = None
            logger.info("Checking for syllabus in chat history")
            
            for _, bot_message in reversed(chat_history):
                # Look for JSON code block in bot messages
                if "```json" in bot_message:
                    # Extract JSON from code block
                    json_start = bot_message.find("```json\n") + 8
                    json_end = bot_message.find("```", json_start)
                    json_content = bot_message[json_start:json_end].strip()
                    
                    try:
                        syllabus_json = json.loads(json_content)
                        logger.info(f"Found potential syllabus JSON in chat history: {json.dumps(syllabus_json)[:200]}...")
                        
                        # Basic validation of the syllabus structure
                        if ("syllabus_name" in syllabus_json and 
                            "syllabus" in syllabus_json and 
                            isinstance(syllabus_json["syllabus"], list) and 
                            len(syllabus_json["syllabus"]) > 0):
                            
                            logger.info(f"Valid syllabus found in chat history with {len(syllabus_json['syllabus'])} stages")
                            syllabus_name = syllabus_json.get("syllabus_name", "Unknown")
                            audience = syllabus_json.get("target_audience", "")
                            
                            success_message = SUCCESS_SYLLABUS_TEMPLATE.format(
                                syllabus_name,
                                audience,
                                len(syllabus_json['syllabus'])
                            )
                            
                            # Update button state without directly manipulating the component
                            # We'll return interactive=True and let Gradio update it
                            
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
                            
                            # Create dropdown choices
                            dropdown_choices = [s.get("syllabus_name", "Unknown") for s in all_syllabi_updated]
                            
                            # Update dropdown
                            dropdown_update = gr.update(
                                choices=dropdown_choices,
                                value=syllabus_name,  # Set current syllabus as selected
                                visible=True
                            )
                            
                            return (
                                True,                  # syllabus_ready
                                syllabus_json,         # syllabus_data
                                success_message,       # status_message
                                all_syllabi_updated,   # all_syllabi_updated
                                dropdown_update        # dropdown_update
                            )
                        else:
                            logger.warning(f"Found JSON but it's not a valid syllabus. Keys: {list(syllabus_json.keys())}")
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse syllabus JSON from chat history: {str(e)}")
            
            # No valid syllabus found
            return (
                False,                          # syllabus_ready
                None,                           # syllabus_data
                ERROR_NO_SYLLABUS,              # status_message
                None,                           # all_syllabi_updated (no change)
                gr.update(visible=False)        # hide dropdown if no valid syllabus
            )
        
        # Function to handle syllabus selection from dropdown
        def handle_syllabus_selection(selection, all_syllabi):
            """Handle selection of a syllabus from the dropdown
            
            Args:
                selection (str): Name of the selected syllabus
                all_syllabi (list or State): List of all syllabi
                
            Returns:
                tuple: (syllabus_ready, syllabus_data, status_message)
            """
            logger.info(f"Handling syllabus selection: {selection}")
            
            # Extract actual list from State object if needed
            all_syllabi_val = all_syllabi.value if hasattr(all_syllabi, "value") else all_syllabi
            
            if not selection or not all_syllabi_val:
                return False, None, ERROR_NO_SELECTION
            
            # Find the selected syllabus in all_syllabi
            selected_syllabus = None
            for syllabus in all_syllabi_val:
                if syllabus.get("syllabus_name") == selection:
                    selected_syllabus = syllabus
                    break
            
            if not selected_syllabus:
                return False, None, ERROR_SELECTION_NOT_FOUND
            
            # Success - update the state with the selected syllabus
            syllabus_name = selected_syllabus.get("syllabus_name", "Unknown")
            audience = selected_syllabus.get("target_audience", "")
            
            success_message = SUCCESS_SYLLABUS_TEMPLATE.format(
                syllabus_name,
                audience,
                len(selected_syllabus.get("syllabus", []))
            )
            
            return True, selected_syllabus, success_message
        
        # Connect chat history to syllabus checking with the modified function
        syllabus_chat.change(
            fn=check_for_syllabus_and_update_button,
            inputs=[syllabus_chat],
            outputs=[
                syllabus_ready, 
                syllabus_data, 
                syllabus_status, 
                all_syllabi,
                syllabus_dropdown
            ]
        )
        
        # Connect syllabus dropdown to selection handler
        syllabus_dropdown.change(
            fn=handle_syllabus_selection,
            inputs=[syllabus_dropdown, all_syllabi],
            outputs=[syllabus_ready, syllabus_data, syllabus_status]
        )
        
        # Update button interactivity when syllabus_ready state changes
        syllabus_ready.change(
            lambda x: gr.update(interactive=x),
            inputs=[syllabus_ready],
            outputs=[start_teaching_btn]
        )
        
        # Function to handle the start teaching button click
        def handle_start_teaching(syllabus_ready, syllabus_data):
            # Extract values from State objects if needed 
            syllabus_ready_val = syllabus_ready.value if hasattr(syllabus_ready, "value") else syllabus_ready
            syllabus_data_val = syllabus_data.value if hasattr(syllabus_data, "value") else syllabus_data
            
            logger.info(f"Handling start teaching button click, syllabus_ready: {syllabus_ready_val} syllabus_data_val:{syllabus_data_val}")
            
            if syllabus_ready_val and syllabus_data_val:
                # Set syllabus for tutor bot
                try:
                    logger.info("Setting syllabus for tutor bot from state",syllabus_data_val)
                    tutor_bot_service.set_syllabus(syllabus_data_val)
                    return gr.Tabs(selected='teaching-tab')
                except Exception as e:
                    logger.error(f"Error setting syllabus from state: {str(e)}", exc_info=True)
            
            return gr.Tabs(selected='syllabus-tab')
    
        # Connect start teaching button to the handler function
        start_teaching_btn.click(
            fn=handle_start_teaching,
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