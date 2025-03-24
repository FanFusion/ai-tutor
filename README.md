# Teaching Syllabus Generator and Tutor

A Gradio application that uses Gemini AI to generate teaching syllabuses from uploaded documents (PDF) and then provides an interactive teaching experience based on the generated syllabus.

## Features

- Upload PDF
- Direct multimodal document processing using Gemini's `Part.from_uri` capability
- Generate structured teaching syllabuses using Gemini AI with JSON schema validation
- Modify and refine syllabuses through natural language instructions
- Interactive teaching sessions based on the generated syllabus
- Support for multimedia content tags in both the syllabus and teaching responses
- Stage-by-stage progression through the teaching content
- Automatic evaluation of user answers with progress tracking

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your credentials:
   ```
   cp .env.example .env
   ```
4. Run the application:
   ```
   python main.py
   ```

## Environment Variables

- `AWS_ACCESS_KEY_ID`: AWS access key for S3 uploads
- `AWS_SECRET_ACCESS_KEY`: AWS secret key for S3 uploads
- `AWS_REGION`: AWS region (default: us-east-1)
- `S3_BUCKET_NAME`: S3 bucket name for document uploads
- `S3_ACCESS_HOST`: S3 access host for public URLs
- `AWS_S3_ENDPOINT`: S3 endpoint URL
- `GEMINI_CHAT_MODEL`: Gemini model for interactive teaching 

## Usage

### Syllabus Generation

1. Open the application in your browser
2. Go to the "Generate Syllabus" tab
3. Upload a document (PDF or TXT)
4. Send a message to generate a syllabus (e.g., "Generate a syllabus from this document")
5. Refine the syllabus with additional instructions if needed

### Interactive Teaching

1. After generating a syllabus, click the "Start Teaching" button
2. The application will switch to the "Teaching Session" tab
3. Click "Start Teaching" to begin the teaching session
4. Interact with the AI tutor by:
   - Asking questions about the content
   - Answering evaluation questions
   - Using the multimedia input buttons to add image or video descriptions
5. Use the navigation buttons to move between stages
6. Click "End Teaching" when you're done

## Syllabus Format

The generated syllabus follows this JSON structure:

```json
{
  "syllabus_name": "Name of the course",
  "target_audience": "Description of target audience",
  "syllabus": [
    {
      "stage_id": "1",
      "stage_description": "Description of this stage",
      "judge_media_allowed": ["image", "text"],
      "target": "Learning goal for this stage",
      "teaching_knowledge": ["Knowledge point 1", "Knowledge point 2"],
      "judge_question": "Question to evaluate understanding",
      "judge_answer": "Expected answer"
    }
  ]
}
```
