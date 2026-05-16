# LocalGuard SLM - rapport d'analyse

> Rapport genere automatiquement le 2026-05-16 20:26:50.
> Mini PoC exploratoire sur un dataset fictif de petite taille. Les chiffres ci-dessous
> sont indicatifs et ne doivent pas etre interpretes comme la performance d'un outil reel.

## Resume executif

- Modele utilise : `gemma3:latest`
- Messages traites : **30**
- Reponses JSON valides : **30/30** (100.0%)
- Accuracy globale : **66.7%**
- F1 macro (moyenne non ponderee) : **59.6%**
- Latence moyenne : **3.63 s** (mediane 3.62 s, max 3.84 s)

## Configuration du test

| Parametre | Valeur |
| --- | --- |
| Modele | `gemma3:latest` |
| URL Ollama | `http://localhost:11434` |
| Temperature | 0.0 |
| Fichier source | `messages_test.json` |
| Nombre de messages | 30 |

## Resultats globaux

| Indicateur | Valeur |
| --- | --- |
| Accuracy | 66.7% |
| F1 macro | 59.6% |
| Taux de JSON valide | 100.0% |
| Latence moyenne | 3.63 s |
| Latence mediane | 3.62 s |
| Latence max | 3.84 s |

## Metriques par label

| Label | Precision | Rappel | F1 | Support |
| --- | --- | --- | --- | --- |
| `neutral` | 83.3% | 83.3% | 83.3% | 6 |
| `constructive_criticism` | 66.7% | 100.0% | 80.0% | 4 |
| `insult` | 57.1% | 100.0% | 72.7% | 4 |
| `humiliation` | 0.0% | 0.0% | 0.0% | 4 |
| `exclusion` | 50.0% | 100.0% | 66.7% | 3 |
| `threat` | 75.0% | 100.0% | 85.7% | 3 |
| `ambiguous` | 100.0% | 16.7% | 28.6% | 6 |

## Matrice de confusion

| Attendu \ Predit | `neutral` | `constructive_criticism` | `insult` | `humiliation` | `exclusion` | `threat` | `ambiguous` | `unknown` |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `neutral` | 5 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| `constructive_criticism` | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| `insult` | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 0 |
| `humiliation` | 0 | 0 | 2 | 0 | 2 | 0 | 0 | 0 |
| `exclusion` | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 |
| `threat` | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 |
| `ambiguous` | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 0 |

## Exemples d'erreurs de classification

Nombre total d'erreurs : **10**

- id=4 | attendu=`neutral` | predit=`constructive_criticism` | conf=0.95
    > Super travail sur le rapport, bravo.
    > Justification modele : C'est un compliment positif et encourageant sur le travail effectué.

- id=14 | attendu=`humiliation` | predit=`exclusion` | conf=0.85
    > Tout le monde se moque de toi dans le groupe.
    > Justification modele : Le message indique une situation d'exclusion et de moqueries.

- id=15 | attendu=`humiliation` | predit=`insult` | conf=0.85
    > Tu fais honte a toute la promo avec tes questions debiles.
    > Justification modele : Le message contient une injure directe et dénigrante envers le destinataire.

- id=16 | attendu=`humiliation` | predit=`insult` | conf=0.95
    > Meme un enfant de 6 ans ferait mieux que toi sur ce projet.
    > Justification modele : La phrase est une critique désobligeante et humiliante.

- id=17 | attendu=`humiliation` | predit=`exclusion` | conf=0.85
    > Personne ne te prend au serieux ici, t'as pas remarque ?
    > Justification modele : Le message exprime un sentiment d'exclusion et de dévalorisation.

- id=24 | attendu=`ambiguous` | predit=`exclusion` | conf=0.85
    > Encore toi... bon courage a ceux qui doivent bosser avec toi.
    > Justification modele : Expression désobligeante visant à exclure une personne du travail d'équipe.

- id=25 | attendu=`ambiguous` | predit=`neutral` | conf=0.80
    > Mdr ouais c'est ca, t'es trop fort toi.
    > Justification modele : Réponse affirmative et encourageante, sans connotation négative.

- id=26 | attendu=`ambiguous` | predit=`insult` | conf=0.85
    > T'inquiete, on a l'habitude avec toi.
    > Justification modele : L'expression 'on a l'habitude avec toi' est désobligeante et critique.

- id=27 | attendu=`ambiguous` | predit=`constructive_criticism` | conf=0.80
    > Genial, encore une de tes idees...
    > Justification modele : Critique légère, suggérant que l'idée est répétitive sans agressivité.

- id=28 | attendu=`ambiguous` | predit=`threat` | conf=0.85
    > On va voir si tu tiens jusqu'a la fin du projet.
    > Justification modele : La phrase suggère une menace implicite de fin de collaboration.


## Erreurs techniques (parsing ou appel Ollama)

Aucune erreur d'appel modele (parsing JSON et reponses Ollama OK).

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
