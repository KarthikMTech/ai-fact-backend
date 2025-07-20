import os
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from dotenv import load_dotenv

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

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prompt template
TEMPLATE = """Respond only with a valid JSON object in this format without any explanation:
{
  "title": "Fact title",
  "image_url": "https://source.com",
  "description": "2-4 lines of explanation",
  "reference": "https://source.com"
}
Give 1 interesting fact about: "{category}"
"""

# Endpoint to return a fact
@app.get("/fact")
def get_fact(category: str = Query(...)):    
    prompt = TEMPLATE.format(category=category)

    try:
        response = model.generate_content(prompt)
        content = response.text.strip()

        print("🔍 Gemini raw response:\n", content)
        
        # Remove markdown formatting if present
        if content.startswith("```json"):
            content = content[7:]  # Remove "```json"
        if content.startswith("```"):
            content = content[3:]   # Remove "```"
        if content.endswith("```"):
            content = content[:-3]  # Remove closing "```"
        
        content = content.strip()
        print(content)
        return json.loads(content)
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e)}

@app.get("/models")
def list_models():
    return [m.name for m in genai.list_models()]
