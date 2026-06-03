"""
Gestionnaire de crise — intercepte les interactions sensibles avant toute réponse automatique.
Un seul dérapage peut détruire un profil. Ce module ne rate rien.
"""

import json
import anthropic
from config.settings import MODEL_FAST, CRISIS_KEYWORDS


def analyser_risque(contenu: str) -> dict:
    """
    Analyse un commentaire ou DM et détecte si une intervention humaine est nécessaire.
    Retourne immédiatement sur les mots-clés évidents, sinon délègue à Claude.
    """
    contenu_lower = contenu.lower()

    # Détection rapide sur mots-clés
    mots_detectes = [mot for mot in CRISIS_KEYWORDS if mot in contenu_lower]
    if mots_detectes:
        return {
            "flag": True,
            "niveau": "critique",
            "raison": f"Mots-clés sensibles détectés : {', '.join(mots_detectes)}",
            "action_recommandee": "escalade_humain_immediat",
        }

    # Analyse sémantique via Claude pour les cas ambigus
    return _analyser_semantique(contenu)


def _analyser_semantique(contenu: str) -> dict:
    """Analyse sémantique pour détecter les risques non évidents."""
    client = anthropic.Anthropic()

    prompt = f"""Analyse ce message reçu sur LinkedIn et évalue le risque :

Message : "{contenu}"

Réponds en JSON :
{{
  "flag": true/false,
  "niveau": "faible|moyen|critique",
  "raison": "...",
  "action_recommandee": "repondre_auto|escalade_humain|ignorer"
}}

Flag = true si le message contient :
- Une accusation (arnaque, mensonge, fraude, comportement non éthique)
- Une demande juridique ou menace légale
- Un contenu offensant ou discriminatoire
- Une critique publique qui pourrait devenir virale négativement
- Une question sur des données personnelles ou des pratiques internes
- Toute ambiguïté importante sur l'automatisation du compte"""

    message = client.messages.create(
        model=MODEL_FAST,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )

    texte = message.content[0].text
    debut = texte.find("{")
    fin = texte.rfind("}") + 1
    try:
        return json.loads(texte[debut:fin])
    except Exception:
        # En cas de doute, on flag par sécurité
        return {
            "flag": True,
            "niveau": "moyen",
            "raison": "Impossible d'analyser — escalade par précaution",
            "action_recommandee": "escalade_humain",
        }


def creer_rapport_crise(client_id: str, incident: dict):
    """Enregistre un incident pour revue humaine."""
    import json
    from datetime import datetime
    from pathlib import Path
    from config.settings import DATA_DIR

    dossier = DATA_DIR / "leads" / client_id
    dossier.mkdir(parents=True, exist_ok=True)
    incidents_path = dossier / "incidents.json"

    incidents = []
    if incidents_path.exists():
        with open(incidents_path, encoding="utf-8") as f:
            incidents = json.load(f)

    incidents.append({
        **incident,
        "date": datetime.now().isoformat(),
        "resolu": False,
    })

    with open(incidents_path, "w", encoding="utf-8") as f:
        json.dump(incidents, f, ensure_ascii=False, indent=2)
