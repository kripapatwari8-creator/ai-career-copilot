from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv
import fitz  # PyMuPDF
import json

# =========================
# LOAD ENV VARIABLES
# =========================

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)

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
# PDF TEXT EXTRACTION
# =========================

def extract_text_from_pdf(pdf_bytes):

    text = ""

    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")

    for page in pdf_document:
        text += page.get_text()

    return text

# =========================
# AI ANALYSIS FUNCTION
# =========================

def analyze_resume_with_ai(resume_text):

    prompt = f"""
You are an expert ATS Resume Analyzer and FAANG Career Mentor.

Analyze this resume deeply.

Return ONLY valid JSON.

Resume:
{resume_text}

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
"""

    try:

        response = model.generate_content(prompt)

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
            "ai_feedback": "AI response failed."
        }

# =========================
# ROOT ROUTE
# =========================

@app.get("/")
def home():
    return {"message": "AI Career Copilot Backend Running"}

# =========================
# TEXT RESUME ANALYSIS
# =========================

@app.post("/analyze")
def analyze_resume(data: ResumeRequest):

    result = analyze_resume_with_ai(data.resume_text)

    return result

# =========================
# PDF UPLOAD ANALYSIS
# =========================

@app.post("/upload")
async def upload_resume(file: UploadFile = File(...)):

    pdf_bytes = await file.read()

    extracted_text = extract_text_from_pdf(pdf_bytes)

    result = analyze_resume_with_ai(extracted_text)

    return result