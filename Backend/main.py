
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv
import fitz
import json

# =========================
# LOAD ENV VARIABLES
# =========================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

# =========================
# GEMINI MODEL
# =========================

model = genai.GenerativeModel("gemini-1.5-flash")

# =========================
# FASTAPI APP
# =========================

app = FastAPI()

# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# REQUEST MODEL
# =========================

class ResumeRequest(BaseModel):
    resume_text: str

# =========================
# HOME ROUTE
# =========================

@app.get("/")
def home():
    return {"message": "AI Career Copilot Backend Running"}

# =========================
# ANALYZE FUNCTION
# =========================

def analyze_resume_text(resume_text):

    prompt = f"""
You are a world-class ATS Resume Analyzer, Career Mentor, and FAANG Hiring Expert.

Analyze the following resume deeply.

RESUME:
{resume_text}

Your task:
- Evaluate ATS compatibility
- Evaluate FAANG readiness
- Predict most suitable role
- Detect strengths and weaknesses
- Detect missing industry skills
- Generate a highly personalized career roadmap
- Generate detailed career guidance

IMPORTANT RULES:
- Be VERY detailed
- Be professional
- Give realistic insights
- Mention technical improvements
- Mention resume formatting quality
- Mention interview preparation guidance
- Mention project improvements
- Mention missing tools/frameworks
- Give detailed roadmap steps

Return ONLY valid JSON.

FORMAT:

{{
  "resume_score": 75,
  "ats_score": 88,

  "strengths": [
    "Detailed point",
    "Detailed point"
  ],

  "weaknesses": [
    "Detailed point",
    "Detailed point"
  ],

  "suggestions": [
    "Detailed suggestion",
    "Detailed suggestion"
  ],

  "found_skills": [
    "Python",
    "React"
  ],

  "missing_skills": [
    "Docker",
    "AWS"
  ],

  "faang_readiness": 50,

  "predicted_role": "Software Engineer",

  "roadmap": [
    "Detailed roadmap step",
    "Detailed roadmap step"
  ],

  "ai_feedback": "A VERY DETAILED personalized career analysis paragraph."
}}
"""

    try:

        response = model.generate_content(prompt)

        text = response.text.strip()

        # remove markdown wrappers
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

        data = json.loads(text)

        return data

    except Exception as e:

        return {
            "resume_score": 0,
            "ats_score": 0,
            "strengths": [],
            "weaknesses": [],
            "suggestions": [str(e)],
            "found_skills": [],
            "missing_skills": [],
            "faang_readiness": 0,
            "predicted_role": "Error",
            "roadmap": [],
            "ai_feedback": f"Error occurred: {str(e)}"
        }

# =========================
# TEXT ANALYSIS
# =========================

@app.post("/analyze")
async def analyze_resume(data: ResumeRequest):

    result = analyze_resume_text(data.resume_text)

    return result

# =========================
# PDF ANALYSIS
# =========================

@app.post("/upload")
async def upload_resume(file: UploadFile = File(...)):

    try:

        pdf_bytes = await file.read()

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        text = ""

        for page in doc:
            text += page.get_text()

        result = analyze_resume_text(text)

        return result

    except Exception as e:

        return {
            "resume_score": 0,
            "ats_score": 0,
            "strengths": [],
            "weaknesses": [],
            "suggestions": [str(e)],
            "found_skills": [],
            "missing_skills": [],
            "faang_readiness": 0,
            "predicted_role": "PDF Upload Error",
            "roadmap": [],
            "ai_feedback": f"PDF processing failed: {str(e)}"
        }

