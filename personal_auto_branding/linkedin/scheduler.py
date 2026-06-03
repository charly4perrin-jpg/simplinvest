"""
Scheduler — planifie et ordonne les publications au meilleur moment.
S'assure qu'aucun post ne sort hors des créneaux optimaux.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from config.settings import DATA_DIR, OPTIMAL_HOURS, OPTIMAL_DAYS
from linkedin.anti_ban import peut_effectuer_action, enregistrer_action


def planifier_post(client_id: str, post_id: str, date_souhaitee: datetime = None) -> dict:
    """Planifie un post pour le prochain créneau optimal."""
    if date_souhaitee is None:
        date_souhaitee = _prochain_creneau_optimal()

    planning = _charger_planning(client_id)
    planning.append({
        "post_id": post_id,
        "planifie_pour": date_souhaitee.isoformat(),
        "statut": "en_attente",
        "cree_le": datetime.now().isoformat(),
    })

    _sauvegarder_planning(client_id, planning)
    return {"post_id": post_id, "planifie_pour": date_souhaitee.isoformat()}


def obtenir_posts_a_publier(client_id: str) -> list[dict]:
    """Retourne les posts dont l'heure de publication est passée et qui sont en attente."""
    planning = _charger_planning(client_id)
    maintenant = datetime.now()

    a_publier = []
    for entree in planning:
        if entree["statut"] != "en_attente":
            continue
        date_pub = datetime.fromisoformat(entree["planifie_pour"])
        if date_pub <= maintenant:
            verification = peut_effectuer_action(client_id, "post")
            if verification["autorise"]:
                a_publier.append(entree)

    return a_publier


def marquer_publie(client_id: str, post_id: str):
    """Marque un post comme publié dans le planning."""
    planning = _charger_planning(client_id)
    for entree in planning:
        if entree["post_id"] == post_id:
            entree["statut"] = "publie"
            entree["publie_le"] = datetime.now().isoformat()
            break
    _sauvegarder_planning(client_id, planning)
    enregistrer_action(client_id, "post")


def generer_planning_semaine(client_id: str, post_ids: list[str]) -> list[dict]:
    """Distribue intelligemment une liste de posts sur la semaine."""
    creneaux = _creneaux_semaine_prochaine()
    planning_genere = []

    for i, post_id in enumerate(post_ids):
        if i >= len(creneaux):
            break
        entree = planifier_post(client_id, post_id, creneaux[i])
        planning_genere.append(entree)

    return planning_genere


def _prochain_creneau_optimal() -> datetime:
    """Calcule le prochain créneau de publication optimal."""
    maintenant = datetime.now()
    candidat = maintenant.replace(minute=0, second=0, microsecond=0)

    for _ in range(14):  # chercher dans les 14 prochains jours
        if candidat.weekday() in OPTIMAL_DAYS:
            for heure in sorted(OPTIMAL_HOURS):
                creneau = candidat.replace(hour=heure)
                if creneau > maintenant:
                    return creneau
        candidat += timedelta(days=1)

    return maintenant + timedelta(hours=2)


def _creneaux_semaine_prochaine() -> list[datetime]:
    """Génère les créneaux disponibles pour la semaine prochaine."""
    creneaux = []
    debut = datetime.now() + timedelta(days=1)
    debut = debut.replace(hour=0, minute=0, second=0, microsecond=0)

    for delta_jour in range(7):
        jour = debut + timedelta(days=delta_jour)
        if jour.weekday() in OPTIMAL_DAYS:
            # 1 post par jour max, à l'heure optimale du matin
            heure_choisie = OPTIMAL_HOURS[0]  # 7h par défaut
            creneaux.append(jour.replace(hour=heure_choisie))

    return creneaux


def _charger_planning(client_id: str) -> list:
    chemin = DATA_DIR / "metrics" / f"{client_id}_planning.json"
    if not chemin.exists():
        return []
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


def _sauvegarder_planning(client_id: str, planning: list):
    chemin = DATA_DIR / "metrics" / f"{client_id}_planning.json"
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(planning, f, ensure_ascii=False, indent=2)
