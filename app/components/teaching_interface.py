import gradio as gr
import re
from app.utils.gr_logger import setup_logger
from app.utils.const import *

logger = setup_logger(__name__)

def create_teaching_interface(tutor_bot_service):
    """Create a teaching interface for interacting with the tutor bot
    
    Args:
        tutor_bot_service: Instance of TutorBotService
        
    Returns:
        tuple: The teaching interface components
    """
    logger.info("Creating teaching interface")
    
    # Create chatbot component for the teaching interaction
    chatbot = gr.Chatbot(
        height=400,
        elem_id="teaching-chatbot",
        show_label=False,
        avatar_images=("./app/assets/user.png", "./app/assets/bot.png")
    )
    
        # Create message input and send button in a row
    with gr.Row():
        msg = gr.Textbox(
            placeholder=TEACHING_CHAT_PLACEHOLDER,
            container=False,
            scale=7
        )
        send_btn = gr.Button(SEND_BTN_TEXT, variant="primary", scale=1)

    # Create stage indicators
    current_stage = gr.Markdown(TEACHING_STAGE_NOT_STARTED)
    stage_progress = gr.Markdown(TEACHING_PROGRESS_NOT_STARTED)
    
    # Create admin control buttons
    with gr.Row():
        start_btn = gr.Button(START_TEACHING_TEXT, variant="primary")
        next_stage_btn = gr.Button(NEXT_STAGE_TEXT)
        prev_stage_btn = gr.Button(PREV_STAGE_TEXT)
        end_btn = gr.Button(END_TEACHING_TEXT, variant="stop")
    
    # Create multimedia input buttons
    with gr.Row():
        gr.Markdown("### Add Interaction:")
        interaction_btn = gr.Button("💬 Add Interaction")
    
    # Add example questions
    example_questions = TEACHING_EXAMPLE_QUESTIONS
    
    # Define chat submit function for user messages
    def user_message_submit(message, chat_history):
        logger.info(f"User message submitted: {message}")
        
        if not message:
            return "", chat_history
        
        if not tutor_bot_service.syllabus_info:
            logger.warning("No syllabus available for teaching")
            chat_history.append((message, NO_SYLLABUS_TEACHING_ERROR))
            return "", chat_history
            
        updated_chat_history, stage_updated = tutor_bot_service.process_message("user", message, chat_history)
        
        # Update stage indicator if needed
        update_stage_indicators()
        
        return "", updated_chat_history
    
    # Define functions for admin commands
    def start_teaching(chat_history):
        logger.info("Starting teaching session")
        
        if not tutor_bot_service.syllabus_info:
            logger.warning("No syllabus available for teaching")
            chat_history.append(("", NO_SYLLABUS_TEACHING_ERROR))
            return chat_history
            
        updated_chat_history = tutor_bot_service.start_teaching(chat_history)
        update_stage_indicators()
        return updated_chat_history
    
    def end_teaching(chat_history):
        logger.info("Ending teaching session")
        
        if not tutor_bot_service.syllabus_info:
            return chat_history
            
        updated_chat_history = tutor_bot_service.end_teaching(chat_history)
        return updated_chat_history
    
    def next_stage(chat_history):
        logger.info("Moving to next stage")
        
        if not tutor_bot_service.syllabus_info:
            logger.warning("No syllabus available for teaching")
            chat_history.append(("", NO_SYLLABUS_TEACHING_ERROR))
            return chat_history
            
        updated_chat_history, _ = tutor_bot_service.process_message("admin", "next stage", chat_history)
        update_stage_indicators()
        return updated_chat_history
    
    def prev_stage(chat_history):
        logger.info("Moving to previous stage")
        
        if not tutor_bot_service.syllabus_info:
            logger.warning("No syllabus available for teaching")
            chat_history.append(("", NO_SYLLABUS_TEACHING_ERROR))
            return chat_history
            
        updated_chat_history, _ = tutor_bot_service.process_message("admin", "previous stage", chat_history)
        update_stage_indicators()
        return updated_chat_history
    
    def update_stage_indicators():
        """Update the stage indicators"""
        if tutor_bot_service.syllabus_info and tutor_bot_service.is_teaching_started:
            try:
                print(f"update_stage_indicators:",tutor_bot_service.current_stage_index )
                current_stage_info = tutor_bot_service.syllabus_info["syllabus"][tutor_bot_service.current_stage_index]
                stage_id = current_stage_info.get("stage_id", "Unknown")
                stage_description = current_stage_info.get("stage_description", "")
                total_stages = len(tutor_bot_service.syllabus_info["syllabus"])
                current_stage_num = tutor_bot_service.current_stage_index + 1
                
                current_stage_md = f"### Current Stage: {stage_id} - {stage_description}"
                progress_md = f"### Progress: {current_stage_num}/{total_stages} stages"
                return current_stage_md, progress_md
            except (IndexError, KeyError) as e:
                logger.error(f"Error updating stage indicators: {str(e)}")
                return TEACHING_STAGE_ERROR, TEACHING_PROGRESS_ERROR
        else:
            return TEACHING_STAGE_NOT_STARTED, TEACHING_PROGRESS_NOT_STARTED
    
    # Helper functions for multimedia input
    def add_interaction_tag(message):
        logger.debug("Adding interaction tag to message")
        return message + " [interaction][/interaction]"
    
    # Connect components
    msg.submit(user_message_submit, [msg, chatbot], [msg, chatbot])
    
    # Connect send button to submit function
    send_btn.click(user_message_submit, [msg, chatbot], [msg, chatbot])
 
    # Connect admin buttons
    start_btn.click(start_teaching, [chatbot], [chatbot])
    next_stage_btn.click(next_stage, [chatbot], [chatbot])
    prev_stage_btn.click(prev_stage, [chatbot], [chatbot])
    end_btn.click(end_teaching, [chatbot], [chatbot])
    
    # Connect multimedia buttons to message input
    interaction_btn.click(add_interaction_tag, [msg], [msg])
    
    # Connect stage indicators update
    # for btn in [start_btn, next_stage_btn, prev_stage_btn,send_btn]:
    #     btn.click(update_stage_indicators, None, [current_stage, stage_progress])
    chatbot.change(update_stage_indicators, None, [current_stage, stage_progress])
    # Add examples
    gr.Examples(
        examples=example_questions,
        inputs=msg
    )
    
    logger.info("Teaching interface created successfully")
    return chatbot, current_stage, stage_progress 