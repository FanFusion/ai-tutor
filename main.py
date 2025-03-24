import gradio as gr
from app.components.chat_interface import create_chat_interface
from app.components.file_upload import create_file_upload
from app.components.teaching_interface import create_teaching_interface
from app.services.syllabus_generator import SyllabusGenerator
from app.services.tutor_bot_service import TutorBotService
from app.utils.vertex_ai_init import initialize_vertex_ai
from app.utils.env_loader import load_environment
from app.utils.gr_logger import setup_logger
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
    with gr.Blocks(title="Teaching Syllabus Generator and Tutor", css="""
        #teaching_interface_container { 
            display: none; 
        }
        #teaching_interface_container.visible { 
            display: block; 
        }
        #placeholder_message.hidden {
            display: none;
        }
        /* Custom style for the start teaching button */
        .start-teaching-btn {
            font-weight: bold !important;
            padding: 12px 20px !important;
        }
    """) as app:
        gr.Markdown("# Teaching Syllabus Generator and Tutor")
        gr.Markdown("Generate a teaching syllabus from a document and use it for interactive teaching.")
        
        # Create shared services
        logger.debug("Initializing services")
        syllabus_generator = SyllabusGenerator()
        tutor_bot_service = TutorBotService()
        
        # Create state to track if a valid syllabus has been generated
        syllabus_ready = gr.State(False)
        syllabus_data = gr.State(None)
        
        # Create tabs with a selector to track the current tab
        with gr.Tabs(elem_id="main_tabs", selected=0) as tabs:
            # First tab: Generate Syllabus
            with gr.Tab("Generate Syllabus", id="syllabus-tab") as syllabus_tab:
                with gr.Row():
                    with gr.Column(scale=1):
                        # Create description
                        gr.Markdown("""
                        ## Instructions
                        
                        1. Upload your document using the file uploader below
                        2. Ask the AI to generate a syllabus
                        3. Provide instructions to modify the syllabus as needed
                        
                        The document will be processed using Gemini's multimodal capabilities,
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
                        
                        # Add status message and start teaching button
                        syllabus_status = gr.Markdown("**Status**: No syllabus generated yet. Please generate a syllabus first.")
                        start_teaching_btn = gr.Button(
                            "Start Teaching", 
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
            with gr.Tab("Teaching Session", id="teaching-tab"):
                # Placeholder message when no syllabus is available
                placeholder_message = gr.Markdown(
                    "### Please generate a syllabus in the 'Generate Syllabus' tab first before starting the teaching session.",
                    visible=True, 
                    elem_id="placeholder_message"
                )
                
                # Teaching status indicator - initially hidden
                teaching_status = gr.Markdown(
                    "**Status**: Syllabus loaded successfully. You can now start the teaching session.",
                    visible=False,
                    elem_id="teaching_status"
                )
                
                # Teaching interface container - initially hidden
                with gr.Group(visible=False, elem_id="teaching_interface_container") as teaching_container:
                    with gr.Row():
                        with gr.Column(scale=1):
                            gr.Markdown("""
                            ## Teaching Session
                            
                            This is an interactive teaching session based on the syllabus you generated.
                            
                            The AI tutor will guide you through each stage of the syllabus, providing:
                            - Explanations of concepts
                            - Answers to your questions
                            - Evaluation of your answers to questions
                            
                            Use the controls below to:
                            - Start/end the teaching session
                            - Navigate between stages
                            - Add multimedia descriptions in your responses
                            """)
                            
                            # Display current stage and progress
                            current_stage_display = gr.Markdown("### Current Stage: Not started")
                            progress_display = gr.Markdown("### Progress: 0/0 stages")
                            
                        with gr.Column(scale=2):
                            # Create teaching interface
                            logger.debug("Setting up teaching interface")
                            teaching_chat, current_stage, stage_progress = create_teaching_interface(tutor_bot_service)
                            
                    # Ensure stage indicators update properly
                    current_stage.change(lambda x: x, current_stage, current_stage_display)
                    stage_progress.change(lambda x: x, stage_progress, progress_display)
        
        # Function to check for syllabus in chat history
        def check_for_syllabus(chat_history):
            """Check if chat history contains a valid syllabus
            
            Args:
                chat_history (list): Chat history from syllabus generator
                
            Returns:
                tuple: (syllabus_ready, syllabus_data, status_message, button_interactive)
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
                            return (
                                True, 
                                syllabus_json, 
                                "**Status**: Syllabus generated successfully! Click 'Start Teaching' to begin the teaching session.", 
                                {"interactive": True, "__type__": "update"}
                            )
                        else:
                            logger.warning(f"Found JSON but it's not a valid syllabus. Keys: {list(syllabus_json.keys())}")
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse syllabus JSON from chat history: {str(e)}")
            
            return (
                False, 
                None, 
                "**Status**: No valid syllabus found. Please generate a syllabus first.", 
                {"interactive": False, "__type__": "update"}
            )
        
        # Function to switch to teaching tab and set syllabus
        def switch_to_teaching(chat_history, syllabus_ready, syllabus_data):
            """Switch to teaching tab and set syllabus for tutor bot
            
            Args:
                chat_history (list): Chat history from syllabus generator
                syllabus_ready (bool): Whether a valid syllabus has been generated
                syllabus_data (dict): The syllabus data if already parsed
                
            Returns:
                tuple: (tabs_update, placeholder_update, teaching_status_update, container_update)
            """
            logger.info(f"Switching to teaching tab, syllabus_ready: {syllabus_ready}")
            
            try:
                # Case 1: We already have valid syllabus data from state
                if syllabus_ready and syllabus_data:
                    try:
                        # Set syllabus for tutor bot
                        logger.info("Setting syllabus for tutor bot from state")
                        tutor_bot_service.set_syllabus(syllabus_data)
                        
                        # Generate status message with syllabus info
                        syllabus_name = syllabus_data.get("syllabus_name", "Unknown")
                        status_msg = f"**Status**: Syllabus '{syllabus_name}' loaded successfully. You can now start the teaching session."
                        
                        # Switch to teaching tab (index 1) and show interface
                        return (
                            gr.Tabs.update(selected=1),
                            gr.Markdown.update(visible=False),
                            gr.Markdown.update(visible=True, value=status_msg),
                            gr.Group.update(visible=True)
                        )
                    except Exception as e:
                        logger.error(f"Error setting syllabus from state: {str(e)}", exc_info=True)
                
                # Case 2: Try to find a syllabus in the chat history
                ready, data, _, _ = check_for_syllabus(chat_history)
                
                if ready and data:
                    try:
                        # Set syllabus for tutor bot
                        logger.info("Setting syllabus for tutor bot from chat history")
                        tutor_bot_service.set_syllabus(data)
                        
                        # Generate status message with syllabus info
                        syllabus_name = data.get("syllabus_name", "Unknown")
                        status_msg = f"**Status**: Syllabus '{syllabus_name}' loaded successfully. You can now start the teaching session."
                        
                        # Switch to teaching tab (index 1) and show interface
                        return (
                            gr.Tabs.update(selected=1),
                            gr.Markdown.update(visible=False),
                            gr.Markdown.update(visible=True, value=status_msg),
                            gr.Group.update(visible=True)
                        )
                    except Exception as e:
                        logger.error(f"Error setting syllabus from chat history: {str(e)}", exc_info=True)
                
                # Case 3: No valid syllabus found or error occurred
                logger.warning("No valid syllabus found or error setting syllabus, staying on current tab")
                # Stay on current tab (index 0) and show placeholder
                return (
                    gr.Tabs.update(selected=0),
                    gr.Markdown.update(visible=True),
                    gr.Markdown.update(visible=False),
                    gr.Group.update(visible=False)
                )
                
            except Exception as e:
                logger.error(f"Unexpected error in switch_to_teaching: {str(e)}", exc_info=True)
                # Stay on current tab (index 0) and show placeholder
                return (
                    gr.Tabs.update(selected=0),
                    gr.Markdown.update(visible=True),
                    gr.Markdown.update(visible=False),
                    gr.Group.update(visible=False)
                )
        
        # Connect chat history to syllabus checking
        syllabus_chat.change(
            fn=check_for_syllabus,
            inputs=[syllabus_chat],
            outputs=[syllabus_ready, syllabus_data, syllabus_status, start_teaching_btn]
        )
        
        # Connect start teaching button
        start_teaching_btn.click(
            fn=switch_to_teaching,
            inputs=[syllabus_chat, syllabus_ready, syllabus_data],
            outputs=[tabs, placeholder_message, teaching_status, teaching_container]
        )
    
    logger.info("Application initialization complete")
    return app

if __name__ == "__main__":
    logger.info("Application startup")
    app = create_app()
    logger.info("Launching Gradio app")
    app.launch(server_name="0.0.0.0", server_port=8006) 