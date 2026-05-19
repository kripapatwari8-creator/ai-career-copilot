from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
import fitz
import json
import os
import re

# =========================
# LOAD ENV
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
    return {"message": "AI Career Copilot Backend Running"}

# =========================
# MODELS
# =========================

MODELS = [
    "meta-llama/llama-3.1-8b-instruct:free",
    "microsoft/phi-3-mini-128k-instruct:free",
    "google/gemma-2-9b-it:free",
]

# =========================
# AI ANALYSIS
# =========================

def generate_ai_response(prompt):

    for model_name in MODELS:

        try:

            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert ATS Resume Analyzer and FAANG Career Mentor."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2500,
            )

            return completion.choices[0].message.content

        except Exception as e:

            print(f"Model failed: {model_name}")
            print(e)

            continue

    return None

# =========================
# ANALYZE FUNCTION
# =========================

def analyze_resume_text(resume_text):

    prompt = f"""
Analyze this resume carefully.

Resume:
{resume_text}

Return ONLY valid JSON.

Format:

{{
  "resume_score": 75,
  "ats_score": 88,
  "strengths": ["point1"],
  "weaknesses": ["point1"],
  "suggestions": ["point1"],
  "found_skills": ["Python"],
  "missing_skills": ["Docker"],
  "faang_readiness": 50,
  "predicted_role": "Software Engineer",
  "roadmap": [
    "Step 1",
    "Step 2"
  ],
  "ai_feedback": "Detailed personalized career guidance."
}}

Make the feedback extremely detailed and personalized.
"""

    response = generate_ai_response(prompt)

    if not response:

        return {
            "resume_score": 0,
            "ats_score": 0,
            "strengths": [],
            "weaknesses": [],
            "suggestions": [
                "All AI providers are currently rate limited. Please retry after some time."
            ],
            "found_skills": [],
            "missing_skills": [],
            "faang_readiness": 0,
            "predicted_role": "AI Service Unavailable",
            "roadmap": [],
            "ai_feedback": "The AI service is temporarily overloaded."
        }

    try:

        cleaned = re.sub(r"```json|```", "", response).strip()

        data = json.loads(cleaned)

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
            "predicted_role": "JSON Error",
            "roadmap": [],
            "ai_feedback": response
        }

# =========================
# ANALYZE TEXT API
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