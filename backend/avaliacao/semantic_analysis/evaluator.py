import traceback
from typing import Dict, List, Optional

from ..models import PromptResult
from .pipeline import classify, run_pipeline


def evaluate(
    dataset: List[Dict],
    limit: Optional[int] = None,
) -> List[PromptResult]:
    results: List[PromptResult] = []
    subset = dataset[:limit] if limit else dataset
    total = len(subset)

    for i, item in enumerate(subset, start=1):
        prompt_id = item["id"]
        prompt = item["prompt"]
        expected_risk = item["expected_risk"]

        print(f"[{i}/{total}] Avaliando {prompt_id}...", end=" ", flush=True)

        try:
            pipeline_out = run_pipeline(prompt)
        except Exception as exc:
            pipeline_out = {
                "predicted_risk": None,
                "issues": [],
                "safe_prompt": None,
                "latency_seconds": None,
                "technical_error": f"{type(exc).__name__}: {exc}",
            }
            traceback.print_exc()

        predicted_risk = pipeline_out["predicted_risk"]
        classification = classify(expected_risk, predicted_risk)

        result = PromptResult(
            id=prompt_id,
            prompt=prompt,
            expected_risk=expected_risk,
            predicted_risk=predicted_risk,
            sensitive_data_detected=None,
            sanitized_prompt=None,
            issues="; ".join(pipeline_out["issues"]) if pipeline_out["issues"] else "",
            safe_prompt=pipeline_out["safe_prompt"],
            latency_seconds=pipeline_out["latency_seconds"],
            technical_error=pipeline_out["technical_error"],
            classification=classification,
        )
        results.append(result)

        print(f"esperado={expected_risk} previsto={predicted_risk} -> {classification}")

    return results
