"""
Mémoire conversationnelle — conserve l'historique de chaque échange par contact.
Permet des réponses cohérentes sur la durée, même des semaines plus tard.
"""

import json
from datetime import datetime
from pathlib import Path
from config.settings import DATA_DIR


def sauvegarder_echange(
    client_id: str,
    contact: str,
    type_echange: str,
    message_recu: str,
    reponse_envoyee: str,
):
    """Sauvegarde un échange avec un contact."""
    chemin = _chemin_contact(client_id, contact)
    historique = _charger_json(chemin)

    historique.append({
        "date": datetime.now().isoformat(),
        "type": type_echange,  # "commentaire" ou "dm"
        "role": "contact",
        "contenu": message_recu,
    })
    historique.append({
        "date": datetime.now().isoformat(),
        "type": type_echange,
        "role": "client",
        "contenu": reponse_envoyee,
    })

    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(historique, f, ensure_ascii=False, indent=2)


def charger_historique(client_id: str, contact: str) -> list[dict]:
    chemin = _chemin_contact(client_id, contact)
    return _charger_json(chemin)


def lister_contacts_actifs(client_id: str) -> list[dict]:
    """Liste les contacts avec qui le client a le plus interagi."""
    dossier = DATA_DIR / "leads" / client_id / "conversations"
    if not dossier.exists():
        return []

    contacts = []
    for fichier in dossier.glob("*.json"):
        historique = _charger_json(fichier)
        if historique:
            contacts.append({
                "contact": fichier.stem,
                "nb_echanges": len(historique),
                "dernier_echange": historique[-1]["date"],
                "type_dernier": historique[-1]["type"],
            })

    return sorted(contacts, key=lambda x: x["dernier_echange"], reverse=True)


def _chemin_contact(client_id: str, contact: str) -> Path:
    contact_safe = contact.replace(" ", "_").replace("/", "_").lower()
    dossier = DATA_DIR / "leads" / client_id / "conversations"
    dossier.mkdir(parents=True, exist_ok=True)
    return dossier / f"{contact_safe}.json"


def _charger_json(chemin: Path) -> list:
    if not chemin.exists():
        return []
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)
