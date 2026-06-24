import time
from typing import Dict, Optional

try:
    from semantic_analysis.gemini_client import analyze_security
except ImportError:
    analyze_security = None


def is_ready() -> bool:
    return analyze_security is not None


def run_pipeline(prompt: str) -> Dict:
    start = time.perf_counter()

    try:
        security_result = analyze_security(prompt)
        predicted_risk = bool(security_result.get("security_risk", False))
        issues = security_result.get("issues", [])
        safe_prompt = security_result.get("safe_prompt")
        technical_error = None

        if security_result.get("error"):
            technical_error = f"gemini: {security_result['error']}"

    except Exception as exc:
        predicted_risk = None
        issues = []
        safe_prompt = None
        technical_error = f"{type(exc).__name__}: {exc}"

    latency = time.perf_counter() - start

    return {
        "predicted_risk": predicted_risk,
        "issues": issues,
        "safe_prompt": safe_prompt,
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
