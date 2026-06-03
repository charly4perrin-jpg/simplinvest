"""
Lead Tracker — score et classe les contacts en fonction de leur niveau d'engagement.
Un contact devient "lead chaud" quand son score dépasse le seuil défini.
"""

import json
from datetime import datetime
from pathlib import Path
import anthropic
from config.settings import MODEL_FAST, DATA_DIR, LEAD_SCORE_THRESHOLD


SCORING_REGLES = {
    "dm_entrant": 25,
    "commentaire_post": 10,
    "commentaire_multiple": 20,
    "partage_post": 15,
    "connexion_acceptee": 5,
    "visite_profil_repetee": 10,
    "reaction_post": 3,
    "question_sur_offre": 40,
}


def scorer_contact(client_id: str, contact: str, actions: list[str]) -> dict:
    """Calcule le score d'un contact et détermine s'il est lead qualifié."""
    score = sum(SCORING_REGLES.get(action, 0) for action in actions)
    score = min(score, 100)

    statut = "froid"
    if score >= LEAD_SCORE_THRESHOLD:
        statut = "chaud"
    elif score >= 30:
        statut = "tiede"

    lead = {
        "client_id": client_id,
        "contact": contact,
        "score": score,
        "statut": statut,
        "actions": actions,
        "mis_a_jour_le": datetime.now().isoformat(),
        "converti": False,
    }

    _sauvegarder_lead(lead)

    if statut == "chaud":
        _alerter_lead_chaud(client_id, contact, score)

    return lead


def _alerter_lead_chaud(client_id: str, contact: str, score: int):
    """Crée une alerte quand un lead devient chaud."""
    dossier = DATA_DIR / "leads" / client_id
    dossier.mkdir(parents=True, exist_ok=True)
    alertes_path = dossier / "alertes.json"

    alertes = []
    if alertes_path.exists():
        with open(alertes_path, encoding="utf-8") as f:
            alertes = json.load(f)

    alertes.append({
        "contact": contact,
        "score": score,
        "date": datetime.now().isoformat(),
        "traite": False,
    })

    with open(alertes_path, "w", encoding="utf-8") as f:
        json.dump(alertes, f, ensure_ascii=False, indent=2)

    # Notification email + SMS
    try:
        from notifications.alertes import alerter_lead_chaud
        alerter_lead_chaud(client_id, contact, score)
    except Exception:
        pass


def generer_message_approche(persona: dict, lead: dict, historique: list) -> str:
    """Génère un message d'approche personnalisé pour un lead chaud."""
    client = anthropic.Anthropic()

    contexte_historique = ""
    if historique:
        points_cles = [e["contenu"][:100] for e in historique[-4:] if e["role"] == "contact"]
        contexte_historique = f"\nIl a notamment dit : {' | '.join(points_cles)}"

    prompt = f"""Rédige un message LinkedIn court pour approcher ce lead chaud.

Envoyeur : {persona['profil']['nom']} ({persona['profil']['metier']})
Contact : {lead['contact']}
Score d'engagement : {lead['score']}/100
Actions effectuées : {', '.join(lead['actions'])}
{contexte_historique}

Objectif : proposer naturellement un échange ou un appel découverte.

Règles :
- Maximum 5 lignes
- Pas de pitch agressif
- Référencer un échange récent si possible
- Finir par une question ouverte simple
- Ton naturel, pas corporate"""

    message = client.messages.create(
        model=MODEL_FAST,
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def charger_leads_chauds(client_id: str) -> list[dict]:
    dossier = DATA_DIR / "leads" / client_id
    if not dossier.exists():
        return []
    leads = []
    for fichier in dossier.glob("lead_*.json"):
        with open(fichier, encoding="utf-8") as f:
            lead = json.load(f)
        if lead.get("statut") == "chaud" and not lead.get("converti"):
            leads.append(lead)
    return sorted(leads, key=lambda x: x["score"], reverse=True)


def _sauvegarder_lead(lead: dict):
    contact_safe = lead["contact"].replace(" ", "_").replace("/", "_").lower()
    dossier = DATA_DIR / "leads" / lead["client_id"]
    dossier.mkdir(parents=True, exist_ok=True)
    chemin = dossier / f"lead_{contact_safe}.json"
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(lead, f, ensure_ascii=False, indent=2)
