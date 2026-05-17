from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
import fitz  # PyMuPDF
from dotenv import load_dotenv

# =========================
# LOAD ENV VARIABLES
# =========================

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)

# =========================
# GEMINI MODEL
# =========================

model = genai.GenerativeModel("gemini-2.5-flash")

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
# ROOT ROUTE
# =========================

@app.get("/")
def home():
    return {
        "message": "AI Career Copilot Backend Running Successfully"
    }

# =========================
# ANALYZE RESUME FUNCTION
# =========================

def analyze_resume_text(resume_text):

    prompt = f"""
You are an expert FAANG recruiter, ATS scanner, and career mentor.

Analyze the following resume carefully.

Resume:
{resume_text}

Return ONLY valid JSON in this exact format:

{{
    "resume_score": 85,
    "ats_score": 90,
    "strengths": [
        "strength1",
        "strength2"
    ],
    "weaknesses": [
        "weakness1",
        "weakness2"
    ],
    "suggestions": [
        "suggestion1",
        "suggestion2"
    ],
    "found_skills": [
        "Python",
        "React"
    ],
    "missing_skills": [
        "Docker",
        "AWS"
    ],
    "faang_readiness": 80,
    "predicted_role": "Software Engineer",
    "roadmap": [
        "Step 1",
        "Step 2"
    ],
    "ats_issues": [
        "Issue 1",
        "Issue 2"
    ],
    "ai_feedback": "Write a detailed personalized career guidance paragraph for the candidate."
}}

Rules:
- Resume score should be between 0-100.
- ATS score should be between 0-100.
- Give meaningful strengths and weaknesses.
- AI feedback MUST NOT be empty.
- Roadmap should contain at least 5 actionable steps.
- ATS issues should mention formatting/content issues.
- Return ONLY JSON.
"""

    try:

        response = model.generate_content(prompt)

        raw_text = response.text.strip()

        # Remove markdown formatting if Gemini adds it
        raw_text = raw_text.replace("```json", "")
        raw_text = raw_text.replace("```", "")

        import json

        result = json.loads(raw_text)

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
            "predicted_role": "Error",
            "roadmap": [],
            "ats_issues": [],
            "ai_feedback": "AI feedback could not be generated."
        }

# =========================
# TEXT RESUME ANALYSIS
# =========================

@app.post("/analyze")
def analyze_resume(data: ResumeRequest):

    result = analyze_resume_text(data.resume_text)

    return result

# =========================
# PDF UPLOAD
# =========================

@app.post("/upload")
async def upload_resume(file: UploadFile = File(...)):

    try:

        contents = await file.read()

        pdf = fitz.open(stream=contents, filetype="pdf")

        text = ""

        for page in pdf:
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
            "ats_issues": [],
            "ai_feedback": "PDF analysis failed."
        }