import sys

from .local_analysis.cli import main as local_main
from .semantic_analysis.cli import main as semantic_main


def main() -> None:
    # Compatibilidade: se não houver subcomando explícito, assume semantic_analysis.
    if len(sys.argv) == 1 or sys.argv[1].startswith("-"):
        semantic_main()
        return

    command = sys.argv[1]

    if command == "semantic_analysis":
        sys.argv = [sys.argv[0], *sys.argv[2:]]
        semantic_main()
        return

    if command == "local_analysis":
        sys.argv = [sys.argv[0], *sys.argv[2:]]
        local_main()
        return

    print(
        "Uso: python avaliar_analisadores.py [semantic_analysis|local_analysis] [opções]",
        file=sys.stderr,
    )
    sys.exit(2)
