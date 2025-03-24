import os
import tempfile
import json
from app.services.s3_service import S3Service
from app.services.gemini_service import GeminiService
from app.utils.gr_logger import setup_logger
import re

class SyllabusGenerator:
    """Service for generating teaching syllabuses from documents"""
    
    def __init__(self):
        """Initialize the syllabus generator with required services"""
        self.logger = setup_logger(__name__)
        self.logger.info("Initializing SyllabusGenerator")
        
        self.s3_service = S3Service()
        self.gemini_service = GeminiService()
        self.document_url = None
        self.document_uploaded = False
        self.current_syllabus = None
        
        self.logger.debug("SyllabusGenerator initialized successfully")
    
    def handle_file_upload(self, file):
        """Handle document upload, save to S3, and return status
        
        Args:
            file: Gradio file object
            
        Returns:
            list: Updated chat history
        """
        if file is None:
            self.logger.warning("No file uploaded")
            return [[None, "No file uploaded. Please upload a PDF or TXT file."]]
        
        try:
            self.logger.info(f"Processing file upload: {file.name}")
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[1]) as temp_file:
                temp_file_path = temp_file.name
                self.logger.debug(f"Created temporary file at {temp_file_path}")
                
                # Write uploaded file content to temporary file
                with open(file.name, 'rb') as f:
                    temp_file.write(f.read())
            
            # Upload file to S3
            self.logger.info("Uploading file to S3")
            self.document_url = self.s3_service.upload_file(temp_file_path)
            
            # Clean up temporary file
            self.logger.debug(f"Removing temporary file {temp_file_path}")
            os.unlink(temp_file_path)
            
            if self.document_url:
                self.document_uploaded = True
                self.logger.info(f"Document uploaded successfully: {self.document_url}")
                return [[None, f"Document uploaded successfully. You can now generate a syllabus by sending a message like 'Generate a syllabus from this document'."]]
            else:
                self.logger.error("Failed to upload document to S3")
                return [[None, "Failed to upload document. Please check your AWS credentials and try again."]]
                
        except Exception as e:
            self.logger.error(f"Error processing file: {str(e)}", exc_info=True)
            return [[None, f"Error processing file: {str(e)}"]]
    
    def process_message(self, message):
        """Process user message and generate response
        
        Args:
            message (str): User message
            
        Returns:
            str: Response to user
        """
        self.logger.info(f"Processing user message: {message}")
        
        # Check if document is uploaded
        if not self.document_uploaded:
            self.logger.warning("No document uploaded")
            return "Please upload a document first to generate a syllabus."
        
        # Generate syllabus if requested
        if re.search(r'generate.*syllabus|create.*syllabus', message.lower()):
            self.logger.info("Generating syllabus from document")
            try:
                self.current_syllabus = self.gemini_service.generate_syllabus_from_document(self.document_url)
                
                # Check if there was an error in generation
                if "error" in self.current_syllabus:
                    self.logger.error(f"Error generating syllabus: {self.current_syllabus['error']}")
                    return f"Error: {self.current_syllabus['error']}"
                
                # Format syllabus for display
                formatted_syllabus = json.dumps(self.current_syllabus, indent=2, ensure_ascii=False)
                self.logger.info("Syllabus generated successfully")
                return f"Generated teaching syllabus:\n```json\n{formatted_syllabus}\n```\n\nYou can now modify this syllabus by giving specific instructions."
            except Exception as e:
                self.logger.error(f"Error generating syllabus: {str(e)}", exc_info=True)
                return f"Error generating syllabus: {str(e)}"
        
        # Update syllabus if already generated
        elif self.current_syllabus:
            self.logger.info("Updating existing syllabus")
            try:
                updated_syllabus = self.gemini_service.update_syllabus(self.current_syllabus, message)
                
                # Check if there was an error in update
                if "error" in updated_syllabus:
                    self.logger.error(f"Error updating syllabus: {updated_syllabus['error']}")
                    return f"Error: {updated_syllabus['error']}"
                
                self.current_syllabus = updated_syllabus
                
                # Format syllabus for display
                formatted_syllabus = json.dumps(self.current_syllabus, indent=2, ensure_ascii=False)
                
                # Check syllabus structure

                self.logger.info("Syllabus updated successfully")
                return f"Updated teaching syllabus:\n```json\n{formatted_syllabus}\n```"
            except Exception as e:
                self.logger.error(f"Error updating syllabus: {str(e)}", exc_info=True)
                return f"Error updating syllabus: {str(e)}"
        else:
            self.logger.warning("No syllabus generated yet")
            return "Please generate a syllabus first by typing 'Generate a syllabus from this document'."
    