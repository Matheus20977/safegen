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

def analyze_sensitive_data(user_prompt: str) -> dict:
    system_prompt = load_prompt()

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"{system_prompt}\n\nPrompt a analisar:\n{user_prompt}",
        "stream": False
    }

    response = requests.post(f"{OLLAMA_URL}/api/generate", json=payload)
    response.raise_for_status()

    raw = response.json().get("response", "")

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "sensitive_data": False,
            "sanitized_prompt": user_prompt,
            "error": "Resposta inválida do modelo local"
        }