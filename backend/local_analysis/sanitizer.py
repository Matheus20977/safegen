from local_analysis.phi3_client import analyze_sensitive_data

def sanitize(user_prompt: str) -> dict:
    result = analyze_sensitive_data(user_prompt)

    return {
        "sensitive_data": result.get("sensitive_data"),
        "sanitized_prompt": result.get("sanitized_prompt", user_prompt),
        "error": result.get("error")
    }
