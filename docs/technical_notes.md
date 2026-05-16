# Notes techniques - LocalGuard SLM

Fiche de référence rapide sur les notions clés mobilisées par le projet : modèle local, sortie JSON structurée, classification multi-classes, métriques, et limites éthiques.

## SLM (Small Language Model)

**Définition.** Modèle de langage de taille réduite (typiquement quelques centaines de millions à quelques milliards de paramètres). Conjugue empreinte mémoire faible, latence basse et possibilité d'exécution locale, au prix d'une compréhension plus limitée que les grands modèles cloud.

**Lien projet.** Le modèle par défaut `gemma3:1b` est un SLM d'environ 1 milliard de paramètres, tournant sur CPU et embarquable à terme sur smartphone.

## Modèle local

**Définition.** Modèle dont les poids sont chargés et exécutés sur la machine de l'utilisateur, sans appel à un serveur distant. Souvent via un runtime dédié (Ollama, llama.cpp, MLC, ExecuTorch).

**Lien projet.** Tous les appels modèle passent par `http://localhost:11434`. Aucune donnée ne sort de la machine.

**Intérêt pour la détection de signaux de cyberharcèlement.** Les messages traités sont par nature sensibles. Garder le traitement en local évite d'envoyer ces contenus dans le cloud et limite les risques de fuite.

## Ollama

**Définition.** Runtime open source qui simplifie le téléchargement, la gestion et l'exposition d'un modèle local via une API HTTP locale, avec un format proche de l'API chat d'OpenAI.

**Lien projet.** Le client dans `src/ollama_client.py` appelle `/api/chat` en POST avec `format=json` pour forcer une réponse JSON. Pas de SDK requis : un POST avec `requests` suffit.

## JSON structuré (sortie modèle)

**Définition.** Réponse du modèle formatée strictement en JSON afin d'être exploitable automatiquement par le pipeline aval.

**Lien projet.** Le prompt impose un schéma fixe. Côté serveur, `format=json` aide. Côté client, `parse_model_json` tente un parsing direct puis une extraction du premier bloc `{...}`.

**Intérêt.** Sans format strict, on ne peut ni mesurer, ni stocker, ni chaîner avec d'autres systèmes. Un JSON contraint rend le pipeline industrialisable.

## Classification de texte

**Définition.** Tâche supervisée qui associe à chaque texte un label parmi un ensemble fini.

**Lien projet.** 7 labels : `neutral`, `constructive_criticism`, `insult`, `humiliation`, `exclusion`, `threat`, `ambiguous`. Approche multi-classes en zero-shot via prompt, rapide à mettre en place mais sensible à la formulation et sans garantie de calibration.

## Cyberharcèlement et signaux faibles

**Définition.** Le cyberharcèlement combine répétition, intentionnalité et asymétrie de pouvoir. Un message isolé suffit rarement à le caractériser. Les signaux faibles sont les indices subtils : exclusion implicite, humiliation publique discrète, menaces voilées, sarcasme ciblant une personne.

**Lien projet.** La présence d'un label `ambiguous` et d'un `risk_level` séparé du label reflète justement cette difficulté : un message peut sembler bénin tout en s'inscrivant dans une dynamique problématique.

**Limite.** La détection automatique de cyberharcèlement ne peut pas vivre au niveau du message isolé. Un SLM aide à remonter des signaux ; c'est la couche au-dessus (séquence, contexte, humain) qui décide.

## Benchmark

**Définition.** Démarche structurée de mesure des performances d'un système sur un jeu de test connu, dans des conditions reproductibles.

**Lien projet.** Le pipeline produit un fichier JSON brut plus un rapport Markdown : configuration, métriques, matrice de confusion, exemples d'erreurs. Reproductible par `python src/run_demo.py`.

## Accuracy

**Définition.** Proportion de prédictions correctes sur le total. Simple à comprendre, mais trompeuse en cas de classes déséquilibrées.

**Lien projet.** Calculée dans `metrics.compute_accuracy`. Affichée dans le rapport, mais à interpréter avec prudence : sur ce type de sujet, un modèle qui dit toujours `neutral` peut avoir une accuracy élevée tout en étant inutile.

## Précision

**Définition.** Pour une classe C : parmi tous les messages que le modèle prédit en C, combien le sont vraiment. Calcul : TP / (TP + FP).

**Lien projet.** Calculée par classe. Critique pour les classes sévères (`threat`, `humiliation`) : une mauvaise précision implique des faux positifs pénalisants pour les utilisateurs (accusation à tort).

## Rappel

**Définition.** Pour une classe C : parmi tous les messages réellement en C, combien le modèle a su détecter. Calcul : TP / (TP + FN).

**Lien projet.** Critique aussi pour les classes sévères : un faible rappel signifie qu'on rate des situations à risque.

## F1-score

**Définition.** Moyenne harmonique de la précision et du rappel. Pénalise les modèles qui sacrifient une dimension.

**Lien projet.** Calculé par classe et résumé par un F1 macro. Plus informatif que l'accuracy sur des classes déséquilibrées. C'est l'indicateur à regarder en premier dans le rapport, parce qu'il révèle les classes où le modèle s'effondre.

## Latence

**Définition.** Temps entre l'envoi de la requête et la réception de la réponse. Sur un SLM local, dépend du modèle, du matériel, du contexte envoyé et du nombre de tokens générés.

**Lien projet.** Mesurée par `time.perf_counter` autour de l'appel HTTP. Reportée par message et résumée (moyenne, médiane, max). Très dépendante du matériel : un passage sur smartphone via un runtime adapté permettrait une expérience temps réel.

## Limites éthiques

Toute classification automatique sur du contenu sensible peut avoir des conséquences réelles sur les utilisateurs : étiquetage erroné, biais de représentation, effet chilling sur la liberté d'expression.

Le README et les rapports rappellent que ce projet est un PoC, pas un outil déployable. Aucune décision automatique n'est prise en sortie. Sur ce type de sujet, un humain doit rester dans la boucle, et les outils doivent servir à remonter des signaux, pas à sanctionner.
