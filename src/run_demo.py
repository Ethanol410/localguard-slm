"""Pipeline complet : classification + evaluation.

Les fichiers de sortie sont automatiquement suffixes par le nom du modele,
ce qui permet d'enchainer plusieurs benchmarks sans ecraser les resultats.

Usage :
    python src/run_demo.py --model gemma3:latest --limit 10
    python src/run_demo.py --model gemma3:latest
    python src/run_demo.py --model qwen3:1.7b
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import (
    DEFAULT_ANALYSIS_PATH,
    DEFAULT_INPUT_PATH,
    DEFAULT_MODEL,
    DEFAULT_OLLAMA_BASE_URL,
    DEFAULT_OUTPUT_PATH,
)


def sanitize_model_name(model: str) -> str:
    """Convertit un nom de modele en suffixe de fichier valide.

    Exemple : 'qwen3:1.7b' -> 'qwen3_1_7b', 'gemma3:latest' -> 'gemma3_latest'.
    """
    return re.sub(r"[^a-zA-Z0-9]+", "_", model).strip("_").lower()


def add_suffix(path_str: str, suffix: str) -> str:
    """Insere un suffixe avant l'extension du fichier."""
    p = Path(path_str)
    return str(p.with_name(f"{p.stem}_{suffix}{p.suffix}"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pipeline complet LocalGuard SLM (classification + evaluation)."
    )
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--base-url", type=str, default=DEFAULT_OLLAMA_BASE_URL)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--input", type=str, default=str(DEFAULT_INPUT_PATH))
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Chemin du JSON resultats. Par defaut, suffixe par le nom du modele.",
    )
    parser.add_argument(
        "--analysis",
        type=str,
        default=None,
        help="Chemin du rapport Markdown. Par defaut, suffixe par le nom du modele.",
    )
    parser.add_argument(
        "--no-suffix",
        action="store_true",
        help="Desactive le suffixage automatique par nom de modele.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    suffix = sanitize_model_name(args.model)
    if args.no_suffix:
        output_path = args.output or str(DEFAULT_OUTPUT_PATH)
        analysis_path = args.analysis or str(DEFAULT_ANALYSIS_PATH)
    else:
        output_path = args.output or add_suffix(str(DEFAULT_OUTPUT_PATH), suffix)
        analysis_path = args.analysis or add_suffix(str(DEFAULT_ANALYSIS_PATH), suffix)

    # Etape 1 : classification.
    print("=" * 60)
    print(" Etape 1 / 2 : classification via Ollama")
    print("=" * 60)
    sys.argv = [
        "classify_messages.py",
        "--model", args.model,
        "--base-url", args.base_url,
        "--temperature", str(args.temperature),
        "--input", args.input,
        "--output", output_path,
    ]
    if args.limit is not None:
        sys.argv += ["--limit", str(args.limit)]

    import classify_messages

    rc = classify_messages.main()
    if rc != 0:
        return rc

    # Etape 2 : evaluation.
    print()
    print("=" * 60)
    print(" Etape 2 / 2 : evaluation et generation du rapport")
    print("=" * 60)
    sys.argv = [
        "evaluate_results.py",
        "--input", output_path,
        "--output", analysis_path,
    ]
    import evaluate_results

    rc = evaluate_results.main()
    if rc != 0:
        return rc

    print()
    print("Pipeline termine.")
    print(f"  - Resultats JSON   : {output_path}")
    print(f"  - Rapport Markdown : {analysis_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
