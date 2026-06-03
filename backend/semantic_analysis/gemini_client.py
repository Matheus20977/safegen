import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

def load_prompt():
    prompt_path = os.path.join(os.path.dirname(__file__), "../prompts/gemini_prompt.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

def analyze_security(sanitized_prompt: str) -> dict:
    system_prompt = load_prompt()

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{system_prompt}\n\nPrompt a analisar:\n{sanitized_prompt}"}
                ]
            }
        ]
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()

    raw = response.json()
    text = raw["candidates"][0]["content"]["parts"][0]["text"]

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "security_risk": False,
            "issues": [],
            "safe_prompt": sanitized_prompt,
            "error": "Resposta inválida do modelo externo"
        }