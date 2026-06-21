import time
from typing import Dict, Optional

from local_analysis.sanitizer import sanitize

try:
    from semantic_analysis.gemini_client import analyze_security
except ImportError:
    analyze_security = None


def is_ready() -> bool:
    return analyze_security is not None


def run_pipeline(prompt: str, use_sanitizer: bool = True) -> Dict:
    start = time.perf_counter()
    technical_error = None
    sensitive_data_detected = None
    sanitized_prompt = prompt

    try:
        if use_sanitizer:
            # etapa 1: sanitização local de dados sensíveis (Phi-3 Mini)
            sanitize_result = sanitize(prompt)
            sensitive_data_detected = sanitize_result.get("sensitive_data")
            sanitized_prompt = sanitize_result.get("sanitized_prompt", prompt)
            if sanitize_result.get("error"):
                technical_error = f"sanitizer: {sanitize_result['error']}"

        # etapa 2: análise semântica de segurança (Gemini)
        security_result = analyze_security(sanitized_prompt)
        predicted_risk = bool(security_result.get("security_risk", False))
        issues = security_result.get("issues", [])
        safe_prompt = security_result.get("safe_prompt")

        if security_result.get("error"):
            err = f"gemini: {security_result['error']}"
            technical_error = f"{technical_error}; {err}" if technical_error else err

    except Exception as exc:
        predicted_risk = None
        issues = []
        safe_prompt = None
        technical_error = f"{type(exc).__name__}: {exc}"

    latency = time.perf_counter() - start

    return {
        "predicted_risk": predicted_risk,
        "sensitive_data_detected": sensitive_data_detected,
        "sanitized_prompt": sanitized_prompt,
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
