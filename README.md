# Teaching Syllabus Generator

A Gradio application that uses Gemini AI to generate teaching syllabuses from uploaded documents (PDF/TXT).

## Features

- Upload PDF or TXT documents
- Direct multimodal document processing using Gemini's `Part.from_uri` capability
- Generate structured teaching syllabuses using Gemini AI with JSON schema validation
- Modify and refine syllabuses through natural language instructions
- Support for multimedia content tags in the syllabus
- Robust error handling with fallback mechanisms

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
   python app/main.py
   ```

## Environment Variables

- `AWS_ACCESS_KEY_ID`: AWS access key for S3 uploads
- `AWS_SECRET_ACCESS_KEY`: AWS secret key for S3 uploads
- `AWS_REGION`: AWS region (default: us-east-1)
- `S3_BUCKET_NAME`: S3 bucket name for document uploads
- `VERTEX_PROJECT_ID`: Google Cloud project ID (default: funplus-ai)
- `VERTEX_LOCATION`: Google Cloud location (default: asia-east2)

## Usage

1. Open the application in your browser
2. Upload a document (PDF or TXT)
3. Send a message to generate a syllabus (e.g., "Generate a syllabus from this document")
4. Refine the syllabus with additional instructions (e.g., "Change the target audience to high school students")

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

## Technical Implementation

The application uses:

- **Gemini 1.5 Pro** for document analysis and syllabus generation
- **Multimodal document processing** with direct PDF/document analysis
- **Schema-based structured output** to ensure consistent JSON formatting
- **S3 storage** for document management
- **Gradio** for the interactive web interface 