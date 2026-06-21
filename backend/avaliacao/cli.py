import argparse
import sys

from .dataset import load_dataset
from .evaluator import evaluate
from .metrics import compute_metrics
from .report import print_report, save_results
from .pipeline import is_ready

# Avalia a qualidade do analisador semântico (Gemini)
# Retorno: precisão, recall, F1-score, taxa de falsos positivos e taxa de falsos negativos
# Entrada: dataset de prompts seguros e inseguros


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset", required=True,
        help="Caminho para o JSON com os prompts rotulados (ex: prompts_analise_semantica_gemini.json)."
    )
    parser.add_argument(
        "--output-dir", default="resultados",
        help="Diretório onde os relatórios serão salvos (padrão: ./resultados)."
    )
    parser.add_argument(
        "--delay", type=float, default=0.0,
        help="Tempo de espera entre chamadas para respeitar limites de taxa da API do Gemini (padrão: 0)."
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Avalia apenas os N primeiros prompts do dataset."
    )
    parser.add_argument(
        "--no-sanitize", action="store_true",
        help="Pula a etapa de sanitização local e envia o prompt original direto para o analisador semântico."
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not is_ready():
        print("ERRO: não foi possível importar o analisador semântico do Gemini. Verifique se as dependências do requirements.txt estão instaladas e se o .env contém a GEMINI_API_KEY.", file=sys.stderr)
        sys.exit(1)

    print(f"Carregando dataset: {args.dataset}")
    dataset = load_dataset(args.dataset)
    print(f"Dataset carregado: {len(dataset)} prompts ({sum(1 for d in dataset if d['expected_risk'])} inseguros, {sum(1 for d in dataset if not d['expected_risk'])} seguros).\n")

    results = evaluate(
        dataset,
        use_sanitizer=not args.no_sanitize,
        delay=args.delay,
        limit=args.limit,
    )

    metrics = compute_metrics(results)
    print_report(metrics)
    save_results(results, metrics, args.output_dir)
