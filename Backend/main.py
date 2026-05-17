from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import fitz
import json
import os
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

model = genai.GenerativeModel("gemini-flash-latest")

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
# HOME ROUTE
# =========================

@app.get("/")
def home():
    return {
        "message": "AI Career Copilot Backend Running"
    }

# =========================
# AI ANALYSIS FUNCTION
# =========================

def analyze_resume_with_ai(resume):

    prompt = f"""
Analyze this resume deeply for:

1. Resume quality
2. ATS optimization
3. FAANG readiness
4. Technical skills
5. Missing skills
6. Career roadmap

Resume:
{resume}

Return ONLY valid JSON.

{{
  "resume_score": 92,
  "ats_score": 88,
  "strengths": [],
  "weaknesses": [],
  "suggestions": [],
  "found_skills": [],
  "missing_skills": [],
  "ats_issues": [],
  "ats_keywords_missing": [],
  "faang_readiness": 85,
  "predicted_role": "",
  "roadmap": [],
  "ai_feedback": ""
}}
"""

    try:

        response = model.generate_content(prompt)

        text = response.text.strip()

        # Remove markdown formatting if Gemini adds it
        text = text.replace("```json", "")
        text = text.replace("```", "")

        result = json.loads(text)

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
            "ats_issues": [],
            "ats_keywords_missing": [],
            "faang_readiness": 0,
            "predicted_role": "Error",
            "roadmap": [],
            "ai_feedback": "AI analysis failed."
        }

# =========================
# ANALYZE TEXT RESUME
# =========================

@app.post("/analyze")
async def analyze_resume(data: dict):

    resume_text = data.get("resume_text", "")

    result = analyze_resume_with_ai(resume_text)

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

        result = analyze_resume_with_ai(text)

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
            "ats_issues": [],
            "ats_keywords_missing": [],
            "faang_readiness": 0,
            "predicted_role": "PDF Upload Error",
            "roadmap": [],
            "ai_feedback": "PDF processing failed."
        }