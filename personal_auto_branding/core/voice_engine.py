"""
Voice Engine — injecte l'empreinte vocale du client dans chaque génération.
Garant que tous les contenus sonnent humains et cohérents avec l'identité du client.
"""

import anthropic
from config.settings import MODEL_MAIN


def construire_system_prompt(persona: dict) -> str:
    """Construit le system prompt personnalisé à partir de l'empreinte vocale."""
    p = persona["profil"]
    s = persona["strategie"]
    v = persona["voix"]

    return f"""Tu ghostwrites du contenu LinkedIn pour {p['nom']}.

IDENTITÉ :
- Métier : {p['metier']} | Entreprise : {p['entreprise']} | Ville : {p['ville']}
- {p['annees_experience']} ans d'expérience dans son domaine

OBJECTIF LINKEDIN :
- {s['objectif_principal']}
- Client idéal : {s['client_ideal']}
- Résultat mis en avant : {s['resultat_promis']}

EMPREINTE VOCALE :
{v['empreinte']}

RÈGLES ABSOLUES :
- Écrire à la première personne, comme si c'était {p['nom']} qui parle
- Sujets interdits : {v['sujets_interdits']}
- Maximum 1300 caractères par post (limite LinkedIn)
- Jamais de hashtags génériques (#motivation, #success, #mindset)
- Jamais de formules bateau ("Dans un monde où...", "En tant que...")
- Phrases courtes. Aérer le texte. Une idée par paragraphe.
- Terminer par UNE seule action : question OU CTA, jamais les deux"""


def valider_ton(contenu: str, persona: dict) -> dict:
    """Vérifie si un contenu est cohérent avec l'empreinte vocale du client."""
    client = anthropic.Anthropic()

    prompt = f"""Voici l'empreinte vocale d'un profil LinkedIn :

{persona['voix']['empreinte']}

Voici un post à analyser :

{contenu}

Évalue la cohérence vocale sur ces 4 critères (score 0-10 chacun) :
1. Authenticité (semble écrit par un humain, pas une IA)
2. Cohérence de ton (correspond au style décrit)
3. Clarté du message (idée principale immédiatement lisible)
4. Potentiel d'engagement (donne envie de réagir)

Réponds en JSON strict :
{{"authenticite": 0, "coherence_ton": 0, "clarte": 0, "engagement": 0, "score_global": 0, "suggestion": "..."}}"""

    message = client.messages.create(
        model=MODEL_MAIN,
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}],
    )

    import json
    try:
        texte = message.content[0].text
        debut = texte.find("{")
        fin = texte.rfind("}") + 1
        return json.loads(texte[debut:fin])
    except Exception:
        return {"score_global": 0, "suggestion": "Impossible de parser la réponse"}
