"""Genere un rapport Markdown a partir des resultats de classification.

Usage :
    python src/evaluate_results.py --input results/benchmark_results.json
"""

import argparse
import json
import statistics
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import (
    ALLOWED_LABELS,
    DEFAULT_ANALYSIS_PATH,
    DEFAULT_OUTPUT_PATH,
)
from metrics import (
    compute_accuracy,
    compute_confusion_matrix,
    compute_precision_recall_f1,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Calcule les metriques et genere un rapport Markdown."
    )
    parser.add_argument("--input", type=str, default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--output", type=str, default=str(DEFAULT_ANALYSIS_PATH))
    return parser.parse_args()


def format_pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def build_metrics_table(per_label: dict[str, dict[str, float]]) -> str:
    lines = [
        "| Label | Precision | Rappel | F1 | Support |",
        "| --- | --- | --- | --- | --- |",
    ]
    for label in ALLOWED_LABELS:
        m = per_label.get(label, {})
        lines.append(
            f"| `{label}` | {format_pct(m.get('precision', 0.0))} "
            f"| {format_pct(m.get('recall', 0.0))} "
            f"| {format_pct(m.get('f1', 0.0))} "
            f"| {int(m.get('support', 0))} |"
        )
    return "\n".join(lines)


def build_confusion_matrix_md(matrix: dict[str, dict[str, int]]) -> str:
    columns = ALLOWED_LABELS + ["unknown"]
    header = "| Attendu \\ Predit | " + " | ".join(f"`{c}`" for c in columns) + " |"
    separator = "| --- " * (len(columns) + 1) + "|"
    lines = [header, separator]
    for true_label in ALLOWED_LABELS:
        row = matrix.get(true_label, {})
        cells = [str(row.get(col, 0)) for col in columns]
        lines.append(f"| `{true_label}` | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def build_errors_section(items: list[dict], max_examples: int = 10) -> str:
    errors = [
        i
        for i in items
        if i.get("predicted_label") is not None
        and i.get("predicted_label") != i.get("expected_label")
    ]
    if not errors:
        return "Aucune erreur de classification observee sur ce jeu de test (a interpreter avec prudence : dataset tres petit)."

    lines = [f"Nombre total d'erreurs : **{len(errors)}**", ""]
    for err in errors[:max_examples]:
        lines.append(
            f"- id={err['id']} | attendu=`{err['expected_label']}` "
            f"| predit=`{err['predicted_label']}` "
            f"| conf={err.get('confidence', 0):.2f}"
        )
        lines.append(f"    > {err['text']}")
        reason = err.get("reason") or ""
        if reason:
            lines.append(f"    > Justification modele : {reason}")
        lines.append("")
    return "\n".join(lines)


def build_failures_section(items: list[dict]) -> str:
    failures = [i for i in items if i.get("error")]
    if not failures:
        return "Aucune erreur d'appel modele (parsing JSON et reponses Ollama OK)."
    lines = [f"Nombre d'erreurs techniques : **{len(failures)}**", ""]
    for f in failures[:5]:
        lines.append(f"- id={f['id']} : {f['error']}")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"[ERREUR] Fichier introuvable : {input_path}", file=sys.stderr)
        return 1

    with input_path.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    config = payload.get("config", {})
    items: list[dict] = payload.get("results", [])
    total = len(items)
    if total == 0:
        print("[ERREUR] Aucun resultat a evaluer.", file=sys.stderr)
        return 1

    n_json_valid = sum(1 for i in items if i.get("json_valid"))
    json_valid_rate = n_json_valid / total

    accuracy = compute_accuracy(items)
    per_label = compute_precision_recall_f1(items, ALLOWED_LABELS)
    confusion = compute_confusion_matrix(items, ALLOWED_LABELS)

    latencies = [i["latency_seconds"] for i in items if i.get("latency_seconds") is not None]
    mean_latency = statistics.fmean(latencies) if latencies else 0.0
    median_latency = statistics.median(latencies) if latencies else 0.0
    max_latency = max(latencies) if latencies else 0.0

    macro_f1 = sum(m["f1"] for m in per_label.values()) / max(len(per_label), 1)

    report = f"""# LocalGuard SLM - rapport d'analyse

> Rapport genere automatiquement le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.
> Mini PoC exploratoire sur un dataset fictif de petite taille. Les chiffres ci-dessous
> sont indicatifs et ne doivent pas etre interpretes comme la performance d'un outil reel.

## Resume executif

- Modele utilise : `{config.get('model', 'inconnu')}`
- Messages traites : **{total}**
- Reponses JSON valides : **{n_json_valid}/{total}** ({format_pct(json_valid_rate)})
- Accuracy globale : **{format_pct(accuracy)}**
- F1 macro (moyenne non ponderee) : **{format_pct(macro_f1)}**
- Latence moyenne : **{mean_latency:.2f} s** (mediane {median_latency:.2f} s, max {max_latency:.2f} s)

## Configuration du test

| Parametre | Valeur |
| --- | --- |
| Modele | `{config.get('model', 'inconnu')}` |
| URL Ollama | `{config.get('base_url', 'inconnu')}` |
| Temperature | {config.get('temperature', 'inconnu')} |
| Fichier source | `{Path(config.get('input_path', 'inconnu')).name}` |
| Nombre de messages | {total} |

## Resultats globaux

| Indicateur | Valeur |
| --- | --- |
| Accuracy | {format_pct(accuracy)} |
| F1 macro | {format_pct(macro_f1)} |
| Taux de JSON valide | {format_pct(json_valid_rate)} |
| Latence moyenne | {mean_latency:.2f} s |
| Latence mediane | {median_latency:.2f} s |
| Latence max | {max_latency:.2f} s |

## Metriques par label

{build_metrics_table(per_label)}

## Matrice de confusion

{build_confusion_matrix_md(confusion)}

## Exemples d'erreurs de classification

{build_errors_section(items)}

## Erreurs techniques (parsing ou appel Ollama)

{build_failures_section(items)}

## Observations qualitatives

- La sortie JSON forcee par `format=json` cote Ollama reduit fortement les erreurs de parsing par rapport a un prompt libre.
- Les categories ambigues sont, sans surprise, les plus difficiles : sarcasme et second degre peuvent etre lus comme neutres ou inversement comme menacants.
- La latence d'un modele 1B sur CPU reste compatible avec un usage interactif sur quelques messages, mais ne supporterait pas un debit eleve sans optimisation.

## Limites du test

- Dataset fictif et tres petit (30 messages), aucune signification statistique.
- Annotations realisees par une seule personne (moi), pas de double annotation ni d'accord inter-annotateurs.
- Pas de prise en compte du contexte conversationnel ni de la relation entre interlocuteurs.
- Une seule formulation de prompt testee, pas d'ablation systematique.
- Resultats dependants de la version exacte du modele tire via Ollama.

## Prochaines etapes

- Comparer plusieurs SLM (`gemma3:1b`, `qwen2.5:1.5b`, `llama3.2:1b`) sur le meme dataset.
- Tester des variantes de prompt (zero-shot vs few-shot, instructions courtes vs detaillees).
- Augmenter et faire valider le jeu de test.
- Ajouter une tache de resume et une tache d'extraction sur le meme corpus pour explorer la polyvalence d'un meme SLM.

## Synthese

Ce prototype montre qu'un SLM local de petite taille peut produire une classification structuree en JSON sur des messages courts en francais, avec une latence raisonnable sur machine standard. Les erreurs observees confirment que la detection fine de signaux faibles (humiliation, exclusion, ambiguite) reste un probleme difficile, qui demande des donnees annotees serieuses, du contexte et probablement une combinaison de SLM specialise et de regles metier.
"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(f"Rapport ecrit dans : {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
