import os
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Load Gemini API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("❌ GEMINI_API_KEY is not set.")

genai.configure(api_key=api_key)

# Load the Gemini model
try:
    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
except Exception as e:
    raise RuntimeError(f"❌ Model initialization failed: {e}")

app = FastAPI()

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# FastAPI endpoint to fetch a fact
@app.get("/fact")
def get_fact(category: str = Query(...)):
    # ✅ Dynamically inject category
    prompt = f"""Respond only with a valid JSON object in this format without any explanation:
{{
  "title": "Fact title",
  "image_url": "https://optional-image.com",
  "description": "2-4 lines of explanation",
  "reference": "https://source.com"
}}
Give 1 interesting fact about: "{category}"
"""

    try:
        response = model.generate_content(prompt)
        content = response.text.strip()

        # Clean up markdown if present
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]

        content = content.strip()
        print("🔍 Gemini raw response:\n", content)

        return json.loads(content)

    except json.JSONDecodeError as e:
        return {"error": f"JSON decode failed: {e}", "raw": content}
    except Exception as e:
        return {"error": f"Internal server error: {e}"}

@app.get("/models")
def list_models():
    return [m.name for m in genai.list_models()]
