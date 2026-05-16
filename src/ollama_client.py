"""Client minimal pour l'API Ollama locale."""

import time
from typing import Any

try:
    import requests
except ImportError as exc:
    raise ImportError(
        "Le package 'requests' est requis. Installer via : pip install -r requirements.txt"
    ) from exc


def chat_with_ollama(
    prompt: str,
    model: str,
    base_url: str,
    temperature: float = 0.0,
    timeout_seconds: int = 60,
) -> dict[str, Any]:
    """Envoie un prompt a Ollama et retourne la reponse brute plus la latence.

    Le payload utilise format=json pour forcer une sortie JSON cote serveur.

    Retourne un dictionnaire avec les cles :
    - raw_content : str ou None
    - latency_seconds : float
    - model : str
    - error : str ou None
    """
    url = f"{base_url.rstrip('/')}/api/chat"
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "format": "json",
        "options": {
            "temperature": temperature,
        },
    }

    start = time.perf_counter()
    try:
        response = requests.post(url, json=payload, timeout=timeout_seconds)
    except requests.exceptions.ConnectionError:
        latency = time.perf_counter() - start
        return {
            "raw_content": None,
            "latency_seconds": latency,
            "model": model,
            "error": (
                f"Connexion impossible a Ollama sur {base_url}. "
                "Verifier qu'Ollama est lance (commande : ollama list)."
            ),
        }
    except requests.exceptions.Timeout:
        latency = time.perf_counter() - start
        return {
            "raw_content": None,
            "latency_seconds": latency,
            "model": model,
            "error": f"Timeout apres {timeout_seconds}s sur l'appel Ollama.",
        }
    except requests.exceptions.RequestException as exc:
        latency = time.perf_counter() - start
        return {
            "raw_content": None,
            "latency_seconds": latency,
            "model": model,
            "error": f"Erreur reseau : {exc}",
        }

    latency = time.perf_counter() - start

    if response.status_code != 200:
        return {
            "raw_content": None,
            "latency_seconds": latency,
            "model": model,
            "error": f"HTTP {response.status_code} : {response.text[:200]}",
        }

    try:
        data = response.json()
    except ValueError as exc:
        return {
            "raw_content": None,
            "latency_seconds": latency,
            "model": model,
            "error": f"Reponse non JSON cote serveur : {exc}",
        }

    # Ollama renvoie la reponse du modele dans message.content
    message = data.get("message") or {}
    raw_content = message.get("content")

    return {
        "raw_content": raw_content,
        "latency_seconds": latency,
        "model": model,
        "error": None,
    }
