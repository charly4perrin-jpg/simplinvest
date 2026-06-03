"""
Dashboard web — interface de gestion pour les clients.
Validation de posts, suivi des leads, métriques, incidents.

Usage : python dashboard/app.py
        Ouvrir http://localhost:5000
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, jsonify, session

sys.path.insert(0, str(Path(__file__).parent.parent))

from onboarding.persona_builder import lister_clients, charger_persona
from core.content_generator import charger_posts_client, valider_post
from core.feedback_loop import charger_apprentissage
from linkedin.scheduler import planifier_post, generer_planning_semaine
from linkedin.anti_ban import rapport_activite_jour
from memory.lead_tracker import charger_leads_chauds
from config.settings import DATA_DIR
from dashboard.auth import init_app, login_required, creer_cle_client

app = Flask(__name__, template_folder="templates", static_folder="static")
init_app(app)


# ── ROUTES PRINCIPALES ────────────────────────────────────────────

@app.route("/")
@login_required
def index():
    clients = lister_clients() if session.get("role") == "admin" else [session.get("client_id")]
    return render_template("index.html", clients=clients)


@app.route("/client/<client_id>")
@login_required
def dashboard(client_id: str):
    persona = charger_persona(client_id)
    posts_generes = charger_posts_client(client_id, statut="genere")
    posts_valides = charger_posts_client(client_id, statut="valide")
    posts_publies = charger_posts_client(client_id, statut="publie")
    leads = charger_leads_chauds(client_id)
    activite = rapport_activite_jour(client_id)
    apprentissage = charger_apprentissage(client_id)
    incidents = _charger_incidents(client_id)

    return render_template(
        "dashboard.html",
        client_id=client_id,
        persona=persona,
        posts_generes=posts_generes,
        posts_valides=posts_valides,
        posts_publies=posts_publies,
        leads=leads,
        activite=activite,
        apprentissage=apprentissage,
        incidents=[i for i in incidents if not i.get("resolu")],
        now=datetime.now(),
    )


@app.route("/client/<client_id>/posts")
@login_required
def posts(client_id: str):
    persona = charger_persona(client_id)
    statut = request.args.get("statut", "genere")
    posts = charger_posts_client(client_id, statut=statut if statut != "tous" else None)
    return render_template(
        "posts.html",
        client_id=client_id,
        persona=persona,
        posts=posts,
        statut_actif=statut,
    )


@app.route("/client/<client_id>/leads")
@login_required
def leads(client_id: str):
    persona = charger_persona(client_id)
    leads = charger_leads_chauds(client_id)
    return render_template(
        "leads.html",
        client_id=client_id,
        persona=persona,
        leads=leads,
    )


# ── ACTIONS API ───────────────────────────────────────────────────

@app.route("/api/post/<client_id>/<post_id>/valider", methods=["POST"])
def api_valider_post(client_id: str, post_id: str):
    succes = valider_post(post_id, client_id)
    if succes:
        planifier_post(client_id, post_id)
    return jsonify({"succes": succes})


@app.route("/api/post/<client_id>/<post_id>/rejeter", methods=["POST"])
def api_rejeter_post(client_id: str, post_id: str):
    succes = _changer_statut_post(client_id, post_id, "rejete")
    return jsonify({"succes": succes})


@app.route("/api/incident/<client_id>/<int:idx>/resoudre", methods=["POST"])
def api_resoudre_incident(client_id: str, idx: int):
    incidents = _charger_incidents(client_id)
    if idx < len(incidents):
        incidents[idx]["resolu"] = True
        incidents[idx]["resolu_le"] = datetime.now().isoformat()
        _sauvegarder_incidents(client_id, incidents)
    return jsonify({"succes": True})


@app.route("/api/client/<client_id>/stats")
def api_stats(client_id: str):
    posts_generes = charger_posts_client(client_id, statut="genere")
    posts_valides = charger_posts_client(client_id, statut="valide")
    posts_publies = charger_posts_client(client_id, statut="publie")
    leads = charger_leads_chauds(client_id)
    activite = rapport_activite_jour(client_id)

    return jsonify({
        "posts": {
            "generes": len(posts_generes),
            "valides": len(posts_valides),
            "publies": len(posts_publies),
        },
        "leads_chauds": len(leads),
        "activite": activite,
    })


# ── UTILITAIRES ───────────────────────────────────────────────────

def _charger_incidents(client_id: str) -> list:
    chemin = DATA_DIR / "leads" / client_id / "incidents.json"
    if not chemin.exists():
        return []
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


def _sauvegarder_incidents(client_id: str, incidents: list):
    chemin = DATA_DIR / "leads" / client_id / "incidents.json"
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(incidents, f, ensure_ascii=False, indent=2)


def _changer_statut_post(client_id: str, post_id: str, nouveau_statut: str) -> bool:
    chemin = DATA_DIR / "posts" / client_id / f"{post_id}.json"
    if not chemin.exists():
        return False
    with open(chemin, encoding="utf-8") as f:
        post = json.load(f)
    post["statut"] = nouveau_statut
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(post, f, ensure_ascii=False, indent=2)
    return True


if __name__ == "__main__":
    app.run(debug=True, port=5000)
