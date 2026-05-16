# LocalGuard SLM - rapport d'analyse

> Rapport genere automatiquement le 2026-05-16 20:26:51.
> Mini PoC exploratoire sur un dataset fictif de petite taille. Les chiffres ci-dessous
> sont indicatifs et ne doivent pas etre interpretes comme la performance d'un outil reel.

## Resume executif

- Modele utilise : `llama3.2:1b`
- Messages traites : **30**
- Reponses JSON valides : **30/30** (100.0%)
- Accuracy globale : **30.0%**
- F1 macro (moyenne non ponderee) : **16.9%**
- Latence moyenne : **4.64 s** (mediane 4.51 s, max 6.09 s)

## Configuration du test

| Parametre | Valeur |
| --- | --- |
| Modele | `llama3.2:1b` |
| URL Ollama | `http://localhost:11434` |
| Temperature | 0.0 |
| Fichier source | `messages_test.json` |
| Nombre de messages | 30 |

## Resultats globaux

| Indicateur | Valeur |
| --- | --- |
| Accuracy | 30.0% |
| F1 macro | 16.9% |
| Taux de JSON valide | 100.0% |
| Latence moyenne | 4.64 s |
| Latence mediane | 4.51 s |
| Latence max | 6.09 s |

## Metriques par label

| Label | Precision | Rappel | F1 | Support |
| --- | --- | --- | --- | --- |
| `neutral` | 100.0% | 83.3% | 90.9% | 6 |
| `constructive_criticism` | 0.0% | 0.0% | 0.0% | 4 |
| `insult` | 16.0% | 100.0% | 27.6% | 4 |
| `humiliation` | 0.0% | 0.0% | 0.0% | 4 |
| `exclusion` | 0.0% | 0.0% | 0.0% | 3 |
| `threat` | 0.0% | 0.0% | 0.0% | 3 |
| `ambiguous` | 0.0% | 0.0% | 0.0% | 6 |

## Matrice de confusion

| Attendu \ Predit | `neutral` | `constructive_criticism` | `insult` | `humiliation` | `exclusion` | `threat` | `ambiguous` | `unknown` |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `neutral` | 5 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| `constructive_criticism` | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 0 |
| `insult` | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 0 |
| `humiliation` | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 0 |
| `exclusion` | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 |
| `threat` | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 |
| `ambiguous` | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 0 |

## Exemples d'erreurs de classification

Nombre total d'erreurs : **21**

- id=6 | attendu=`constructive_criticism` | predit=`insult` | conf=0.50
    > Ton rendu n'est pas encore au niveau, mais on peut l'ameliorer ensemble.
    > Justification modele : tu as utilisé un langage colinistrant et ridicule, cela est inapproprié.

- id=7 | attendu=`constructive_criticism` | predit=`insult` | conf=0.50
    > Je pense que tu pourrais structurer ta presentation autrement, ce serait plus clair pour le jury.
    > Justification modele : tu as utilisé un langage condescendant et critiquant, ce qui est inapproprié dans une situation professionnelle.

- id=8 | attendu=`constructive_criticism` | predit=`insult` | conf=0.50
    > Attention aux fautes dans le doc, prends le temps de te relire avant d'envoyer.
    > Justification modele : attaque verbale directe, sens incertain

- id=9 | attendu=`constructive_criticism` | predit=`insult` | conf=0.50
    > Ton idee est interessante mais il manque des arguments pour convaincre.
    > Justification modele : Tu as utilisé un label trop vague et n'as pas fourni de preuves concretes pour soutenir ton argument.

- id=14 | attendu=`humiliation` | predit=`insult` | conf=0.50
    > Tout le monde se moque de toi dans le groupe.
    > Justification modele : attaque verbale directe, insulte publiquement

- id=15 | attendu=`humiliation` | predit=`insult` | conf=0.00
    > Tu fais honte a toute la promo avec tes questions debiles.
    > Justification modele : tu fais honte a toute la promo avec tes questions debiles.

- id=16 | attendu=`humiliation` | predit=`insult` | conf=0.00
    > Meme un enfant de 6 ans ferait mieux que toi sur ce projet.
    > Justification modele : ferait meme mieux que toi sur ce projet, un enfant de 6 ans.

- id=17 | attendu=`humiliation` | predit=`insult` | conf=0.50
    > Personne ne te prend au serieux ici, t'as pas remarque ?
    > Justification modele : tu as dit que personne ne te prend au serieux, mais tu n'as pas remarqué quoi que ce soit de plus.

- id=18 | attendu=`exclusion` | predit=`insult` | conf=0.50
    > On devrait arreter de l'inviter, il sert a rien de toute facon.
    > Justification modele : attaque verbale directe et injure publique

- id=19 | attendu=`exclusion` | predit=`insult` | conf=0.50
    > Faites le groupe sans elle, ca ira plus vite.
    > Justification modele : attaque verbale directe et ridicule de la personne.


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
