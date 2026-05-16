# LocalGuard SLM - rapport d'analyse

> Rapport genere automatiquement le 2026-05-16 20:26:50.
> Mini PoC exploratoire sur un dataset fictif de petite taille. Les chiffres ci-dessous
> sont indicatifs et ne doivent pas etre interpretes comme la performance d'un outil reel.

## Resume executif

- Modele utilise : `qwen3:1.7b`
- Messages traites : **30**
- Reponses JSON valides : **30/30** (100.0%)
- Accuracy globale : **53.3%**
- F1 macro (moyenne non ponderee) : **47.0%**
- Latence moyenne : **5.48 s** (mediane 4.98 s, max 9.82 s)

## Configuration du test

| Parametre | Valeur |
| --- | --- |
| Modele | `qwen3:1.7b` |
| URL Ollama | `http://localhost:11434` |
| Temperature | 0.0 |
| Fichier source | `messages_test.json` |
| Nombre de messages | 30 |

## Resultats globaux

| Indicateur | Valeur |
| --- | --- |
| Accuracy | 53.3% |
| F1 macro | 47.0% |
| Taux de JSON valide | 100.0% |
| Latence moyenne | 5.48 s |
| Latence mediane | 4.98 s |
| Latence max | 9.82 s |

## Metriques par label

| Label | Precision | Rappel | F1 | Support |
| --- | --- | --- | --- | --- |
| `neutral` | 50.0% | 83.3% | 62.5% | 6 |
| `constructive_criticism` | 50.0% | 100.0% | 66.7% | 4 |
| `insult` | 100.0% | 25.0% | 40.0% | 4 |
| `humiliation` | 100.0% | 50.0% | 66.7% | 4 |
| `exclusion` | 100.0% | 33.3% | 50.0% | 3 |
| `threat` | 0.0% | 0.0% | 0.0% | 3 |
| `ambiguous` | 37.5% | 50.0% | 42.9% | 6 |

## Matrice de confusion

| Attendu \ Predit | `neutral` | `constructive_criticism` | `insult` | `humiliation` | `exclusion` | `threat` | `ambiguous` | `unknown` |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `neutral` | 5 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| `constructive_criticism` | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| `insult` | 0 | 0 | 1 | 0 | 0 | 0 | 3 | 0 |
| `humiliation` | 1 | 0 | 0 | 2 | 0 | 0 | 1 | 0 |
| `exclusion` | 1 | 1 | 0 | 0 | 1 | 0 | 0 | 0 |
| `threat` | 1 | 1 | 0 | 0 | 0 | 0 | 1 | 0 |
| `ambiguous` | 2 | 1 | 0 | 0 | 0 | 0 | 3 | 0 |

## Exemples d'erreurs de classification

Nombre total d'erreurs : **14**

- id=4 | attendu=`neutral` | predit=`constructive_criticism` | conf=0.90
    > Super travail sur le rapport, bravo.
    > Justification modele : message positif et constructif, sans risque

- id=11 | attendu=`insult` | predit=`ambiguous` | conf=0.70
    > T'es vraiment con ou tu fais semblant ?
    > Justification modele : question ambiguë avec un ton implicite négatif

- id=12 | attendu=`insult` | predit=`ambiguous` | conf=0.70
    > Quel boulet serieux, j'en peux plus de toi.
    > Justification modele : sarcasme et ambiguïté de l'expression

- id=13 | attendu=`insult` | predit=`ambiguous` | conf=0.70
    > T'es la pire personne du groupe, sans deconner.
    > Justification modele : sarcasme et critique directe sans certitude

- id=16 | attendu=`humiliation` | predit=`neutral` | conf=0.80
    > Meme un enfant de 6 ans ferait mieux que toi sur ce projet.
    > Justification modele : Comparaison neutre sans agressivité ou intention malveillante

- id=17 | attendu=`humiliation` | predit=`ambiguous` | conf=0.60
    > Personne ne te prend au serieux ici, t'as pas remarque ?
    > Justification modele : sarcasme ou sous-entendu sans certitude

- id=18 | attendu=`exclusion` | predit=`constructive_criticism` | conf=0.90
    > On devrait arreter de l'inviter, il sert a rien de toute facon.
    > Justification modele : Critique honnête et utile, formulee correctement

- id=20 | attendu=`exclusion` | predit=`neutral` | conf=0.80
    > Si tu viens en soiree, moi je viens pas.
    > Justification modele : réponse courante sans agressivité

- id=21 | attendu=`threat` | predit=`constructive_criticism` | conf=0.70
    > Tu vas regretter d'avoir dit ca.
    > Justification modele : suggestion de feedback constructif avec tonne de regret

- id=22 | attendu=`threat` | predit=`ambiguous` | conf=0.70
    > Fais gaffe a toi quand on se croisera dans les couloirs.
    > Justification modele : sarcasm or understatement without clear intent


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
