"""Genere un rapport Markdown comparant deux benchmarks (ou plus).

Usage :
    python src/compare_models.py results/benchmark_results_gemma3_latest.json results/benchmark_results_qwen3_1_7b.json
    python src/compare_models.py results/*.json --output results/comparison.md
"""

import argparse
import json
import statistics
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import ALLOWED_LABELS
from metrics import (
    compute_accuracy,
    compute_confusion_matrix,
    compute_precision_recall_f1,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare plusieurs benchmarks LocalGuard SLM."
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        help="Fichiers benchmark_results_*.json a comparer.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/comparison.md",
        help="Chemin du rapport Markdown de comparaison.",
    )
    return parser.parse_args()


def load_benchmark(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def format_pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def compute_summary(payload: dict) -> dict:
    """Calcule l'ensemble des metriques d'un benchmark."""
    items = payload.get("results", [])
    config = payload.get("config", {})
    total = len(items)

    n_json_valid = sum(1 for i in items if i.get("json_valid"))
    json_valid_rate = n_json_valid / total if total else 0.0

    accuracy = compute_accuracy(items)
    per_label = compute_precision_recall_f1(items, ALLOWED_LABELS)
    confusion = compute_confusion_matrix(items, ALLOWED_LABELS)

    latencies = [i["latency_seconds"] for i in items if i.get("latency_seconds") is not None]
    mean_latency = statistics.fmean(latencies) if latencies else 0.0
    median_latency = statistics.median(latencies) if latencies else 0.0
    max_latency = max(latencies) if latencies else 0.0

    macro_f1 = sum(m["f1"] for m in per_label.values()) / max(len(per_label), 1)

    return {
        "model": config.get("model", "inconnu"),
        "config": config,
        "n_messages": total,
        "n_json_valid": n_json_valid,
        "json_valid_rate": json_valid_rate,
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "per_label": per_label,
        "confusion": confusion,
        "mean_latency": mean_latency,
        "median_latency": median_latency,
        "max_latency": max_latency,
        "items": items,
    }


def build_overview_table(summaries: list[dict]) -> str:
    """Tableau recapitulatif global."""
    header = "| Indicateur | " + " | ".join(f"`{s['model']}`" for s in summaries) + " |"
    sep = "| --- " * (len(summaries) + 1) + "|"
    rows = [header, sep]

    def row(label: str, values: list[str]) -> str:
        return f"| {label} | " + " | ".join(values) + " |"

    rows.append(row("Messages traites", [str(s["n_messages"]) for s in summaries]))
    rows.append(row("JSON valides", [f"{s['n_json_valid']}/{s['n_messages']}" for s in summaries]))
    rows.append(row("Taux JSON valide", [format_pct(s["json_valid_rate"]) for s in summaries]))
    rows.append(row("**Accuracy**", [f"**{format_pct(s['accuracy'])}**" for s in summaries]))
    rows.append(row("**F1 macro**", [f"**{format_pct(s['macro_f1'])}**" for s in summaries]))
    rows.append(row("Latence moyenne", [f"{s['mean_latency']:.2f} s" for s in summaries]))
    rows.append(row("Latence mediane", [f"{s['median_latency']:.2f} s" for s in summaries]))
    rows.append(row("Latence max", [f"{s['max_latency']:.2f} s" for s in summaries]))
    return "\n".join(rows)


def build_f1_per_label_table(summaries: list[dict]) -> str:
    """Tableau F1 par classe pour chaque modele."""
    header = "| Label | " + " | ".join(f"`{s['model']}`" for s in summaries) + " | Support |"
    sep = "| --- " * (len(summaries) + 2) + "|"
    rows = [header, sep]
    for label in ALLOWED_LABELS:
        cells = []
        support = 0
        for s in summaries:
            m = s["per_label"].get(label, {})
            f1 = m.get("f1", 0.0)
            cells.append(format_pct(f1))
            support = int(m.get("support", 0))  # identique pour tous les modeles
        rows.append(f"| `{label}` | " + " | ".join(cells) + f" | {support} |")
    return "\n".join(rows)


def build_precision_recall_table(summaries: list[dict]) -> str:
    """Tableau detaille precision/rappel par classe."""
    blocks = []
    for label in ALLOWED_LABELS:
        block = [f"### `{label}`", ""]
        header = "| Modele | Precision | Rappel | F1 | Support |"
        sep = "| --- | --- | --- | --- | --- |"
        block.append(header)
        block.append(sep)
        for s in summaries:
            m = s["per_label"].get(label, {})
            block.append(
                f"| `{s['model']}` "
                f"| {format_pct(m.get('precision', 0.0))} "
                f"| {format_pct(m.get('recall', 0.0))} "
                f"| {format_pct(m.get('f1', 0.0))} "
                f"| {int(m.get('support', 0))} |"
            )
        block.append("")
        blocks.append("\n".join(block))
    return "\n".join(blocks)


def build_disagreements(summaries: list[dict]) -> str:
    """Liste les messages ou les modeles divergent (utile pour l'oral)."""
    if len(summaries) < 2:
        return "Comparaison necessite au moins 2 modeles."

    # Index par id pour chaque modele.
    by_id = [{i["id"]: i for i in s["items"]} for s in summaries]
    all_ids = sorted(set().union(*(set(d.keys()) for d in by_id)))

    rows = []
    for msg_id in all_ids:
        preds = []
        text = ""
        expected = ""
        for d in by_id:
            item = d.get(msg_id)
            if item is None:
                preds.append("absent")
                continue
            preds.append(item.get("predicted_label") or "erreur")
            text = item.get("text", "")
            expected = item.get("expected_label", "")
        if len(set(preds)) > 1:
            rows.append((msg_id, expected, preds, text))

    if not rows:
        return "Aucun desaccord entre les modeles sur ce jeu de test."

    header = (
        "| id | attendu | "
        + " | ".join(f"`{s['model']}`" for s in summaries)
        + " | message |"
    )
    sep = "| --- " * (len(summaries) + 3) + "|"
    lines = [f"Nombre de desaccords : **{len(rows)}**", "", header, sep]
    for msg_id, expected, preds, text in rows:
        # Met en gras la bonne reponse.
        pred_cells = []
        for p in preds:
            cell = f"`{p}`"
            if p == expected:
                cell = f"**{cell}**"
            pred_cells.append(cell)
        text_short = text.replace("|", "\\|")
        if len(text_short) > 80:
            text_short = text_short[:77] + "..."
        lines.append(
            f"| {msg_id} | `{expected}` | "
            + " | ".join(pred_cells)
            + f" | {text_short} |"
        )
    return "\n".join(lines)


def pick_best(summaries: list[dict], key: str, higher_is_better: bool = True) -> str:
    """Retourne le nom du modele qui maximise (ou minimise) une metrique."""
    if not summaries:
        return "n/a"
    sorted_s = sorted(summaries, key=lambda s: s[key], reverse=higher_is_better)
    return sorted_s[0]["model"]


def build_conclusion(summaries: list[dict]) -> str:
    best_acc = pick_best(summaries, "accuracy")
    best_f1 = pick_best(summaries, "macro_f1")
    best_lat = pick_best(summaries, "mean_latency", higher_is_better=False)
    best_json = pick_best(summaries, "json_valid_rate")

    lines = [
        f"- Meilleure accuracy : `{best_acc}`",
        f"- Meilleur F1 macro : `{best_f1}`",
        f"- Latence la plus basse : `{best_lat}`",
        f"- Taux de JSON valide le plus eleve : `{best_json}`",
        "",
        "A interpreter avec prudence : dataset fictif de 30 messages, aucune valeur statistique. "
        "L'objectif de cette comparaison est de degager une intuition sur les forces et faiblesses "
        "de chaque modele, pas de classer definitivement les SLM testes.",
    ]
    return "\n".join(lines)


def main() -> int:
    args = parse_args()

    paths = [Path(p) for p in args.inputs]
    missing = [p for p in paths if not p.exists()]
    if missing:
        for p in missing:
            print(f"[ERREUR] Fichier introuvable : {p}", file=sys.stderr)
        return 1

    summaries = [compute_summary(load_benchmark(p)) for p in paths]

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    report = f"""# LocalGuard SLM - comparaison de modeles

> Rapport genere automatiquement le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.
> Mini PoC exploratoire sur un dataset fictif de 30 messages. Les chiffres ci-dessous
> sont indicatifs et n'ont pas de valeur statistique.

## Modeles compares

{chr(10).join(f"- `{s['model']}` ({s['n_messages']} messages)" for s in summaries)}

## Tableau recapitulatif

{build_overview_table(summaries)}

## F1 par classe (comparaison directe)

{build_f1_per_label_table(summaries)}

## Detail precision / rappel par classe

{build_precision_recall_table(summaries)}

## Desaccords entre modeles

{build_disagreements(summaries)}

## Conclusion rapide

{build_conclusion(summaries)}

## Lecture du comparatif

La vraie valeur d'un comparatif comme celui-ci n'est pas le classement final, mais la lecture qu'il permet :
quelles classes resistent (typiquement les claires : `neutral`, `threat`), lesquelles cassent
(souvent `humiliation` et `ambiguous`), quel arbitrage latence vs qualite chaque modele propose,
et quelles confusions sont systematiques chez l'un mais pas l'autre.
"""

    output_path.write_text(report, encoding="utf-8")
    print(f"Rapport de comparaison ecrit dans : {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
