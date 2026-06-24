import argparse
import os
import sys

from ..dataset import load_dataset
from ..metrics import compute_metrics
from ..report import print_report, save_results
from .evaluator import evaluate
from .pipeline import is_ready


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        default="prompts_analise_semantica_gemini.json",
        help=(
            "Caminho para o JSON com os prompts rotulados "
            "(padrão: prompts_analise_semantica_gemini.json)."
        ),
    )
    parser.add_argument(
        "--output-dir",
        default=os.path.join("resultados", "semantic_analysis"),
        help=(
            "Diretório onde os relatórios serão salvos "
            "(padrão: ./resultados/semantic_analysis)."
        ),
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Avalia apenas os N primeiros prompts do dataset.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not is_ready():
        print(
            "ERRO: não foi possível importar o analisador semântico do Gemini. "
            "Verifique as dependências do requirements.txt e se o .env contém "
            "GEMINI_API_KEY1, GEMINI_API_KEY2 e GEMINI_API_KEY3.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Carregando dataset semântico: {args.dataset}")
    dataset = load_dataset(args.dataset)
    print(
        f"Dataset carregado: {len(dataset)} prompts "
        f"({sum(1 for d in dataset if d['expected_risk'])} inseguros, "
        f"{sum(1 for d in dataset if not d['expected_risk'])} seguros).\n"
    )

    results = evaluate(dataset, limit=args.limit)
    metrics = compute_metrics(results)

    print_report(
        metrics,
        title="RELATÓRIO DE AVALIAÇÃO DO ANALISADOR SEMÂNTICO (Gemini)",
    )
    save_results(results, metrics, args.output_dir)
