from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import fitz
import json
import os

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

MODEL_NAME = "deepseek/deepseek-chat-v3-0324:free"

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
You are an elite ATS Resume Analyzer and FAANG Career Mentor.

Analyze the following resume in EXTREME DETAIL.

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
  "ai_feedback": "Very detailed personalized career guidance."
}}
"""

    try:

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7
        )

        text = response.choices[0].message.content.strip()

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
            "predicted_role": "AI Service Error",
            "roadmap": [],
            "ai_feedback": str(e)
        }

# =========================
# TEXT ANALYSIS
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
            "ai_feedback": str(e)
        }