import os
import json
from vertexai.generative_models import GenerativeModel, GenerationConfig, Part
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
                            "judge_answer": {"type": "string"}
                        },
                        "required": [
                            "stage_id",
                            "stage_description",
                            "judge_media_allowed",
                            "target",
                            "teaching_knowledge",
                            "judge_question",
                            "judge_answer"
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
        
        For any content that should include multimedia elements, use appropriate tags:
        - For images: <image>detailed description of what the image should show</image>
        - For videos: <video>detailed description of what the video should contain</video>
        
        Analyze the document thoroughly and organize the content into a logical learning progression.
        Return a structured JSON object following the required format.
        """
        
        # Combine document and prompt as parts for the model
        contents = [document_part, prompt_text]
        
        # First try using structured output with schema
        try:
            self.logger.info("Attempting to generate structured syllabus with schema")
            response = self.model.generate_content(
                contents,
                generation_config=GenerationConfig(
                    max_output_tokens=4096,
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
            self.logger.error(f"Error generating structured syllabus: {str(schema_error)}", exc_info=True)
            
            # Fallback to text generation without schema
            try:
                self.logger.info("Falling back to text generation without schema")
                response = self.model.generate_content(
                    contents,
                    generation_config=GenerationConfig(
                        max_output_tokens=4096,
                        temperature=0.2
                    )
                )
                
                response_text = response.text
                
                # Try to parse response as JSON directly
                try:
                    result = json.loads(response_text)
                    self.logger.info("Successfully parsed response as JSON")
                    return result
                except json.JSONDecodeError:
                    self.logger.warning("Failed to parse response as JSON, attempting to extract JSON from text")
                    # If direct parsing fails, try to extract JSON from text
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1
                    
                    if json_start != -1 and json_end != -1:
                        json_content = response_text[json_start:json_end]
                        try:
                            result = json.loads(json_content)
                            self.logger.info("Successfully extracted and parsed JSON content")
                            return result
                        except json.JSONDecodeError:
                            self.logger.error("Could not parse extracted content as JSON")
                            return {"error": "Could not parse extracted content as JSON"}
                    else:
                        self.logger.error("Could not find JSON content in response")
                        return {"error": "Could not find JSON content in response"}
            except Exception as fallback_error:
                self.logger.error(f"Failed to generate syllabus: {str(fallback_error)}", exc_info=True)
                return {"error": f"Failed to generate syllabus: {str(fallback_error)}"}
    
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
        
        # Convert current syllabus to string for the prompt
        current_syllabus_str = json.dumps(current_syllabus, indent=2)
        
        # Prompt for updating the syllabus
        prompt = f"""
        You are an expert educational content creator. I have a teaching syllabus in JSON format:
        
        {current_syllabus_str}
        
        I would like to update this syllabus according to these instructions:
        
        {user_message}
        
        Please modify the syllabus accordingly and return the updated syllabus.
        
        Make sure to maintain the exact same JSON structure with these fields:
        - syllabus_name
        - target_audience
        - syllabus (an array of stages)
          - Each stage must include: stage_id, stage_description, judge_media_allowed, target, teaching_knowledge, judge_question, judge_answer
        
        For any content that should include multimedia elements, use appropriate tags:
        - For images: <image>detailed description of what the image should show</image>
        - For videos: <video>detailed description of what the video should contain</video>
        """
        
        # First try using structured output with schema
        try:
            self.logger.info("Attempting to update syllabus with schema")
            response = self.model.generate_content(
                prompt,
                generation_config=GenerationConfig(
                    max_output_tokens=4096,
                    temperature=0.2,
                    response_mime_type="application/json",
                    response_schema=self.syllabus_schema
                )
            )
            
            # Parse the structured JSON response
            result = json.loads(response.text)
            self.logger.info("Successfully updated syllabus with schema")
            return result
            
        except Exception as schema_error:
            self.logger.error(f"Error updating structured syllabus: {str(schema_error)}", exc_info=True)
            
            # Fallback to text generation without schema
            try:
                self.logger.info("Falling back to text generation without schema")
                response = self.model.generate_content(
                    prompt,
                    generation_config=GenerationConfig(
                        max_output_tokens=4096,
                        temperature=0.2
                    )
                )
                
                response_text = response.text
                
                # Try to parse response as JSON directly
                try:
                    result = json.loads(response_text)
                    self.logger.info("Successfully parsed response as JSON")
                    return result
                except json.JSONDecodeError:
                    self.logger.warning("Failed to parse response as JSON, attempting to extract JSON from text")
                    # If direct parsing fails, try to extract JSON from text
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1
                    
                    if json_start != -1 and json_end != -1:
                        json_content = response_text[json_start:json_end]
                        try:
                            result = json.loads(json_content)
                            self.logger.info("Successfully extracted and parsed JSON content")
                            return result
                        except json.JSONDecodeError:
                            self.logger.error("Could not parse extracted content as JSON")
                            return {"error": "Could not parse extracted content as JSON"}
                    else:
                        self.logger.error("Could not find JSON content in response")
                        return {"error": "Could not find JSON content in response"}
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
            '.txt': 'text/plain',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        
        mime_type = mime_types.get(file_extension, 'application/pdf')
        self.logger.debug(f"Determined MIME type for {url}: {mime_type}")
        
        # Return appropriate MIME type or default to PDF
        return mime_type 