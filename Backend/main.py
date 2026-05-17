
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
# ROOT ROUTE
# =========================

@app.get("/")
def home():
    return {"message": "AI Career Copilot Backend Running"}

# =========================
# ANALYZE FUNCTION
# =========================

def analyze_resume_text(resume_text):

    prompt = f"""
    You are an expert ATS Resume Analyzer and FAANG Career Mentor.

    Analyze this resume carefully.

    Resume:
    {resume_text}

    Return ONLY valid JSON in this exact format:

    {{
      "resume_score": 85,
      "ats_score": 90,
      "strengths": ["point1", "point2"],
      "weaknesses": ["point1", "point2"],
      "suggestions": ["point1", "point2"],
      "found_skills": ["Python", "React"],
      "missing_skills": ["Docker", "AWS"],
      "faang_readiness": 80,
      "predicted_role": "Software Engineer",
      "roadmap": [
        "Step 1",
        "Step 2",
        "Step 3"
      ],
      "ai_feedback": "Detailed personalized career guidance here."
    }}
    """

    response = model.generate_content(prompt)

    text = response.text.strip()

    # remove markdown formatting
    text = text.replace("```json", "")
    text = text.replace("```", "")

    try:
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
            "ai_feedback": text
        }

# =========================
# TEXT RESUME API
# =========================

@app.post("/analyze")
async def analyze_resume(data: ResumeRequest):

    result = analyze_resume_text(data.resume_text)

    return result

# =========================
# PDF UPLOAD API
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
            "ai_feedback": ""
        }

