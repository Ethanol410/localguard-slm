"""Script de classification des messages via le modele SLM local.

Usage :
    python src/classify_messages.py --model gemma3:1b --limit 10
"""

import argparse
import json
import sys
from pathlib import Path

# Permet l'import quand le script est lance depuis la racine du projet.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import (
    DEFAULT_INPUT_PATH,
    DEFAULT_MODEL,
    DEFAULT_OLLAMA_BASE_URL,
    DEFAULT_OUTPUT_PATH,
)
from json_utils import parse_model_json, validate_prediction
from ollama_client import chat_with_ollama
from prompts import build_classification_prompt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Classifie un jeu de messages via un SLM local (Ollama)."
    )
    parser.add_argument("--input", type=str, default=str(DEFAULT_INPUT_PATH))
    parser.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL)
    parser.add_argument("--base-url", type=str, default=DEFAULT_OLLAMA_BASE_URL)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--temperature", type=float, default=0.0)
    return parser.parse_args()


def load_messages(path: Path) -> list[dict]:
    if not path.exists():
        print(f"[ERREUR] Fichier introuvable : {path}", file=sys.stderr)
        sys.exit(1)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def classify_one(message: dict, model: str, base_url: str, temperature: float) -> dict:
    """Classifie un message unique et retourne le resultat complet."""
    prompt = build_classification_prompt(message["text"])
    response = chat_with_ollama(prompt, model=model, base_url=base_url, temperature=temperature)

    result: dict = {
        "id": message["id"],
        "text": message["text"],
        "expected_label": message["expected_label"],
        "expected_risk_level": message["expected_risk_level"],
        "predicted_label": None,
        "predicted_risk_level": None,
        "confidence": None,
        "reason": None,
        "latency_seconds": round(response["latency_seconds"], 3),
        "json_valid": False,
        "warnings": [],
        "error": response["error"],
        "model": model,
    }

    if response["error"]:
        return result

    data, parse_error = parse_model_json(response["raw_content"])
    if data is None:
        result["error"] = f"parsing JSON impossible : {parse_error}"
        result["warnings"] = [f"raw_content (tronque) : {(response['raw_content'] or '')[:200]}"]
        return result

    normalized, warnings = validate_prediction(data)
    result["json_valid"] = True
    result["predicted_label"] = normalized["label"]
    result["predicted_risk_level"] = normalized["risk_level"]
    result["confidence"] = normalized["confidence"]
    result["reason"] = normalized["reason"]
    result["warnings"] = warnings
    return result


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    messages = load_messages(input_path)
    if args.limit is not None:
        messages = messages[: args.limit]

    total = len(messages)
    print(f"Classification de {total} messages avec le modele '{args.model}'.")
    print(f"Ollama : {args.base_url}")
    print(f"Temperature : {args.temperature}")
    print()

    results: list[dict] = []
    first_error_reported = False
    for idx, msg in enumerate(messages, start=1):
        print(f"[{idx}/{total}] classification du message id={msg['id']}...", flush=True)
        result = classify_one(
            msg,
            model=args.model,
            base_url=args.base_url,
            temperature=args.temperature,
        )
        results.append(result)

        if result["error"] and not first_error_reported:
            print(f"    -> ERREUR : {result['error']}", flush=True)
            first_error_reported = True

    # Ecriture du fichier de sortie.
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "config": {
                    "model": args.model,
                    "base_url": args.base_url,
                    "temperature": args.temperature,
                    "input_path": str(input_path),
                    "n_messages": total,
                },
                "results": results,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print(f"Resultats ecrits dans : {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
