import json
import os
from vertexai.generative_models import GenerativeModel, ChatSession
from app.utils.gr_logger import setup_logger
import re

class TutorBotService:
    """Service for handling the tutoring chatbot interactions"""
    
    def __init__(self):
        """Initialize the tutor bot service"""
        self.logger = setup_logger(__name__)
        self.logger.info("Initializing TutorBotService")
        
        # Initialize Gemini model
        model_name = os.environ.get("GEMINI_CHAT_MODEL", "gemini-2.0-flash")
        self.logger.debug(f"Using Gemini model: {model_name}")
        self.model = GenerativeModel(model_name)
        self.chat_session = None
        
        # Syllabus information
        self.syllabus_info = None
        self.current_stage_index = 0
        self.is_teaching_started = False
        
        self.logger.debug("TutorBotService initialized successfully")
    
    def set_syllabus(self, syllabus_info):
        """Set the syllabus information for the tutor bot
        
        Args:
            syllabus_info (dict): The syllabus information
        """
        self.logger.info("Setting syllabus for tutor bot")
        self.syllabus_info = syllabus_info
        self.current_stage_index = 0
        self.is_teaching_started = False
        
        # Initialize a new chat session
        self.chat_session = self.model.start_chat()
        
        # Prime the chat session with system instructions
        system_prompt = self._create_system_prompt()
        self._send_message_to_model(system_prompt, is_system=True)
        self.logger.info("Syllabus set and chat session initialized")
    
    def process_message(self, input_type, input_content, chat_history):
        """Process a message from the user or admin and generate a response
        
        Args:
            input_type (str): The type of input - "user" or "admin"
            input_content (str): The content of the input
            chat_history (list): The current chat history
            
        Returns:
            tuple: Updated chat history and any UI state updates
        """
        self.logger.info(f"Processing message - Type: {input_type}, Content: {input_content}")
        
        if not self.syllabus_info:
            self.logger.warning("No syllabus set for tutor bot")
            chat_history.append((input_content if input_type == "user" else "", 
                                "Please set a syllabus before starting the teaching session. Go back to the 'Generate Syllabus' tab and generate one first."))
            return chat_history, None
        
        # Get current stage information
        current_stage_info = self._get_current_stage_info()
        if not current_stage_info:
            self.logger.error("Failed to get current stage information")
            chat_history.append((input_content if input_type == "user" else "", 
                                "There was an error retrieving the current stage information. Please try again or generate a new syllabus."))
            return chat_history, None
        
        # Create prompt for the model
        prompt = self._create_prompt(input_type, input_content, current_stage_info)
        
        # Get response from model
        response_text = self._send_message_to_model(prompt)
        
        try:
            # Parse the response as JSON
            response_json = json.loads(response_text)
            
            # Validate response structure
            if not self._validate_response(response_json):
                self.logger.error("Invalid response structure")
                error_msg = "I encountered an error in processing your request. Let me try again."
                chat_history.append((input_content if input_type == "user" else "", error_msg))
                return chat_history, None
            
            # Extract the response content
            response_content = response_json.get("response_content", "")
            response_type = response_json.get("response_type", "")
            is_pass = response_json.get("is_pass", False)
            
            # Add to chat history
            if input_type == "user":
                chat_history.append((input_content, response_content))
            elif input_type == "admin" and input_content.lower() not in ["start teaching", "end teaching"]:
                # Don't show admin commands in chat history except for special commands
                pass
            else:
                chat_history.append(("", response_content))
                
            # Handle stage progression if needed
            stage_updated = False
            if (input_type == "admin" and "next stage" in input_content.lower()) or \
               (response_type == "judge" and is_pass and self.current_stage_index < len(self.syllabus_info["syllabus"]) - 1):
                # Move to next stage
                self.current_stage_index += 1
                stage_updated = True
                self.logger.info(f"Moving to next stage: {self.current_stage_index}")
                
                # If advancing stage, send a teaching message for the new stage
                if stage_updated and self.current_stage_index < len(self.syllabus_info["syllabus"]):
                    teach_prompt = self._create_prompt("admin", "start stage", self._get_current_stage_info())
                    teach_response_text = self._send_message_to_model(teach_prompt)
                    
                    try:
                        teach_response_json = json.loads(teach_response_text)
                        teach_content = teach_response_json.get("response_content", "")
                        chat_history.append(("", teach_content))
                    except json.JSONDecodeError:
                        self.logger.error("Failed to parse teaching response as JSON")
                
            elif input_type == "admin" and "previous stage" in input_content.lower() and self.current_stage_index > 0:
                # Move to previous stage
                self.current_stage_index -= 1
                stage_updated = True
                self.logger.info(f"Moving to previous stage: {self.current_stage_index}")
                
                # Send teaching message for the previous stage
                teach_prompt = self._create_prompt("admin", "start stage", self._get_current_stage_info())
                teach_response_text = self._send_message_to_model(teach_prompt)
                
                try:
                    teach_response_json = json.loads(teach_response_text)
                    teach_content = teach_response_json.get("response_content", "")
                    chat_history.append(("", teach_content))
                except json.JSONDecodeError:
                    self.logger.error("Failed to parse teaching response as JSON")
            
            return chat_history, stage_updated
            
        except json.JSONDecodeError:
            self.logger.error("Failed to parse response as JSON", exc_info=True)
            error_msg = "I encountered an error in my response format. Let me try again."
            chat_history.append((input_content if input_type == "user" else "", error_msg))
            return chat_history, None
    
    def start_teaching(self, chat_history):
        """Start the teaching session
        
        Args:
            chat_history (list): The current chat history
            
        Returns:
            list: Updated chat history
        """
        self.logger.info("Starting teaching session")
        
        if not self.syllabus_info:
            self.logger.warning("No syllabus set for tutor bot")
            chat_history.append(("", "Please generate a syllabus first before starting the teaching session."))
            return chat_history
        
        # Reset to first stage
        self.current_stage_index = 0
        self.is_teaching_started = True
        
        # Create a greeting prompt
        current_stage_info = self._get_current_stage_info()
        greeting_prompt = self._create_prompt("admin", "start teaching", current_stage_info)
        
        # Get greeting response
        greeting_response_text = self._send_message_to_model(greeting_prompt)
        
        try:
            greeting_response_json = json.loads(greeting_response_text)
            greeting_content = greeting_response_json.get("response_content", "")
            chat_history.append(("", greeting_content))
            
            # Then automatically trigger the first stage teaching content
            teach_prompt = self._create_prompt("admin", "start stage", current_stage_info)
            teach_response_text = self._send_message_to_model(teach_prompt)
            
            try:
                teach_response_json = json.loads(teach_response_text)
                teach_content = teach_response_json.get("response_content", "")
                chat_history.append(("", teach_content))
            except json.JSONDecodeError:
                self.logger.error("Failed to parse teaching response as JSON")
            
        except json.JSONDecodeError:
            self.logger.error("Failed to parse greeting response as JSON")
            chat_history.append(("", "Welcome to the teaching session! Let's get started."))
        
        return chat_history
    
    def end_teaching(self, chat_history):
        """End the teaching session
        
        Args:
            chat_history (list): The current chat history
            
        Returns:
            list: Updated chat history
        """
        self.logger.info("Ending teaching session")
        
        if not self.is_teaching_started:
            self.logger.warning("Teaching session not started")
            return chat_history
        
        # Create an ending prompt
        ending_prompt = self._create_prompt("admin", "end teaching", None)
        
        # Get ending response
        ending_response_text = self._send_message_to_model(ending_prompt)
        
        try:
            ending_response_json = json.loads(ending_response_text)
            ending_content = ending_response_json.get("response_content", "")
            chat_history.append(("", ending_content))
        except json.JSONDecodeError:
            self.logger.error("Failed to parse ending response as JSON")
            chat_history.append(("", "Thank you for completing the teaching session! I hope you learned a lot."))
        
        self.is_teaching_started = False
        return chat_history
    
    def _get_current_stage_info(self):
        """Get the current stage information
        
        Returns:
            dict: The current stage information or None if not available
        """
        try:
            if not self.syllabus_info:
                self.logger.warning("No syllabus info available")
                return None
                
            if "syllabus" not in self.syllabus_info:
                self.logger.error("Syllabus info does not contain 'syllabus' key")
                return None
                
            if not isinstance(self.syllabus_info["syllabus"], list) or not self.syllabus_info["syllabus"]:
                self.logger.error("Syllabus does not contain any stages")
                return None
            
            if self.current_stage_index >= len(self.syllabus_info["syllabus"]):
                self.logger.warning(f"Current stage index {self.current_stage_index} is out of bounds, resetting to last stage")
                self.current_stage_index = len(self.syllabus_info["syllabus"]) - 1
            
            return self.syllabus_info["syllabus"][self.current_stage_index]
            
        except Exception as e:
            self.logger.error(f"Error getting current stage info: {str(e)}", exc_info=True)
            return None
    
    def _create_system_prompt(self):
        """Create a system prompt to initialize the chat session
        
        Returns:
            str: The system prompt
        """
        syllabus_str = json.dumps(self.syllabus_info, indent=2)
        
        system_prompt = f"""
        You are an educational AI tutor designed to teach based on a structured syllabus. 
        Your responses should always be formatted as JSON following this specific structure:
        
        {{
            "stage_id": "current stage id",
            "response_type": "teach/explain/judge/greet",
            "is_pass": true/false,
            "response_content": "Your actual response content here"
        }}
        
        Here's the syllabus you will be teaching:
        
        {syllabus_str}
        
        Important rules:
        1. response_type has four possible values:
           - "teach": Used only when starting a new stage, explaining the core teaching content
           - "explain": Used when answering questions or providing additional explanations
           - "judge": Used when evaluating student answers to questions
           - "greet": Used only at the beginning and end of the teaching session
        
        2. is_pass should only be true when response_type is "judge" and the student's answer meets the criteria in judge_rule
        
        3. For multimedia content in response_content, use these tags:
           - <image>detailed description of what the image should show</image>
           - <video>detailed description of what the video should contain</video>
        
        4. You will receive input in this format:
           Input_type: admin/user
           Input: (content)
           Current_stage_info: (JSON of current stage)
        
        5. Admin commands have special meanings:
           - "start teaching": Begin the teaching session with a greeting
           - "end teaching": End the teaching session with a conclusion
           - "start stage": Begin teaching the current stage
           - "next stage": Move to the next stage
           - "previous stage": Move to the previous stage
        
        6. User inputs are either questions or answers to judge_question
        
        7. Always provide rich, engaging educational content appropriate for the target_audience
        
        8. Stay strictly within the scope of the syllabus and current stage
        
        9. response_content is the ONLY part that will be shown to the user
        
        Remember: Your response must ALWAYS be a valid JSON object following the specified format.
        """
        
        return system_prompt
    
    def _create_prompt(self, input_type, input_content, current_stage_info):
        """Create a prompt for the model
        
        Args:
            input_type (str): The type of input - "user" or "admin"
            input_content (str): The content of the input
            current_stage_info (dict): The current stage information
            
        Returns:
            str: The prompt for the model
        """
        # Convert current stage info to string if it exists
        stage_info_str = json.dumps(current_stage_info) if current_stage_info else "null"
        
        prompt = f"""
        Input_type: {input_type}
        Input: {input_content}
        Current_stage_info: {stage_info_str}
        
        Respond with a properly formatted JSON object as instructed.
        """
        
        return prompt
    
    def _send_message_to_model(self, message, is_system=False):
        """Send a message to the model and get the response
        
        Args:
            message (str): The message to send
            is_system (bool): Whether this is a system message
            
        Returns:
            str: The response from the model
        """
        try:
            self.logger.debug(f"Sending message to model: {message[:100]}...")
            
            if not self.chat_session:
                self.logger.info("Creating new chat session")
                self.chat_session = self.model.start_chat()
            
            response = self.chat_session.send_message(message)
            self.logger.debug(f"Received response from model: {response.text[:100]}...")
            
            return response.text
        except Exception as e:
            self.logger.error(f"Error sending message to model: {str(e)}", exc_info=True)
            # Return a basic error response in JSON format
            return '{"stage_id": "", "response_type": "explain", "is_pass": false, "response_content": "I encountered an error processing your request. Please try again."}'
    
    def _validate_response(self, response):
        """Validate the response structure
        
        Args:
            response (dict): The response to validate
            
        Returns:
            bool: Whether the response is valid
        """
        required_fields = ["stage_id", "response_type", "response_content"]
        
        # Check if all required fields are present
        for field in required_fields:
            if field not in response:
                self.logger.error(f"Missing required field in response: {field}")
                return False
        
        # Check if response_type is valid
        valid_response_types = ["teach", "explain", "judge", "greet"]
        if response["response_type"] not in valid_response_types:
            self.logger.error(f"Invalid response_type: {response['response_type']}")
            return False
        
        # If response_type is judge, is_pass must be present
        if response["response_type"] == "judge" and "is_pass" not in response:
            self.logger.error("Missing is_pass field for judge response_type")
            return False
        
        return True 