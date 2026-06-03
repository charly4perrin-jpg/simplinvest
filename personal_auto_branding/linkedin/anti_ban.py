"""
Couche anti-bannissement — simule un comportement humain pour éviter la détection.
Toutes les actions LinkedIn passent par cette couche avant d'être exécutées.
"""

import time
import random
from datetime import datetime, date
from pathlib import Path
import json
from config.settings import DATA_DIR, LINKEDIN_LIMITS


def peut_effectuer_action(client_id: str, type_action: str) -> dict:
    """Vérifie si une action peut être effectuée sans dépasser les limites du jour."""
    compteurs = _charger_compteurs(client_id)
    limite = LINKEDIN_LIMITS.get(f"{type_action}s_per_day", 10)
    compteur_actuel = compteurs.get(type_action, 0)

    if compteur_actuel >= limite:
        return {
            "autorise": False,
            "raison": f"Limite journalière atteinte : {compteur_actuel}/{limite} {type_action}s",
            "reprendre_demain": True,
        }

    return {"autorise": True, "compteur": compteur_actuel, "limite": limite}


def enregistrer_action(client_id: str, type_action: str):
    """Incrémente le compteur après une action effectuée."""
    compteurs = _charger_compteurs(client_id)
    compteurs[type_action] = compteurs.get(type_action, 0) + 1
    _sauvegarder_compteurs(client_id, compteurs)


def attendre_delai_humain(type_action: str = "default"):
    """Attend un délai aléatoire qui imite un comportement humain."""
    delais = {
        "connection": (30, 120),
        "message": (60, 200),
        "commentaire": (20, 90),
        "post": (300, 900),
        "default": (
            LINKEDIN_LIMITS["min_delay_seconds"],
            LINKEDIN_LIMITS["max_delay_seconds"],
        ),
    }
    min_s, max_s = delais.get(type_action, delais["default"])
    delai = random.uniform(min_s, max_s)

    # Micro-variation pour éviter les patterns détectables
    delai += random.gauss(0, 5)
    delai = max(10, delai)

    time.sleep(delai)
    return delai


def heure_optimale_pour_poster(client_id: str = None) -> bool:
    """Retourne True si l'heure actuelle est propice à la publication."""
    from config.settings import OPTIMAL_HOURS, OPTIMAL_DAYS
    maintenant = datetime.now()
    return (
        maintenant.weekday() in OPTIMAL_DAYS
        and maintenant.hour in OPTIMAL_HOURS
    )


def rapport_activite_jour(client_id: str) -> dict:
    """Résumé de l'activité du jour pour un client."""
    compteurs = _charger_compteurs(client_id)
    rapport = {}
    for action, limite_key in [
        ("connection", "connections_per_day"),
        ("message", "messages_per_day"),
        ("commentaire", "comments_per_day"),
        ("post", "posts_per_day"),
    ]:
        effectue = compteurs.get(action, 0)
        limite = LINKEDIN_LIMITS[limite_key]
        rapport[action] = {
            "effectue": effectue,
            "limite": limite,
            "restant": max(0, limite - effectue),
        }
    return rapport


def _charger_compteurs(client_id: str) -> dict:
    chemin = _chemin_compteurs(client_id)
    if not chemin.exists():
        return {}
    with open(chemin, encoding="utf-8") as f:
        data = json.load(f)
    # Reset si c'est un nouveau jour
    if data.get("date") != str(date.today()):
        return {}
    return data.get("compteurs", {})


def _sauvegarder_compteurs(client_id: str, compteurs: dict):
    chemin = _chemin_compteurs(client_id)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump({"date": str(date.today()), "compteurs": compteurs}, f)


def _chemin_compteurs(client_id: str) -> Path:
    return DATA_DIR / "metrics" / f"{client_id}_compteurs.json"
