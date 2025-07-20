import os
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from dotenv import load_dotenv
#from some_module import model  # Your Gemini model
from typing import Set

load_dotenv()

# Check and set your Gemini API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("❌ GEMINI_API_KEY is not set in Render environment.")

genai.configure(api_key=api_key)

# Safely load model
try:
    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
except Exception as e:
    raise RuntimeError(f"❌ Model initialization failed: {e}")

app = FastAPI()

# Enable CORS if frontend is on different domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store shown facts (in memory)
shown_facts: Set[str] = set()

@app.get("/fact")
def get_fact(category: str = Query(...)):
    max_retries = 5
    attempt = 0

    while attempt < max_retries:
        # Dynamically build the prompt
        prompt = f"""Respond only with a valid JSON object in this format without any explanation:
{{
  "title": "Fact title",
  "image_url": "https://source.com",
  "description": "2-4 lines of explanation",
  "reference": "https://source.com"
}}
Give 1 interesting fact about: "{category}"
"""

        try:
            response = model.generate_content(prompt)
            content = response.text.strip()

            print("🔍 Gemini raw response:\n", content)

            # Clean markdown if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            content = content.strip()
            fact = json.loads(content)

            # Skip if already shown
            if fact["title"] in shown_facts:
                print(f"⚠️ Duplicate fact detected: {fact['title']}")
                attempt += 1
                continue

            shown_facts.add(fact["title"])
            return fact

        except Exception as e:
            print("❌ Error:", e)
            attempt += 1

    return {"error": "Could not fetch a new unique fact after multiple attempts."}

@app.get("/models")
def list_models():
    return [m.name for m in genai.list_models()]
