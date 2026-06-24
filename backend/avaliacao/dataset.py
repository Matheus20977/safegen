import json
from typing import List, Dict


def load_dataset(path: str, label_field: str = "security_risk") -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    items: List[Dict] = []

    if isinstance(data, dict) and ("prompts_inseguros" in data or "prompts_seguros" in data):
        items.extend(data.get("prompts_inseguros", []))
        items.extend(data.get("prompts_seguros", []))
    elif isinstance(data, list):
        items = data
    else:
        raise ValueError("Formato de dataset não reconhecido. Esperado um dicionário com 'prompts_inseguros'/'prompts_seguros' ou uma lista de objetos.")

    normalized = []
    for idx, item in enumerate(items):
        normalized.append({
            "id": item.get("id", f"P-{idx:03d}"),
            "prompt": item["prompt"],
            "expected_risk": bool(item[label_field]),
        })
    return normalized
