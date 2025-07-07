import os
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai

# Configure Gemini with your API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

app = FastAPI()

# Allow frontend CORS requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini prompt template
TEMPLATE = """Respond only with a valid JSON object in this format without any explanation:
{
  "title": "Fact title",
  "image_url": "https://optional-image.com",
  "description": "2-4 lines of explanation",
  "reference": "https://source.com"
}
Give 1 interesting fact about: "{category}"
"""

# Optional: Endpoint to list all models
@app.get("/models")
def list_models():
    return [m.name for m in genai.list_models()]

# Main /fact endpoint
@app.get("/fact")
def get_fact(category: str = Query(...)):
    prompt = TEMPLATE.format(category=category)

    try:
        response = model.generate_content(prompt)
        content = response.text.strip()

        # Debug: Log raw content
        print("🔍 Gemini raw response:\n", content)

        # Parse and return the response
        return json.loads(content)

    except json.JSONDecodeError as e:
        print("❌ JSON Decode Error:", str(e))
        return {
            "error": f"Failed to parse JSON: {str(e)}",
            "raw_response": content
        }

    except Exception as e:
        print("❌ General Exception:", str(e))
        return {
            "error": f"Failed to fetch fact: {str(e)}"
        }
