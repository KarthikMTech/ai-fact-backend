import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import json


USE_GEMINI = os.getenv("USE_GEMINI", "false").lower() == "true"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMPLATE = """Respond only with a valid JSON object in this format without any explanation:
{
  "title": "Fact title",
  "image_url": "https://optional-image.com",
  "description": "2-4 lines of explanation",
  "reference": "https://source.com"
}
Give 1 interesting fact about: "{category}"
"""

import google.generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

@app.get("/models")
def list_models():
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    return [m.name for m in genai.list_models()]

@app.get("/fact")
def get_fact(category: str = Query(...)):
    prompt = TEMPLATE.format(category=category)
    
    response = model.generate_content(prompt)
    content = response.text.strip()
    # For debugging:
    print("🔍 Gemini raw content:", content)
    
     try:
        return json.loads(content)
     except json.JSONDecodeError as e:
        return {"error": f"Failed to parse JSON: {e}", "raw_response": content}
