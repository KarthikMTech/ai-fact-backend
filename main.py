from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import os

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

if not USE_GEMINI:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
else:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel(model_name="gemini-pro")

@app.get("/models")
def list_models():
    return [m.name for m in genai.list_models()]

@app.get("/fact")
def get_fact(category: str = Query(...)):
    prompt = TEMPLATE.format(category=category)

    try:
        if USE_GEMINI:
            res = model.generate_content(prompt)
            content = res.text
        else:
            res = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            content = res['choices'][0]['message']['content']

        return eval(content)
    except Exception as e:
        return {"error": f"Failed to fetch fact: {e}"}
