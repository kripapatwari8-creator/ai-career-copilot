from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import fitz
import os
import json

# =========================
# LOAD ENV VARIABLES
# =========================

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# =========================
# OPENROUTER CLIENT
# =========================

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

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
# ANALYZE FUNCTION
# =========================

def analyze_resume_text(resume_text):

    prompt = f"""
You are an expert ATS Resume Analyzer, FAANG Career Mentor, and Hiring Manager.

Analyze the following resume in depth.

Resume:
{resume_text}

IMPORTANT:
Return ONLY valid JSON.
DO NOT add markdown.
DO NOT add explanation outside JSON.

Use this EXACT structure:

{{
  "resume_score": 75,
  "ats_score": 88,
  "strengths": [
    "point1",
    "point2"
  ],
  "weaknesses": [
    "point1",
    "point2"
  ],
  "suggestions": [
    "point1",
    "point2"
  ],
  "found_skills": [
    "Python",
    "React"
  ],
  "missing_skills": [
    "Docker",
    "AWS"
  ],
  "faang_readiness": 40,
  "predicted_role": "Software Engineer",
  "roadmap": [
    "step1",
    "step2",
    "step3"
  ],
  "ai_feedback": "Very detailed personalized career guidance."
}}
"""

    try:

        completion = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2000,
        )

        text = completion.choices[0].message.content.strip()

        # remove markdown if AI adds it
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

        try:

            data = json.loads(text)

            return data

        except Exception as json_error:

            return {
                "resume_score": 0,
                "ats_score": 0,
                "strengths": [],
                "weaknesses": [],
                "suggestions": [f"JSON Parsing Error: {str(json_error)}"],
                "found_skills": [],
                "missing_skills": [],
                "faang_readiness": 0,
                "predicted_role": "Parsing Error",
                "roadmap": [],
                "ai_feedback": text
            }

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
            "predicted_role": "AI Service Unavailable",
            "roadmap": [],
            "ai_feedback": "The AI service is currently unavailable."
        }

# =========================
# TEXT ANALYSIS API
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

        if not text.strip():

            return {
                "resume_score": 0,
                "ats_score": 0,
                "strengths": [],
                "weaknesses": [],
                "suggestions": ["Could not extract text from PDF."],
                "found_skills": [],
                "missing_skills": [],
                "faang_readiness": 0,
                "predicted_role": "Invalid PDF",
                "roadmap": [],
                "ai_feedback": ""
            }

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