# LocalGuard SLM

Mini PoC Python d'évaluation comparative de Small Language Models locaux pour la classification de messages courts en français, avec un focus sur la détection de signaux liés au cyberharcèlement.

> Projet exploratoire à but pédagogique. Les données sont fictives et le jeu de test est volontairement petit. Les résultats n'ont aucune valeur scientifique et ne doivent pas être interprétés comme la performance d'un outil de production.

## Objectif

Mettre en place un pipeline reproductible qui :

1. lit un jeu de données fictif de 30 messages courts en français,
2. interroge un modèle SLM exécuté localement via Ollama,
3. force une sortie JSON exploitable,
4. mesure la latence,
5. compare les prédictions aux labels attendus,
6. produit un rapport Markdown lisible,
7. compare plusieurs modèles entre eux.

Le but est de manipuler concrètement la chaîne complète : prompt, format JSON, parsing tolérant, métriques, erreurs, faux positifs et limites, sans dépendance cloud.

## Pourquoi un SLM local

- **Confidentialité** : les messages traités peuvent être sensibles, on ne veut pas les envoyer dans le cloud.
- **Latence stable** et **coût nul** à l'inférence.
- Possibilité d'embarquer le modèle sur des terminaux contraints (PC, smartphone à terme).

Le compromis : une compréhension plus limitée que les grands modèles, donc le prompt et l'évaluation doivent être soignés.

## Architecture

```
localguard-slm/
├── README.md
├── requirements.txt
├── run_localguard_windows.bat
├── data/
│   └── messages_test.json
├── docs/
│   ├── technical_notes.md
│   └── commandes_windows.md
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── prompts.py
│   ├── ollama_client.py
│   ├── json_utils.py
│   ├── metrics.py
│   ├── classify_messages.py
│   ├── evaluate_results.py
│   ├── compare_models.py
│   └── run_demo.py
└── results/
    ├── benchmark_results_<modele>.json   (généré)
    ├── analysis_<modele>.md              (généré)
    └── comparison_*.md                   (généré)
```

## Labels et niveaux de risque

Sept labels :

- `neutral` : échange courant sans agressivité.
- `constructive_criticism` : critique honnête et utile, formulée correctement.
- `insult` : injure ou attaque verbale directe.
- `humiliation` : message qui rabaisse, ridiculise ou humilie publiquement.
- `exclusion` : message qui exclut ou met de côté une personne.
- `threat` : menace explicite ou implicite.
- `ambiguous` : sens incertain, sarcasme ou sous-entendu.

Quatre niveaux de risque : `none`, `low`, `medium`, `high`.

## Prérequis

- Windows 10 ou 11 (le projet fonctionne aussi sur Linux et macOS).
- Python 3.10 ou supérieur (testé sur 3.12).
- Ollama installé et lancé en local.
- Un modèle SLM disponible : `gemma3:1b`, `qwen3:1.7b`, `llama3.2:1b`, ou tout autre modèle d'Ollama.

## Installation rapide (Windows)

```bat
cd D:\chemin\vers\localguard-slm
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Installer Ollama

Télécharger l'installeur depuis https://ollama.com/download et l'exécuter. Ollama démarre ensuite automatiquement en arrière-plan et expose une API sur `http://localhost:11434`.

### Télécharger un modèle

```bat
ollama pull gemma3:1b
ollama pull qwen3:1.7b
ollama pull llama3.2:1b
```

## Lancer une démo (10 messages)

```bat
python src/run_demo.py --model gemma3:1b --limit 10
```

Ou via le script fourni :

```bat
run_localguard_windows.bat
```

## Lancer le benchmark complet (30 messages)

```bat
python src/run_demo.py --model gemma3:1b
```

Les fichiers de sortie sont automatiquement suffixés par le nom du modèle, ce qui permet d'enchaîner plusieurs benchmarks sans écraser les résultats précédents.

## Comparer plusieurs modèles

Une fois plusieurs benchmarks générés, lancer la comparaison :

```bat
python src/run_demo.py --model gemma3:latest
python src/run_demo.py --model qwen3:1.7b
python src/run_demo.py --model llama3.2:1b
python src/compare_models.py results/benchmark_results_*.json --output results/comparison_all.md
```

Le rapport produit un tableau récapitulatif, un F1 par classe pour chaque modèle, le détail précision/rappel par label, et la liste des messages sur lesquels les modèles divergent.

## Lire les résultats

Pour chaque benchmark, deux fichiers sont générés dans `results/` :

- `benchmark_results_<modele>.json` : prédictions brutes, latences, warnings, erreurs.
- `analysis_<modele>.md` : rapport lisible avec métriques, matrice de confusion et exemples d'erreurs.

Pour les comparaisons multi-modèles : `comparison_*.md`.

## Résultats du benchmark intégré

Trois modèles ont été benchmarkés sur le même dataset (voir `results/`) :

| Modèle | Taille | Accuracy | F1 macro | Latence moy. |
| --- | --- | --- | --- | --- |
| `gemma3:latest` | 4B | 66.7% | 59.6% | 3.63 s |
| `qwen3:1.7b` | 1.7B | 53.3% | 47.0% | 5.48 s |
| `llama3.2:1b` | 1B | 30.0% | 16.9% | 4.64 s |

Lecture rapide :

- **Profils complémentaires** : aucun modèle n'est strictement meilleur. `gemma3` attrape correctement les menaces, `qwen3` est le seul à détecter l'humiliation, `llama3.2` s'effondre sur 5 classes sur 7.
- **Taux de JSON valide à 100%** sur les trois modèles, grâce à `format=json` côté Ollama et un parsing tolérant côté Python.
- **Catégorie `humiliation` particulièrement difficile** : confondue avec `insult` ou `exclusion` selon le modèle.
- **Catégorie `ambiguous` largement sous-détectée** : les SLM en zero-shot préfèrent trancher plutôt que dire "je ne sais pas".

## Limites assumées

- Le jeu de données contient 30 messages fictifs uniquement. Les conclusions chiffrées sont indicatives.
- Les labels sont des annotations personnelles et peuvent être discutables sur les cas ambigus.
- Un SLM 1B à 4B paramètres a une compréhension du français limitée par rapport aux gros modèles.
- La détection du cyberharcèlement réel suppose un contexte (historique, relation entre interlocuteurs, répétition) qui n'est pas modélisé ici.
- Aucune validation humaine ni revue éthique n'a été conduite.

## Pistes d'amélioration

- Augmenter le jeu de test (plusieurs centaines de messages annotés en double aveugle).
- Tester du few-shot prompting et comparer à du zero-shot.
- Étudier la latence sur smartphone via un runtime adapté (llama.cpp, MLC, ExecuTorch).
- Mesurer la consommation mémoire et le temps de premier token (TTFT).
- Explorer une architecture en cascade : petit modèle qui filtre, gros modèle qui analyse les cas suspects.
- Ajouter d'autres tâches (résumé, extraction d'entités) sur le même corpus.

## Licence

MIT. Voir [LICENSE](LICENSE).
