from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
import fitz
import json
import os

# =========================
# LOAD ENV
# =========================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

# =========================
# FASTAPI
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
# ROOT
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

Analyze the following resume deeply.

Resume:
{resume_text}

Return ONLY VALID JSON.

Format:

{{
  "resume_score": 85,
  "ats_score": 90,
  "strengths": [],
  "weaknesses": [],
  "suggestions": [],
  "found_skills": [],
  "missing_skills": [],
  "faang_readiness": 80,
  "predicted_role": "",
  "roadmap": [],
  "ai_feedback": ""
}}
"""

    try:

        completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],
    temperature=0.5,
    max_tokens=2500
)

        text = completion.choices[0].message.content.strip()

        text = text.replace("```json", "")
        text = text.replace("```", "")

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
            "predicted_role": "AI Service Unavailable",
            "roadmap": [],
            "ai_feedback": "AI provider failed."
        }

# =========================
# ANALYZE TEXT
# =========================

@app.post("/analyze")
async def analyze_resume(data: ResumeRequest):

    result = analyze_resume_text(data.resume_text)

    return result

# =========================
# PDF UPLOAD
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