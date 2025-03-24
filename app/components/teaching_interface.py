import gradio as gr
import re
from app.utils.gr_logger import setup_logger

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
        height=500,
        elem_id="teaching-chatbot",
        show_label=False,
        avatar_images=("./app/assets/user.png", "./app/assets/bot.png")
    )
    
    # Create message input
    msg = gr.Textbox(
        placeholder="Ask a question or provide an answer...",
        container=False,
        scale=7
    )
    
    # Create stage indicators
    current_stage = gr.Markdown("### Current Stage: Not started")
    stage_progress = gr.Markdown("### Progress: 0/0 stages")
    
    # Create admin control buttons
    with gr.Row():
        start_btn = gr.Button("Start Teaching", variant="primary")
        next_stage_btn = gr.Button("Next Stage")
        prev_stage_btn = gr.Button("Previous Stage")
        end_btn = gr.Button("End Teaching", variant="stop")
    
    # Create multimedia input buttons
    with gr.Row():
        gr.Markdown("### Add Multimedia Input:")
        image_btn = gr.Button("📷 Add Image Description")
        video_btn = gr.Button("🎬 Add Video Description")
    
    # Add example questions
    example_questions = [
        "Can you explain this concept in more detail?",
        "I didn't understand the last part.",
        "Why is this important?",
        "How does this relate to the previous stage?",
        "What are some real-world applications of this?"
    ]
    
    # Define chat submit function for user messages
    def user_message_submit(message, chat_history):
        logger.info(f"User message submitted: {message}")
        
        if not message:
            return "", chat_history
        
        if not tutor_bot_service.syllabus_info:
            logger.warning("No syllabus available for teaching")
            chat_history.append((message, "Sorry, there's no syllabus available for teaching. Please go back to the 'Generate Syllabus' tab and generate a syllabus first."))
            return "", chat_history
            
        updated_chat_history, stage_updated = tutor_bot_service.process_message("user", message, chat_history)
        
        # Update stage indicator if needed
        if stage_updated:
            update_stage_indicators()
        
        return "", updated_chat_history
    
    # Define functions for admin commands
    def start_teaching(chat_history):
        logger.info("Starting teaching session")
        
        if not tutor_bot_service.syllabus_info:
            logger.warning("No syllabus available for teaching")
            chat_history.append(("", "Sorry, there's no syllabus available for teaching. Please go back to the 'Generate Syllabus' tab and generate a syllabus first."))
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
            chat_history.append(("", "Sorry, there's no syllabus available for teaching. Please go back to the 'Generate Syllabus' tab and generate a syllabus first."))
            return chat_history
            
        updated_chat_history, _ = tutor_bot_service.process_message("admin", "next stage", chat_history)
        update_stage_indicators()
        return updated_chat_history
    
    def prev_stage(chat_history):
        logger.info("Moving to previous stage")
        
        if not tutor_bot_service.syllabus_info:
            logger.warning("No syllabus available for teaching")
            chat_history.append(("", "Sorry, there's no syllabus available for teaching. Please go back to the 'Generate Syllabus' tab and generate a syllabus first."))
            return chat_history
            
        updated_chat_history, _ = tutor_bot_service.process_message("admin", "previous stage", chat_history)
        update_stage_indicators()
        return updated_chat_history
    
    def update_stage_indicators():
        """Update the stage indicators"""
        if tutor_bot_service.syllabus_info and tutor_bot_service.is_teaching_started:
            try:
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
                return "### Current Stage: Error loading stage info", "### Progress: Error loading progress"
        else:
            return "### Current Stage: Not started", "### Progress: 0/0 stages"
    
    # Helper functions for multimedia input
    def add_image_tag(message):
        logger.debug("Adding image tag to message")
        return message + " <image></image>"
    
    def add_video_tag(message):
        logger.debug("Adding video tag to message")
        return message + " <video></video>"
    
    # Connect components
    msg.submit(user_message_submit, [msg, chatbot], [msg, chatbot])
    
    # Connect admin buttons
    start_btn.click(start_teaching, [chatbot], [chatbot])
    next_stage_btn.click(next_stage, [chatbot], [chatbot])
    prev_stage_btn.click(prev_stage, [chatbot], [chatbot])
    end_btn.click(end_teaching, [chatbot], [chatbot])
    
    # Connect multimedia buttons to message input
    image_btn.click(add_image_tag, [msg], [msg])
    video_btn.click(add_video_tag, [msg], [msg])
    
    # Connect stage indicators update
    for btn in [start_btn, next_stage_btn, prev_stage_btn]:
        btn.click(update_stage_indicators, None, [current_stage, stage_progress])
    
    # Add examples
    gr.Examples(
        examples=example_questions,
        inputs=msg,
    )
    
    logger.info("Teaching interface created successfully")
    return chatbot, current_stage, stage_progress 