from dataclasses import dataclass
from typing import Optional


@dataclass
class PromptResult:
    id: str
    prompt: str
    expected_risk: bool
    predicted_risk: Optional[bool]
    sensitive_data_detected: Optional[bool]
    sanitized_prompt: Optional[str]
    issues: str
    safe_prompt: Optional[str]
    latency_seconds: Optional[float]
    technical_error: Optional[str]
    classification: str
