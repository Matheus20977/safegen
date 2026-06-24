import time
from typing import Dict, Optional

try:
    from local_analysis.sanitizer import sanitize
except ImportError:
    sanitize = None


def is_ready() -> bool:
    return sanitize is not None


def run_pipeline(prompt: str) -> Dict:
    start = time.perf_counter()

    try:
        sanitization_result = sanitize(prompt)
        sensitive_data = sanitization_result.get("sensitive_data")
        predicted_risk = None if sensitive_data is None else bool(sensitive_data)
        sanitized_prompt = sanitization_result.get("sanitized_prompt", prompt)
        technical_error = None

        if sanitization_result.get("error"):
            technical_error = f"phi3: {sanitization_result['error']}"

    except Exception as exc:
        predicted_risk = None
        sanitized_prompt = prompt
        technical_error = f"{type(exc).__name__}: {exc}"

    latency = time.perf_counter() - start

    return {
        "predicted_risk": predicted_risk,
        "sanitized_prompt": sanitized_prompt,
        "latency_seconds": latency,
        "technical_error": technical_error,
    }


def classify(expected: bool, predicted: Optional[bool]) -> str:
    if predicted is None:
        return "ERROR"
    if expected and predicted:
        return "TP"
    if not expected and predicted:
        return "FP"
    if not expected and not predicted:
        return "TN"
    return "FN"
