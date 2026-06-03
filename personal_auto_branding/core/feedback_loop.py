"""
Feedback Loop — apprend des performances passées pour améliorer le contenu futur.
Plus le système publie, plus il devient précis sur ce qui fonctionne pour ce client.
"""

import json
from pathlib import Path
from datetime import datetime
import anthropic
from config.settings import MODEL_MAIN, DATA_DIR


def enregistrer_metriques(client_id: str, post_id: str, metriques: dict):
    """Enregistre les métriques d'un post après publication."""
    dossier = DATA_DIR / "posts" / client_id
    chemin = dossier / f"{post_id}.json"

    if not chemin.exists():
        return False

    with open(chemin, encoding="utf-8") as f:
        post = json.load(f)

    post["metriques"] = metriques
    post["statut"] = "publie"
    post["publie_le"] = metriques.get("date_publication", datetime.now().isoformat())

    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(post, f, ensure_ascii=False, indent=2)

    _mettre_a_jour_apprentissage(client_id)
    return True


def _mettre_a_jour_apprentissage(client_id: str):
    """Recalcule les patterns gagnants à partir de tous les posts publiés."""
    posts_publies = _charger_posts_publies(client_id)
    if len(posts_publies) < 3:
        return  # pas assez de données

    analyse = _analyser_patterns(posts_publies)

    chemin = DATA_DIR / "metrics" / f"{client_id}_apprentissage.json"
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump({
            "client_id": client_id,
            "mis_a_jour_le": datetime.now().isoformat(),
            "nb_posts_analyses": len(posts_publies),
            "patterns": analyse,
        }, f, ensure_ascii=False, indent=2)


def _analyser_patterns(posts: list[dict]) -> dict:
    """Identifie les patterns gagnants via Claude."""
    client = anthropic.Anthropic()

    resume_posts = []
    for p in posts[-20:]:  # derniers 20 posts max
        m = p.get("metriques", {})
        resume_posts.append({
            "format": p.get("format"),
            "sujet": p.get("sujet"),
            "longueur": p.get("longueur"),
            "impressions": m.get("impressions", 0),
            "likes": m.get("likes", 0),
            "commentaires": m.get("commentaires", 0),
            "partages": m.get("partages", 0),
            "taux_engagement": m.get("taux_engagement", 0),
        })

    prompt = f"""Analyse ces performances de posts LinkedIn et identifie les patterns gagnants :

{json.dumps(resume_posts, ensure_ascii=False, indent=2)}

Réponds en JSON :
{{
  "meilleur_format": "...",
  "pire_format": "...",
  "longueur_optimale": "...",
  "sujets_qui_marchent": ["..."],
  "sujets_qui_ratent": ["..."],
  "recommandation_principale": "...",
  "score_moyen_engagement": 0.0
}}"""

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
        return {}


def charger_apprentissage(client_id: str) -> dict:
    """Charge les patterns appris pour un client."""
    chemin = DATA_DIR / "metrics" / f"{client_id}_apprentissage.json"
    if not chemin.exists():
        return {}
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


def _charger_posts_publies(client_id: str) -> list[dict]:
    dossier = DATA_DIR / "posts" / client_id
    if not dossier.exists():
        return []
    posts = []
    for fichier in dossier.glob("*.json"):
        with open(fichier, encoding="utf-8") as f:
            p = json.load(f)
        if p.get("statut") == "publie" and p.get("metriques"):
            posts.append(p)
    return sorted(posts, key=lambda x: x.get("publie_le", ""))
