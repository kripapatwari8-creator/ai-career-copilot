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
# TRY AVAILABLE MODELS
# =========================

AVAILABLE_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
]

model = None

for model_name in AVAILABLE_MODELS:

    try:

        temp_model = genai.GenerativeModel(model_name)

        test = temp_model.generate_content("Hello")

        if test:

            model = temp_model
            print(f"Using Gemini Model: {model_name}")
            break

    except Exception as e:

        print(f"Model failed: {model_name}")
        print(e)

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
# RESUME ANALYZER
# =========================

def analyze_resume_text(resume_text):

    # =========================
    # IF MODEL FAILED
    # =========================

    if model is None:

        return {
            "resume_score": 0,
            "ats_score": 0,
            "strengths": [],
            "weaknesses": [],
            "suggestions": [
                "Gemini API quota exceeded OR invalid API key."
            ],
            "found_skills": [],
            "missing_skills": [],
            "faang_readiness": 0,
            "predicted_role": "AI Service Unavailable",
            "roadmap": [],
            "ai_feedback": "The AI service is currently unavailable due to API quota limits."
        }

    # =========================
    # PROMPT
    # =========================

    prompt = f"""
You are an expert ATS Resume Analyzer and FAANG Career Mentor.

Analyze the following resume deeply and professionally.

Resume:
{resume_text}

Return ONLY VALID JSON.

Format:

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
  "ai_feedback": "Give detailed personalized career guidance."
}}

IMPORTANT:
- Give detailed roadmap
- Give ATS-specific suggestions
- Give realistic FAANG readiness
- Give detailed career guidance paragraph
- Return ONLY JSON
"""

    # =========================
    # GEMINI CALL
    # =========================

    try:

        response = model.generate_content(prompt)

        text = response.text.strip()

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
            "predicted_role": "AI Error",
            "roadmap": [],
            "ai_feedback": f"Error occurred: {str(e)}"
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