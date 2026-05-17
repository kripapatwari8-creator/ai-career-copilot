from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv
import fitz
import os
import json

# =========================
# LOAD ENV
# =========================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# =========================
# GEMINI CLIENT
# =========================

client = genai.Client(api_key=GEMINI_API_KEY)

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
    return {
        "message": "AI Career Copilot Backend Running"
    }

# =========================
# PDF TEXT EXTRACTION
# =========================

def extract_pdf_text(pdf_bytes):

    text = ""

    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")

    for page in pdf_document:
        text += page.get_text()

    return text

# =========================
# AI ANALYSIS FUNCTION
# =========================

def analyze_resume(resume_text):

    prompt = f"""
You are an expert ATS Resume Analyzer and FAANG Career Mentor.

Analyze this resume deeply.

Return ONLY valid JSON.

JSON format:

{{
  "resume_score": number,
  "ats_score": number,
  "strengths": [],
  "weaknesses": [],
  "suggestions": [],
  "found_skills": [],
  "missing_skills": [],
  "faang_readiness": number,
  "predicted_role": "",
  "roadmap": [],
  "ai_feedback": ""
}}

Resume:

{resume_text}
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        raw_text = response.text.strip()

        raw_text = raw_text.replace("```json", "")
        raw_text = raw_text.replace("```", "")

        data = json.loads(raw_text)

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
            "ai_feedback": str(e)
        }

# =========================
# ANALYZE TEXT RESUME
# =========================

@app.post("/analyze")
def analyze_text_resume(data: ResumeRequest):

    return analyze_resume(data.resume_text)

# =========================
# UPLOAD PDF RESUME
# =========================

@app.post("/upload")
async def upload_resume(file: UploadFile = File(...)):

    try:

        pdf_bytes = await file.read()

        extracted_text = extract_pdf_text(pdf_bytes)

        result = analyze_resume(extracted_text)

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
            "ai_feedback": str(e)
        }