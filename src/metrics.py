"""Metriques d'evaluation simples, sans dependance externe."""

from typing import Any


def safe_divide(a: float, b: float) -> float:
    """Division qui retourne 0.0 si le denominateur est nul."""
    if b == 0:
        return 0.0
    return a / b


def compute_accuracy(items: list[dict[str, Any]]) -> float:
    """Calcule l'accuracy globale (expected_label == predicted_label).

    Ignore les items pour lesquels predicted_label est None.
    """
    valid = [i for i in items if i.get("predicted_label") is not None]
    if not valid:
        return 0.0
    correct = sum(
        1 for i in valid if i.get("predicted_label") == i.get("expected_label")
    )
    return correct / len(valid)


def compute_confusion_matrix(
    items: list[dict[str, Any]], labels: list[str]
) -> dict[str, dict[str, int]]:
    """Construit une matrice de confusion.

    matrix[expected][predicted] = nombre d'items.
    Les valeurs predites hors de la liste de labels sont regroupees dans
    une colonne 'unknown'.
    """
    extended_labels = labels + ["unknown"]
    matrix: dict[str, dict[str, int]] = {
        true_label: {pred_label: 0 for pred_label in extended_labels}
        for true_label in labels
    }

    for item in items:
        true_label = item.get("expected_label")
        pred_label = item.get("predicted_label")
        if true_label not in matrix:
            continue
        if pred_label in matrix[true_label]:
            matrix[true_label][pred_label] += 1
        else:
            matrix[true_label]["unknown"] += 1

    return matrix


def compute_precision_recall_f1(
    items: list[dict[str, Any]], labels: list[str]
) -> dict[str, dict[str, float]]:
    """Calcule precision, rappel et F1 par classe.

    Retourne un dict {label: {"precision": x, "recall": y, "f1": z, "support": n}}.
    """
    results: dict[str, dict[str, float]] = {}

    for label in labels:
        tp = sum(
            1
            for i in items
            if i.get("expected_label") == label and i.get("predicted_label") == label
        )
        fp = sum(
            1
            for i in items
            if i.get("expected_label") != label and i.get("predicted_label") == label
        )
        fn = sum(
            1
            for i in items
            if i.get("expected_label") == label and i.get("predicted_label") != label
        )
        support = sum(1 for i in items if i.get("expected_label") == label)

        precision = safe_divide(tp, tp + fp)
        recall = safe_divide(tp, tp + fn)
        f1 = safe_divide(2 * precision * recall, precision + recall)

        results[label] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": support,
        }

    return results
