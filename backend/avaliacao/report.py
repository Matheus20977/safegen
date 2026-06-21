import csv
import json
import os
from dataclasses import asdict
from typing import List, Dict

from .models import PromptResult


def print_report(metrics: Dict) -> None:
    cm = metrics["matriz_confusao"]
    m = metrics["metricas"]

    print("\n" + "=" * 60)
    print("RELATÓRIO DE AVALIAÇÃO DO ANALISADOR SEMÂNTICO (Gemini)")
    print("=" * 60)
    print(f"Total de prompts avaliados : {metrics['total_prompts']}")
    print(f"Classificados com sucesso  : {metrics['total_classificados']}")
    print(f"Erros técnicos (timeout/JSON inválido/exceção) : {metrics['erros_tecnicos']}")
    print("-" * 60)
    print("Matriz de confusão:")
    print(f"  TP (inseguro detectado)         : {cm['verdadeiro_positivo_TP']}")
    print(f"  FP (seguro sinalizado indevido) : {cm['falso_positivo_FP']}")
    print(f"  TN (seguro não sinalizado)      : {cm['verdadeiro_negativo_TN']}")
    print(f"  FN (inseguro não detectado)     : {cm['falso_negativo_FN']}")
    print("-" * 60)
    print("Métricas:")
    print(f"  Precisão                  : {m['precisao']:.2%}")
    print(f"  Recall                    : {m['recall']:.2%}")
    print(f"  F1-score                  : {m['f1_score']:.2%}")
    print(f"  Taxa de falsos positivos  : {m['taxa_falsos_positivos_FPR']:.2%}")
    print(f"  Taxa de falsos negativos  : {m['taxa_falsos_negativos_FNR']:.2%}")
    print(f"  Acurácia geral            : {m['acuracia']:.2%}")
    if metrics["latencia_media_segundos"] is not None:
        print(f"  Latência média por prompt : {metrics['latencia_media_segundos']:.3f}s")
    print("=" * 60 + "\n")


def save_results(results: List[PromptResult], metrics: Dict, output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)

    # CSV detalhado, uma linha por prompt
    csv_path = os.path.join(output_dir, "resultados_detalhados.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = list(asdict(results[0]).keys()) if results else []
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(asdict(r))

    # métricas agregadas
    with open(os.path.join(output_dir, "metricas.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    # falsos positivos, falsos negativos e erros técnicos isolados
    falsos_positivos = [asdict(r) for r in results if r.classification == "FP"]
    falsos_negativos = [asdict(r) for r in results if r.classification == "FN"]
    erros_tecnicos = [asdict(r) for r in results if r.classification == "ERROR"]

    with open(os.path.join(output_dir, "falsos_positivos.json"), "w", encoding="utf-8") as f:
        json.dump(falsos_positivos, f, ensure_ascii=False, indent=2)

    with open(os.path.join(output_dir, "falsos_negativos.json"), "w", encoding="utf-8") as f:
        json.dump(falsos_negativos, f, ensure_ascii=False, indent=2)

    with open(os.path.join(output_dir, "erros_tecnicos.json"), "w", encoding="utf-8") as f:
        json.dump(erros_tecnicos, f, ensure_ascii=False, indent=2)

    print(f"Resultados salvos em: {output_dir}/")
    print("  - resultados_detalhados.csv")
    print("  - metricas.json")
    print("  - falsos_positivos.json")
    print("  - falsos_negativos.json")
    print("  - erros_tecnicos.json")
