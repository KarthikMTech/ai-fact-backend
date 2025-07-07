import os
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai

# Check API key presence
api_key = os.getenv("GEMINI_API_KEY")

print ("Gemini API Key Printed:" + api_key);
if not api_key:
    raise RuntimeError("❌ GEMINI_API_KEY is missing. Set it in your environment.")

# Configure Gemini
genai.configure(api_key=api_key)

# Initialize model
try:
    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
except Exception as e:
    raise RuntimeError(f"❌ Failed to initialize Gemini model: {e}")

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
  "description": "2-4 lines of explanation"
}
Give 1 interesting fact about: "{category}"
"""

@app.get("/fact")
def get_fact(category: str = Query(...)):
    prompt = TEMPLATE.format(category=category)

    try:
        response = model.generate_content(prompt)
        content = response.text.strip()

        print("🔍 Gemini raw response:\n", content)

        return json.loads(content)

    except json.JSONDecodeError as e:
        return {
            "error": f"❌ Failed to parse JSON: {str(e)}",
            "raw_response": content
        }
    except Exception as e:
        return {
            "error": f"❌ Failed to fetch fact: {str(e)}"
        }

# Optional model listing endpoint
@app.get("/models")
def list_models():
    return [m.name for m in genai.list_models()]
