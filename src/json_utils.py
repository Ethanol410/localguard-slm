"""Utilitaires de parsing et validation des sorties JSON du modele."""

import json
import re
from typing import Any

from config import ALLOWED_LABELS, ALLOWED_RISK_LEVELS


_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)


def parse_model_json(raw_content: str | None) -> tuple[dict[str, Any] | None, str | None]:
    """Tente de parser le JSON renvoye par le modele.

    Strategie :
    1. parsing direct ;
    2. si echec, extraction du premier bloc {...} dans la reponse ;
    3. sinon erreur.

    Retourne (data, None) ou (None, error_message).
    """
    if not raw_content:
        return None, "contenu vide"

    try:
        return json.loads(raw_content), None
    except json.JSONDecodeError:
        pass

    match = _JSON_BLOCK_RE.search(raw_content)
    if not match:
        return None, "aucun bloc JSON detecte"

    candidate = match.group(0)
    try:
        return json.loads(candidate), None
    except json.JSONDecodeError as exc:
        return None, f"JSON invalide : {exc}"


def validate_prediction(data: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Valide et normalise une prediction.

    Corrige les valeurs invalides plutot que de rejeter, pour permettre
    de calculer des metriques meme sur des sorties partiellement malformees.
    """
    warnings: list[str] = []
    normalized: dict[str, Any] = {}

    # label
    raw_label = data.get("label")
    if isinstance(raw_label, str) and raw_label in ALLOWED_LABELS:
        normalized["label"] = raw_label
    else:
        normalized["label"] = "ambiguous"
        warnings.append(f"label invalide ou manquant : {raw_label!r}, force a 'ambiguous'")

    # risk_level
    raw_risk = data.get("risk_level")
    if isinstance(raw_risk, str) and raw_risk in ALLOWED_RISK_LEVELS:
        normalized["risk_level"] = raw_risk
    else:
        normalized["risk_level"] = "low"
        warnings.append(f"risk_level invalide ou manquant : {raw_risk!r}, force a 'low'")

    # confidence
    raw_conf = data.get("confidence")
    try:
        conf_value = float(raw_conf)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        conf_value = 0.0
        warnings.append(f"confidence invalide : {raw_conf!r}, force a 0.0")

    if conf_value < 0.0:
        warnings.append(f"confidence < 0 ({conf_value}), bornee a 0.0")
        conf_value = 0.0
    elif conf_value > 1.0:
        warnings.append(f"confidence > 1 ({conf_value}), bornee a 1.0")
        conf_value = 1.0

    normalized["confidence"] = conf_value

    # reason
    raw_reason = data.get("reason")
    if isinstance(raw_reason, str) and raw_reason.strip():
        normalized["reason"] = raw_reason.strip()
    else:
        normalized["reason"] = ""
        warnings.append("reason manquant ou vide")

    return normalized, warnings
