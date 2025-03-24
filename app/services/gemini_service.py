import os
import json
from vertexai.generative_models import GenerativeModel, GenerationConfig, Part, ChatSession
from app.utils.gr_logger import setup_logger

class GeminiService:
    """Service for interacting with Gemini API"""
    
    def __init__(self):
        """Initialize Gemini service with API configuration"""
        self.logger = setup_logger(__name__)
        self.logger.info("Initializing GeminiService")
        
        model_name = os.environ.get("GEMINI_MODEL")
        self.logger.debug(f"Using Gemini model: {model_name}")
        self.model = GenerativeModel(model_name)
        self.chat_session = None
        
        # Define syllabus JSON schema for structured output
        self.syllabus_schema = {
            "type": "object",
            "properties": {
                "syllabus_name": {"type": "string"},
                "target_audience": {"type": "string"},
                "syllabus": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "stage_id": {"type": "string"},
                            "stage_description": {"type": "string"},
                            "judge_media_allowed": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "target": {"type": "string"},
                            "teaching_knowledge": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "judge_question": {"type": "string"},
                            "judge_rule": {"type": "string"}
                        },
                        "required": [
                            "stage_id",
                            "stage_description",
                            "judge_media_allowed",
                            "target",
                            "teaching_knowledge",
                            "judge_question",
                            "judge_rule"
                        ]
                    }
                }
            },
            "required": ["syllabus_name", "target_audience", "syllabus"]
        }
        self.logger.debug("Syllabus JSON schema defined")
        
    def generate_syllabus_from_document(self, document_url):
        """Generate a teaching syllabus from a document URL
        
        Args:
            document_url (str): URL of the document to analyze
            
        Returns:
            dict: Generated syllabus in JSON format
        """
        self.logger.info(f"Generating syllabus from document: {document_url}")
        
        # Create document part using Part.from_uri for proper document handling
        document_mime_type = self._get_mime_type_from_url(document_url)
        self.logger.debug(f"Document MIME type determined as: {document_mime_type}")
        
        document_part = Part.from_uri(
            uri=document_url,
            mime_type=document_mime_type
        )
        
        # Initialize a new chat session
        self.chat_session = self.model.start_chat()
        
        # Prompt for generating a structured syllabus
        prompt_text = """
        You are an expert educational content creator. Your task is to analyze the provided document.
        
        Create a comprehensive teaching syllabus based on the content of this document.
        
        The syllabus should be structured as follows:
        1. A descriptive syllabus name that reflects the main topic
        2. An appropriate target audience
        3. A series of learning stages, where each stage includes:
           - A unique stage ID
           - A clear stage description
           - Judge media types allowed (text, image, video) that users can use for testing
           - Learning targets for this stage
           - Key teaching knowledge points
           - Evaluation questions to test understanding
           - Expected answers to evaluation questions
        You will provide the syllabus in JSON format as follows:
     
        syllabus_name: string, The name of the syllabus
        target_audience: string, The target audience of the syllabus
        syllabus: List of syllabus sub object
        syllabus sub object :{
            "stage_id": string,The name of each stage
            "stage_description": string, simpple description of each stage
            "judge_media_allowed": [list of allowed media types],such as ["image","text","video"]
            "target": string, the target of this stage
            "teaching_knowledge":List of string,the knowledge points of this stage,MUST strictly follow the syllabus that provided by the user,you must provide relevant knowledge points for this stage
            "judge_question":string,the question to pass this stage
            "judge_rule":string,the rule to judge the answer if the answer is correct,the user will pass this stage
        }

        VERY IMPORTANT!: YOU MUST FOLLOW THE FOLLOWING RULES ABOUT THE MULTIMEDIA ELEMENTS:
        For any content that should include multimedia elements, use appropriate tags:
        - For images: [image]detailed description of what the image should show[/image]
        - For videos: [video]detailed description of what the video should contain[/video]
        - For interactive elements: <interactive>detailed description of what the interactive element should contain</interactive>
        
        VERY IMPORTANT!:The target,teaching_knowledge,judge_question,judge_rule MAY provide multimedia elements according to the raw data
        
        You MUST provide multimedia tags when you think it is necessary
        for example:
        target:help the student to understand the how gravity works
        teaching_knowledge:[video]a picture of a person jumping and falling[/video] [image]a picture of apple falling towards Newton's head[/image]
        judge_question: which image is effective to explain the gravity? [image] water flows from high to low[/image] [image]a car is driving on the road quickly[/image]
        judge_rule: the correct answer is the image that shows the water flows from high to low
    
        
        Now,Analyze the document thoroughly and organize the content into a logical learning progression.
        Return a structured JSON object following the required format.
        """
        
        try:
            self.logger.info("Attempting to generate structured syllabus with schema")
            
            # Send document part and prompt together in a single message
            contents = [document_part, prompt_text]
            response = self.chat_session.send_message(
                contents,
                generation_config=GenerationConfig(
                    max_output_tokens=8192,
                    temperature=0.2,
                    response_mime_type="application/json",
                    response_schema=self.syllabus_schema
                )
            )
            
            # Parse the structured JSON response
            result = json.loads(response.text)
            self.logger.info("Successfully generated structured syllabus")
            return result
            
        except Exception as schema_error:
            self.logger.error(f"Failed to generate syllabus: {str(schema_error)}", exc_info=True)
            return {"error": f"Failed to generate syllabus: {str(schema_error)}"}
    
    def update_syllabus(self, current_syllabus, user_message):
        """Update a syllabus based on user instructions
        
        Args:
            current_syllabus (dict): Current syllabus in JSON format
            user_message (str): User message with instructions for changes
            
        Returns:
            dict: Updated syllabus in JSON format
        """
        self.logger.info("Updating syllabus based on user instructions")
        self.logger.debug(f"User message: {user_message}")
        
        # Create prompt with just the modification instructions
        update_prompt = f"""
        Please update the syllabus according to these instructions,follow the rules above:
        {user_message}
        """
        
        # Try using structured output with schema
        try:
            self.logger.info("Attempting to update syllabus with schema")
            response = self.chat_session.send_message(
                update_prompt,
                generation_config=GenerationConfig(
                    max_output_tokens=8192,
                    temperature=0.2,
                    response_mime_type="application/json",
                    response_schema=self.syllabus_schema
                )
            )
            # Parse the structured JSON response
            result = json.loads(response.text)
            self.logger.info("Successfully updated syllabus with schema")
            return result
        except Exception as fallback_error:
                self.logger.error(f"Failed to update syllabus: {str(fallback_error)}", exc_info=True)
                return {"error": f"Failed to update syllabus: {str(fallback_error)}"}
                
    def _get_mime_type_from_url(self, url):
        """Determine the MIME type based on the file extension in the URL
        
        Args:
            url (str): URL of the document
            
        Returns:
            str: MIME type for the document
        """
        # Extract file extension from URL
        file_extension = os.path.splitext(url)[1].lower()
        
        # Map file extensions to MIME types
        mime_types = {
            '.pdf': 'application/pdf',
        }
        
        mime_type = mime_types.get(file_extension, 'application/pdf')
        self.logger.debug(f"Determined MIME type for {url}: {mime_type}")
        
        # Return appropriate MIME type or default to PDF
        return mime_type 