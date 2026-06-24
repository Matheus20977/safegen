import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3:mini")

def load_prompt():
    prompt_path = os.path.join(os.path.dirname(__file__), "../prompts/phi3_prompt.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def _parse_model_response(raw: str, user_prompt: str) -> dict:
    cleaned_text = raw.strip()

    if cleaned_text.startswith("```"):
        lines = cleaned_text.splitlines()
        if len(lines) >= 3:
            cleaned_text = "\n".join(lines[1:-1]).strip()

    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        return {
            "sensitive_data": None,
            "sanitized_prompt": user_prompt,
            "error": "Resposta inválida do modelo local"
        }


def analyze_sensitive_data(user_prompt: str) -> dict:
    system_prompt = load_prompt()

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"{system_prompt}\n\nPrompt a analisar:\n{user_prompt}",
        "format": "json",
        "stream": False
    }

    response = requests.post(f"{OLLAMA_URL}/api/generate", json=payload)
    response.raise_for_status()

    raw = response.json().get("response", "")
    return _parse_model_response(raw, user_prompt)
