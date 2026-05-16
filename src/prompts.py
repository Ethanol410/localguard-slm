"""Construction des prompts envoyes au modele SLM local."""


def build_classification_prompt(message: str) -> str:
    """Construit le prompt de classification d'un message unique.

    Le prompt est en francais et impose au modele une sortie JSON stricte
    avec les champs label, risk_level, confidence et reason.
    """
    return f"""Tu es un classifieur de messages courts en francais.

Tu dois classer le message suivant selon son type et son niveau de risque relationnel.

Tu reponds UNIQUEMENT par un objet JSON valide, sans texte avant ni apres, sans bloc Markdown.

Le JSON doit respecter ce schema exactement :

{{
  "label": "neutral | constructive_criticism | insult | humiliation | exclusion | threat | ambiguous",
  "risk_level": "none | low | medium | high",
  "confidence": 0.0,
  "reason": "explication courte en francais, une phrase maximum"
}}

Regles strictes :
- Tu classes uniquement le message fourni, sans inventer de contexte.
- Tu ne fais pas de morale, tu ne donnes pas de conseil, tu ne reponds pas au message.
- Le champ confidence est un nombre entre 0 et 1.
- Le champ reason fait moins de 20 mots.
- Si le message est ironique ou difficile a interpreter, utilise label = ambiguous.

Definitions :
- neutral : echange courant sans agressivite.
- constructive_criticism : critique honnete et utile, formulee correctement.
- insult : injure ou attaque verbale directe.
- humiliation : message qui rabaisse, ridiculise ou humilie publiquement.
- exclusion : message qui exclut ou met de cote une personne du groupe.
- threat : menace explicite ou implicite contre une personne.
- ambiguous : sens incertain, sarcasme ou sous-entendu sans certitude.

Message a classer :
\"\"\"{message}\"\"\"

Reponds par le JSON uniquement."""
