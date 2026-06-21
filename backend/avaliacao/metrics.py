from typing import List, Dict

from .models import PromptResult


def compute_metrics(results: List[PromptResult]) -> Dict:
    tp = sum(1 for r in results if r.classification == "TP")
    fp = sum(1 for r in results if r.classification == "FP")
    tn = sum(1 for r in results if r.classification == "TN")
    fn = sum(1 for r in results if r.classification == "FN")
    errors = sum(1 for r in results if r.classification == "ERROR")

    total_classified = tp + fp + tn + fn

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0
    accuracy = (tp + tn) / total_classified if total_classified > 0 else 0.0

    latencies = [r.latency_seconds for r in results if r.latency_seconds is not None]
    avg_latency = sum(latencies) / len(latencies) if latencies else None

    return {
        "total_prompts": len(results),
        "total_classificados": total_classified,
        "erros_tecnicos": errors,
        "matriz_confusao": {
            "verdadeiro_positivo_TP": tp,
            "falso_positivo_FP": fp,
            "verdadeiro_negativo_TN": tn,
            "falso_negativo_FN": fn,
        },
        "metricas": {
            "precisao": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "taxa_falsos_positivos_FPR": round(fpr, 4),
            "taxa_falsos_negativos_FNR": round(fnr, 4),
            "acuracia": round(accuracy, 4),
        },
        "latencia_media_segundos": round(avg_latency, 3) if avg_latency is not None else None,
    }
