MAIN_CSS="""
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
        /* Status message styling */
        #syllabus-status {
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .success-status {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .error-status {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        /* Make examples closer to chatbox */
        .gradio-container .examples-parent {
            margin-top: -8px !important;
        }
        /* Target examples more generally since we can't use classes */
        .gradio-container .examples {
            margin-top: -8px !important;
        }
        /* Styling for collapsible sections */
        details {
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            padding: 0.5em;
            margin-bottom: 1em;
            background-color: #f9f9f9;
        }
        summary {
            font-weight: bold;
            cursor: pointer;
            padding: 0.5em;
            margin: -0.5em;
            background-color: #f0f0f0;
        }
        details[open] summary {
            border-bottom: 1px solid #e0e0e0;
            margin-bottom: 0.5em;
        }
        /* Syllabus Accordion styling */
        .gradio-accordion {
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            margin-bottom: 1em;
            background-color: #f9f9f9;
        }
        .gradio-accordion[open] .label-wrap {
            border-bottom: 1px solid #e0e0e0;
            margin-bottom: 0.5em;
        }
        .gradio-accordion .grammd {
            padding: 0.5em;
        }
        /* Syllabus details styling */
        .syllabus-details {
            padding: 10px;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
        }
        .syllabus-details h2 {
            color: #2c3e50;
            margin-top: 0;
            border-bottom: 1px solid #eaecef;
            padding-bottom: 10px;
        }
        .syllabus-details h3 {
            color: #3c4043;
            margin: 15px 0 10px 0;
        }
        .syllabus-metadata {
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            border-left: 3px solid #75b798;
        }
        .syllabus-stages {
            margin-left: 20px;
        }
        .syllabus-stages li {
            margin-bottom: 8px;
            line-height: 1.4;
        }
    """

SYLLABUS_DESCRIPTION="""
                        <details>
                            <summary>Instructions</summary>
                            
                            1. Upload your document using the file uploader below
                            2. Ask the AI to generate a syllabus
                            3. Provide instructions to modify the syllabus as needed
                            
                            The document will be processed using Gemini's multimodal capabilities,
                            allowing for direct analysis of PDFs and other document formats.
                            
                            The syllabus will be generated in a structured JSON format that follows a specific schema for teaching content.
                        </details>
                        """
                        
SYLLABUS_FORMAT="""
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
                        """
                        
                        
TEACHING_TUTOR_DESCRIPTION="""
                            <details>
                                <summary>Teaching Session</summary>
                                
                                This is an interactive teaching session based on the syllabus you generated.
                                
                                The AI tutor will guide you through each stage of the syllabus, providing:
                                - Explanations of concepts
                                - Answers to your questions
                                - Evaluation of your answers to questions
                                
                                Use the controls below to:
                                - Start/end the teaching session
                                - Navigate between stages
                                - Add multimedia descriptions in your responses
                            </details>
                            """

# Main application title and description
APP_TITLE = "Teaching Syllabus Generator and Tutor"
APP_DESCRIPTION = "Generate a teaching syllabus from a document and use it for interactive teaching."

# Status messages
NO_SYLLABUS_STATUS = "**Status**: No syllabus generated yet. Please generate a syllabus first."
SYLLABUS_LOADED_STATUS = "**Status**: Syllabus loaded successfully. You can now start the teaching session."
PLACEHOLDER_MESSAGE = "### Please generate a syllabus in the 'Generate Syllabus' tab first before starting the teaching session."

# Button text
START_TEACHING_BTN_TEXT = "▶️ Start Teaching Session"

# Teaching interface strings
TEACHING_STAGE_NOT_STARTED = "### Current Stage: Not started"
TEACHING_PROGRESS_NOT_STARTED = "### Progress: 0/0 stages"
TEACHING_STAGE_ERROR = "### Current Stage: Error loading stage info"
TEACHING_PROGRESS_ERROR = "### Progress: Error loading progress"

# Chat interface strings
CHAT_PLACEHOLDER = "Chat with the AI about your teaching syllabus..."
TEACHING_CHAT_PLACEHOLDER = "Ask a question or provide an answer..."

# Buttons
START_TEACHING_TEXT = "Start Teaching"
NEXT_STAGE_TEXT = "Next Stage"
PREV_STAGE_TEXT = "Previous Stage"
END_TEACHING_TEXT = "End Teaching"
CLEAR_BTN_TEXT = "Clear"
SEND_BTN_TEXT = "Send"

# Multimedia input
MULTIMEDIA_HEADING = "### Add Multimedia Input:"
IMAGE_BTN_TEXT = "📷 Add Image Description"
VIDEO_BTN_TEXT = "🎬 Add Video Description"

# Example questions for teaching interface
TEACHING_EXAMPLE_QUESTIONS = [
    "Can you explain this concept in more detail?",
    "I didn't understand the last part.",
    "Why is this important?",
    "How does this relate to the previous stage?",
    "What are some real-world applications of this?"
]

# Example prompts for chat interface
CHAT_EXAMPLE_PROMPTS = [
    "Generate a teaching syllabus from my uploaded document",
    "Change the target audience to 'middle school students (12-14 years)'",
    "Add a new stage about advanced topics at the end of the syllabus",
    "Update the teaching knowledge in stage 1 to include 'introduction to basic concepts'",
    "Add more media types like 'video' to stage 2",
    "Make the judge question in stage 3 more challenging",
    "Add an image illustrating the concept in the first stage"
]

# Chat interface description
CHAT_INTERFACE_DESCRIPTION = """
    <details>
        <summary>Teaching Syllabus Generator Instructions</summary>
        
        This chatbot can generate and modify teaching syllabuses based on uploaded documents.
        
        **Usage Instructions:**
        1. Upload a document (PDF/TXT) using the file upload component
        2. Ask the chatbot to generate a syllabus from the document
        3. Modify the syllabus by providing specific instructions
        
        The syllabus follows a structured JSON format with stages, each containing:
        - Stage ID and description
        - Allowed media types for evaluation
        - Learning targets and knowledge points
        - Evaluation questions and answers
        
        **Multimedia content can be specified using tags:**
        - `<image>description</image>`
        - `<video>description</video>`
    </details>
    """

# File upload component strings
FILE_UPLOAD_LABEL = "Upload Document"
FILE_UPLOAD_DESCRIPTION = """
    <details>
        <summary>Supported Document Formats</summary>
        
        - PDF documents (recommended for best results)
        - Text files (.txt)
    </details>
    """

# Success and error message templates
SUCCESS_SYLLABUS_TEMPLATE = """
<div class="success-status">
<strong>✅ Success!</strong> Syllabus "{}" generated.
<br>Target audience: {}
<br>Number of stages: {}
<br><br>You can now click 'Start Teaching Session' to begin teaching, or expand 'Current Syllabus' above to see details.
</div>
"""

TEACHING_SUCCESS_TEMPLATE = """
<div class="success-status">
<strong>✅ Ready to teach!</strong> Syllabus "{}" loaded successfully.
<br>Target audience: {}
<br>Number of stages: {}
<br><br>Click "Start Teaching" below to begin the teaching session.
</div>
"""

ERROR_NO_SYLLABUS = """
<div class="error-status">
<strong>⚠️ No valid syllabus found.</strong> Please generate a syllabus first by:
<br>1. Upload a document using the file uploader
<br>2. Type "Generate a syllabus from this document" in the chat
</div>
"""

ERROR_NO_SELECTION = """
<div class="error-status">
<strong>⚠️ No syllabus selected.</strong> Please select a syllabus from the dropdown.
</div>
"""

ERROR_SELECTION_NOT_FOUND = """
<div class="error-status">
<strong>⚠️ Selected syllabus not found.</strong> Please try generating a new syllabus.
</div>
"""

# Error messages for teaching interface
NO_SYLLABUS_TEACHING_ERROR = "Sorry, there's no syllabus available for teaching. Please go back to the 'Generate Syllabus' tab and generate a syllabus first."
NO_DOCUMENT_ERROR = "Please upload a document first to generate a syllabus."