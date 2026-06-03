"""
Trend Radar — détecte les tendances dans la niche du client et génère des idées de posts.
Se base sur les sujets fournis et le secteur du client pour proposer du contenu timely.
"""

import json
from datetime import datetime
import anthropic
from config.settings import MODEL_MAIN


def generer_idees_posts(persona: dict, nb_idees: int = 10) -> list[dict]:
    """Génère des idées de posts adaptées à la niche et aux tendances actuelles."""
    client = anthropic.Anthropic()

    prompt = f"""Tu es un stratégiste de contenu LinkedIn expert.

Profil du compte :
- Métier : {persona['profil']['metier']}
- Secteur : {persona['profil']['entreprise']}
- Expertise : {persona['voix']['sujets_forces']}
- Client idéal : {persona['strategie']['client_ideal']}
- Objectif : {persona['strategie']['objectif_principal']}

Date actuelle : {datetime.now().strftime('%B %Y')}

Génère {nb_idees} idées de posts LinkedIn pour ce profil.
Pour chaque idée, propose le format le plus adapté.

Réponds en JSON strict :
{{
  "idees": [
    {{
      "sujet": "...",
      "angle": "...",
      "format": "liste|storytelling|avant_apres|opinion|tips|coulisses",
      "raison_engagement": "...",
      "urgence": "haute|moyenne|basse"
    }}
  ]
}}"""

    message = client.messages.create(
        model=MODEL_MAIN,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    texte = message.content[0].text
    debut = texte.find("{")
    fin = texte.rfind("}") + 1
    try:
        data = json.loads(texte[debut:fin])
        return data.get("idees", [])
    except Exception:
        return []


def detecter_sujet_viral(niche: str, tendances_recentes: list[str] = None) -> dict:
    """Identifie le sujet le plus susceptible de performer dans une niche donnée."""
    client = anthropic.Anthropic()

    contexte_tendances = ""
    if tendances_recentes:
        contexte_tendances = f"\nTendances récentes dans cette niche : {', '.join(tendances_recentes)}"

    prompt = f"""Dans la niche "{niche}" sur LinkedIn :
{contexte_tendances}

Quel est LE sujet de post qui a le plus de chances de performer en ce moment ?
Réponds en JSON : {{"sujet": "...", "angle": "...", "format": "...", "pourquoi": "..."}}"""

    message = client.messages.create(
        model=MODEL_MAIN,
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}],
    )

    texte = message.content[0].text
    debut = texte.find("{")
    fin = texte.rfind("}") + 1
    try:
        return json.loads(texte[debut:fin])
    except Exception:
        return {"sujet": niche, "angle": "tips pratiques", "format": "liste"}


def evaluer_pertinence_republication(
    persona: dict, contenu_externe: str, auteur_externe: str
) -> dict:
    """Évalue si un contenu externe mérite d'être republié par le client."""
    client = anthropic.Anthropic()

    prompt = f"""Un profil LinkedIn ({persona['profil']['nom']}, {persona['profil']['metier']}) envisage de republier ce contenu :

Auteur original : {auteur_externe}
Contenu : {contenu_externe[:500]}

Son client idéal : {persona['strategie']['client_ideal']}
Ses sujets forts : {persona['voix']['sujets_forces']}
Sujets interdits : {persona['voix']['sujets_interdits']}

Analyse en JSON :
{{
  "republier": true/false,
  "score_pertinence": 0-100,
  "raison": "...",
  "commentaire_suggere": "..."
}}

Le commentaire suggéré sera ajouté lors de la republication pour apporter de la valeur."""

    message = client.messages.create(
        model=MODEL_MAIN,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )

    texte = message.content[0].text
    debut = texte.find("{")
    fin = texte.rfind("}") + 1
    try:
        return json.loads(texte[debut:fin])
    except Exception:
        return {"republier": False, "score_pertinence": 0, "raison": "Erreur d'analyse"}
