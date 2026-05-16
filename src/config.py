"""Constantes de configuration du projet LocalGuard SLM."""

from pathlib import Path

# Modele par defaut. Modifiable via l'argument CLI --model.
DEFAULT_MODEL = "gemma3:1b"

# URL de base de l'API Ollama locale.
DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"

# Labels autorises pour la classification.
ALLOWED_LABELS = [
    "neutral",
    "constructive_criticism",
    "insult",
    "humiliation",
    "exclusion",
    "threat",
    "ambiguous",
]

# Niveaux de risque autorises.
ALLOWED_RISK_LEVELS = ["none", "low", "medium", "high"]

# Chemins par defaut, calcules relativement a la racine du projet.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_INPUT_PATH = _PROJECT_ROOT / "data" / "messages_test.json"
DEFAULT_OUTPUT_PATH = _PROJECT_ROOT / "results" / "benchmark_results.json"
DEFAULT_ANALYSIS_PATH = _PROJECT_ROOT / "results" / "analysis.md"
