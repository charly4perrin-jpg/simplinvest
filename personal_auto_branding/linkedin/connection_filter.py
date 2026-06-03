"""
Filtre de connexions — score les profils LinkedIn avant d'envoyer une demande.
Seuls les profils pertinents pour les objectifs du client sont ciblés.
"""

import json
import anthropic
from config.settings import MODEL_FAST
from linkedin.anti_ban import peut_effectuer_action, enregistrer_action, attendre_delai_humain


def scorer_profil(persona: dict, profil_cible: dict) -> dict:
    """
    Score un profil LinkedIn cible (0-100).
    Un score >= 60 déclenche une demande de connexion.
    """
    client = anthropic.Anthropic()

    prompt = f"""Évalue la pertinence de ce profil LinkedIn pour une demande de connexion.

Profil de l'envoyeur :
- Métier : {persona['profil']['metier']}
- Client idéal : {persona['strategie']['client_ideal']}
- Objectif : {persona['strategie']['objectif_principal']}

Profil cible :
- Nom : {profil_cible.get('nom', 'Inconnu')}
- Titre : {profil_cible.get('titre', '')}
- Entreprise : {profil_cible.get('entreprise', '')}
- Secteur : {profil_cible.get('secteur', '')}
- Localisation : {profil_cible.get('localisation', '')}
- Connexions communes : {profil_cible.get('connexions_communes', 0)}
- Actif récemment : {profil_cible.get('actif_recemment', False)}

Score sur 100 et justification en JSON :
{{
  "score": 0,
  "pertinent": true/false,
  "raison": "...",
  "message_connexion_suggere": "..."
}}

Le message de connexion doit faire maximum 2 lignes, naturel, pas commercial."""

    message = client.messages.create(
        model=MODEL_FAST,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )

    texte = message.content[0].text
    debut = texte.find("{")
    fin = texte.rfind("}") + 1
    try:
        result = json.loads(texte[debut:fin])
        result["profil"] = profil_cible
        return result
    except Exception:
        return {"score": 0, "pertinent": False, "raison": "Erreur d'analyse"}


def filtrer_et_connecter(
    client_id: str, persona: dict, profils_candidats: list[dict]
) -> dict:
    """Filtre une liste de profils et initie les connexions pertinentes."""
    resultats = {"connectes": [], "rejetes": [], "limite_atteinte": False}

    for profil in profils_candidats:
        verification = peut_effectuer_action(client_id, "connection")
        if not verification["autorise"]:
            resultats["limite_atteinte"] = True
            break

        scoring = scorer_profil(persona, profil)

        if scoring.get("score", 0) >= 60 and scoring.get("pertinent", False):
            # Simuler l'envoi (à brancher sur l'API LinkedIn réelle)
            succes = _envoyer_demande_connexion(
                profil=profil,
                message=scoring.get("message_connexion_suggere", ""),
            )
            if succes:
                enregistrer_action(client_id, "connection")
                resultats["connectes"].append({
                    "profil": profil.get("nom"),
                    "score": scoring["score"],
                    "message": scoring.get("message_connexion_suggere"),
                })
                attendre_delai_humain("connection")
        else:
            resultats["rejetes"].append({
                "profil": profil.get("nom"),
                "score": scoring.get("score", 0),
                "raison": scoring.get("raison"),
            })

    return resultats


def _envoyer_demande_connexion(profil: dict, message: str) -> bool:
    """
    Interface d'envoi de demande de connexion.
    À connecter à l'API LinkedIn ou un outil tiers (Phantombuster, etc.)
    """
    # TODO: brancher sur l'implémentation réelle
    print(f"[CONNEXION] → {profil.get('nom')} | Message : {message[:50]}...")
    return True
