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

TEMPLATE = """Give 1 interesting fact about the category "{category}" in the following JSON format:
{{
  "title": "string",
  "image_url": "optional string",
  "description": "string, 2-4 lines",
  "reference": "url"
}}"""


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

    try:
        response = model.generate_content(prompt)
        content = response.text
        print("Gemini raw response:\n", content)
        print("Gemini selected Context:\n", response['choices'][0]['message']['content'])
        return json.loads(content)
    except Exception as e:
        return {"error": f"Failed to fetch fact: {e}"}
