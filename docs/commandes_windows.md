# Commandes Windows - LocalGuard SLM

Toutes les commandes a executer dans un terminal Windows (PowerShell ou cmd) pour installer et lancer le projet.

## 1. Installer Python

Telecharger Python 3.10 ou superieur sur https://www.python.org/downloads/windows/

Pendant l'installation, cocher la case **Add Python to PATH**.

Verifier :

```bat
python --version
```

## 2. Aller dans le dossier du projet

```bat
cd D:\chemin\vers\localguard-slm
```

## 3. Creer un environnement virtuel

```bat
python -m venv .venv
```

## 4. Activer l'environnement virtuel

PowerShell :

```powershell
.venv\Scripts\Activate.ps1
```

Si PowerShell bloque les scripts, executer une fois :

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

cmd.exe :

```bat
.venv\Scripts\activate.bat
```

## 5. Installer les dependances

```bat
pip install -r requirements.txt
```

## 6. Installer Ollama

Telecharger l'installeur Windows depuis https://ollama.com/download

Apres installation, verifier :

```bat
ollama --version
```

Ollama tourne en arriere plan et expose une API sur `http://localhost:11434`.

## 7. Telecharger un modele

Modele par defaut :

```bat
ollama pull gemma3:1b
```

Alternatives :

```bat
ollama pull qwen2.5:1.5b
ollama pull llama3.2:1b
```

Lister les modeles disponibles :

```bat
ollama list
```

## 8. Lancer la demo (10 messages)

```bat
python src\run_demo.py --model gemma3:1b --limit 10
```

Ou via le script fourni :

```bat
run_localguard_windows.bat
```

## 9. Lancer le benchmark complet (30 messages)

```bat
python src\run_demo.py --model gemma3:1b
```

## 10. Lancer avec un autre modele

```bat
python src\run_demo.py --model qwen2.5:1.5b
python src\run_demo.py --model llama3.2:1b
```

## 11. Ou trouver les resultats

- `results\benchmark_results.json` : sorties brutes, latences, warnings
- `results\analysis.md` : rapport lisible

## 12. Erreurs frequentes

**`ConnectionError` vers `localhost:11434`**
Ollama n'est pas lance ou n'est pas installe. Lancer l'app Ollama ou taper `ollama list` pour verifier.

**`model 'gemma3:1b' not found`**
Le modele n'est pas tire localement. Faire `ollama pull gemma3:1b`.

**`pip` non reconnu**
L'environnement virtuel n'est pas active, ou Python n'est pas dans le PATH.

**Pyright signale des imports non resolus dans `src/*.py`**
Avertissement statique seulement. A l'execution, les scripts ajoutent `src/` a `sys.path` avant les imports, donc le code fonctionne.

**Latence tres elevee au premier appel**
Normal : Ollama charge le modele en memoire au premier appel. Les appels suivants sont plus rapides.
