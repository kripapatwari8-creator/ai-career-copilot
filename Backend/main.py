import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import PyPDF2

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use correct Gemini model
model = genai.GenerativeModel("gemini-flash-latest")
# FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request schema
class ResumeRequest(BaseModel):
    resume_text: str


# AI Resume Analysis Function
def analyze_resume_with_ai(resume):

    prompt = f"""
    Analyze the following resume carefully.

    Resume:
    {resume}

    Return ONLY valid JSON in this exact format:

    {{
      "resume_score": 85,
      "strengths": ["Good projects"],
      "weaknesses": ["Needs internships"],
      "suggestions": ["Add more achievements"],
      "found_skills": ["Python", "React"],
      "missing_skills": ["Docker"],
      "faang_readiness": 72,
      "predicted_role": "Frontend Developer"
    }}

    IMPORTANT:
    - Return ONLY JSON
    - No markdown
    - No explanation
    """

    response = model.generate_content(prompt)

    raw_text = response.text.strip()

    # Remove markdown if Gemini adds it
    cleaned = raw_text.replace("```json", "").replace("```", "").strip()

    return json.loads(cleaned)


# TEXT Resume Endpoint
@app.post("/analyze")
def analyze_resume(data: ResumeRequest):

    try:

        result = analyze_resume_with_ai(data.resume_text)

        return result

    except Exception as e:

        return {
            "resume_score": 0,
            "strengths": [],
            "weaknesses": [],
            "suggestions": [str(e)],
            "found_skills": [],
            "missing_skills": [],
            "faang_readiness": 0,
            "predicted_role": "Error"
        }


# PDF Upload Endpoint
@app.post("/upload")
async def upload_resume(file: UploadFile = File(...)):

    try:

        pdf_reader = PyPDF2.PdfReader(file.file)

        text = ""

        for page in pdf_reader.pages:

            extracted = page.extract_text()

            if extracted:
                text += extracted

        result = analyze_resume_with_ai(text)

        return result

    except Exception as e:

        return {
            "resume_score": 0,
            "strengths": [],
            "weaknesses": [],
            "suggestions": [str(e)],
            "found_skills": [],
            "missing_skills": [],
            "faang_readiness": 0,
            "predicted_role": "PDF Upload Error"
        }