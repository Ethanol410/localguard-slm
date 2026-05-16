# LocalGuard SLM - comparaison de modeles

> Rapport genere automatiquement le 2026-05-16 20:26:14.
> Mini PoC exploratoire sur un dataset fictif de 30 messages. Les chiffres ci-dessous
> sont indicatifs et n'ont pas de valeur statistique.

## Modeles compares

- `gemma3:latest` (30 messages)
- `llama3.2:1b` (30 messages)

## Tableau recapitulatif

| Indicateur | `gemma3:latest` | `llama3.2:1b` |
| --- | --- | --- |
| Messages traites | 30 | 30 |
| JSON valides | 30/30 | 30/30 |
| Taux JSON valide | 100.0% | 100.0% |
| **Accuracy** | **66.7%** | **30.0%** |
| **F1 macro** | **59.6%** | **16.9%** |
| Latence moyenne | 3.63 s | 4.64 s |
| Latence mediane | 3.62 s | 4.51 s |
| Latence max | 3.84 s | 6.09 s |

## F1 par classe (comparaison directe)

| Label | `gemma3:latest` | `llama3.2:1b` | Support |
| --- | --- | --- | --- |
| `neutral` | 83.3% | 90.9% | 6 |
| `constructive_criticism` | 80.0% | 0.0% | 4 |
| `insult` | 72.7% | 27.6% | 4 |
| `humiliation` | 0.0% | 0.0% | 4 |
| `exclusion` | 66.7% | 0.0% | 3 |
| `threat` | 85.7% | 0.0% | 3 |
| `ambiguous` | 28.6% | 0.0% | 6 |

## Detail precision / rappel par classe

### `neutral`

| Modele | Precision | Rappel | F1 | Support |
| --- | --- | --- | --- | --- |
| `gemma3:latest` | 83.3% | 83.3% | 83.3% | 6 |
| `llama3.2:1b` | 100.0% | 83.3% | 90.9% | 6 |

### `constructive_criticism`

| Modele | Precision | Rappel | F1 | Support |
| --- | --- | --- | --- | --- |
| `gemma3:latest` | 66.7% | 100.0% | 80.0% | 4 |
| `llama3.2:1b` | 0.0% | 0.0% | 0.0% | 4 |

### `insult`

| Modele | Precision | Rappel | F1 | Support |
| --- | --- | --- | --- | --- |
| `gemma3:latest` | 57.1% | 100.0% | 72.7% | 4 |
| `llama3.2:1b` | 16.0% | 100.0% | 27.6% | 4 |

### `humiliation`

| Modele | Precision | Rappel | F1 | Support |
| --- | --- | --- | --- | --- |
| `gemma3:latest` | 0.0% | 0.0% | 0.0% | 4 |
| `llama3.2:1b` | 0.0% | 0.0% | 0.0% | 4 |

### `exclusion`

| Modele | Precision | Rappel | F1 | Support |
| --- | --- | --- | --- | --- |
| `gemma3:latest` | 50.0% | 100.0% | 66.7% | 3 |
| `llama3.2:1b` | 0.0% | 0.0% | 0.0% | 3 |

### `threat`

| Modele | Precision | Rappel | F1 | Support |
| --- | --- | --- | --- | --- |
| `gemma3:latest` | 75.0% | 100.0% | 85.7% | 3 |
| `llama3.2:1b` | 0.0% | 0.0% | 0.0% | 3 |

### `ambiguous`

| Modele | Precision | Rappel | F1 | Support |
| --- | --- | --- | --- | --- |
| `gemma3:latest` | 100.0% | 16.7% | 28.6% | 6 |
| `llama3.2:1b` | 0.0% | 0.0% | 0.0% | 6 |


## Desaccords entre modeles

Nombre de desaccords : **19**

| id | attendu | `gemma3:latest` | `llama3.2:1b` | message |
| --- | --- | --- | --- | --- |
| 4 | `neutral` | `constructive_criticism` | **`neutral`** | Super travail sur le rapport, bravo. |
| 6 | `constructive_criticism` | **`constructive_criticism`** | `insult` | Ton rendu n'est pas encore au niveau, mais on peut l'ameliorer ensemble. |
| 7 | `constructive_criticism` | **`constructive_criticism`** | `insult` | Je pense que tu pourrais structurer ta presentation autrement, ce serait plus... |
| 8 | `constructive_criticism` | **`constructive_criticism`** | `insult` | Attention aux fautes dans le doc, prends le temps de te relire avant d'envoyer. |
| 9 | `constructive_criticism` | **`constructive_criticism`** | `insult` | Ton idee est interessante mais il manque des arguments pour convaincre. |
| 14 | `humiliation` | `exclusion` | `insult` | Tout le monde se moque de toi dans le groupe. |
| 17 | `humiliation` | `exclusion` | `insult` | Personne ne te prend au serieux ici, t'as pas remarque ? |
| 18 | `exclusion` | **`exclusion`** | `insult` | On devrait arreter de l'inviter, il sert a rien de toute facon. |
| 19 | `exclusion` | **`exclusion`** | `insult` | Faites le groupe sans elle, ca ira plus vite. |
| 20 | `exclusion` | **`exclusion`** | `insult` | Si tu viens en soiree, moi je viens pas. |
| 21 | `threat` | **`threat`** | `insult` | Tu vas regretter d'avoir dit ca. |
| 22 | `threat` | **`threat`** | `insult` | Fais gaffe a toi quand on se croisera dans les couloirs. |
| 23 | `threat` | **`threat`** | `insult` | Tu sais ce qui arrive a ceux qui me cherchent ? |
| 24 | `ambiguous` | `exclusion` | `insult` | Encore toi... bon courage a ceux qui doivent bosser avec toi. |
| 25 | `ambiguous` | `neutral` | `insult` | Mdr ouais c'est ca, t'es trop fort toi. |
| 27 | `ambiguous` | `constructive_criticism` | `insult` | Genial, encore une de tes idees... |
| 28 | `ambiguous` | `threat` | `insult` | On va voir si tu tiens jusqu'a la fin du projet. |
| 29 | `ambiguous` | **`ambiguous`** | `insult` | T'es special toi hein. |
| 30 | `neutral` | **`neutral`** | `insult` | C'etait sympa de bosser avec toi sur ce projet, on remet ca quand tu veux. |

## Conclusion rapide

- Meilleure accuracy : `gemma3:latest`
- Meilleur F1 macro : `gemma3:latest`
- Latence la plus basse : `gemma3:latest`
- Taux de JSON valide le plus eleve : `gemma3:latest`

A interpreter avec prudence : dataset fictif de 30 messages, aucune valeur statistique. L'objectif de cette comparaison est de degager une intuition sur les forces et faiblesses de chaque modele, pas de classer definitivement les SLM testes.

## Lecture du comparatif

La vraie valeur d'un comparatif comme celui-ci n'est pas le classement final, mais la lecture qu'il permet :
quelles classes resistent (typiquement les claires : `neutral`, `threat`), lesquelles cassent
(souvent `humiliation` et `ambiguous`), quel arbitrage latence vs qualite chaque modele propose,
et quelles confusions sont systematiques chez l'un mais pas l'autre.
