"""
Auth dashboard — gestion des accès par client.
Chaque client a une clé API unique. Le gestionnaire (toi) a un accès admin.
Stockage dans data/auth.json — générer les clés via : python dashboard/auth.py create <client_id>
"""

import os
import json
import secrets
import hashlib
from pathlib import Path
from functools import wraps
from flask import request, redirect, url_for, session, render_template_string
from config.settings import DATA_DIR

AUTH_FILE = DATA_DIR / "auth.json"
ADMIN_PASSWORD = os.getenv("DASHBOARD_ADMIN_PASSWORD", "changeme")
SECRET_KEY = os.getenv("DASHBOARD_SECRET_KEY", secrets.token_hex(32))

LOGIN_HTML = """
<!DOCTYPE html><html lang="fr">
<head><meta charset="UTF-8"><title>Connexion</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0f0f0f;display:flex;align-items:center;justify-content:center;height:100vh;font-family:system-ui}
.card{background:#1a1a1a;border:1px solid #2e2e2e;border-radius:12px;padding:40px;width:360px}
h1{color:#e8e8e8;font-size:20px;margin-bottom:24px;text-align:center}
input{width:100%;background:#242424;border:1px solid #2e2e2e;border-radius:6px;padding:10px 14px;color:#e8e8e8;font-size:14px;margin-bottom:12px;outline:none}
input:focus{border-color:#4f8ef7}
button{width:100%;background:#4f8ef7;color:#fff;border:none;border-radius:6px;padding:11px;font-size:14px;font-weight:600;cursor:pointer}
.err{color:#ef4444;font-size:12px;margin-bottom:10px;text-align:center}
</style></head>
<body><div class="card">
<h1>⚡ AutoBranding</h1>
{% if error %}<div class="err">{{ error }}</div>{% endif %}
<form method="POST">
<input type="text" name="client_id" placeholder="ID client (ou 'admin')" required>
<input type="password" name="password" placeholder="Mot de passe / Clé API" required>
<button type="submit">Connexion</button>
</form></div></body></html>
"""


def init_app(app):
    """Initialise l'auth sur l'application Flask."""
    app.secret_key = SECRET_KEY
    app.add_url_rule("/login", "login", _login, methods=["GET", "POST"])
    app.add_url_rule("/logout", "logout", _logout)


def login_required(f):
    """Décorateur — protège une route."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("authenticated"):
            return redirect(url_for("login"))
        # Vérifier que le client accède seulement à ses propres données
        client_id_route = kwargs.get("client_id")
        if client_id_route and session.get("role") != "admin":
            if session.get("client_id") != client_id_route:
                return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def creer_cle_client(client_id: str) -> str:
    """Génère et stocke une clé API pour un client."""
    cle = secrets.token_urlsafe(32)
    cle_hashee = _hasher(cle)

    auth = _charger_auth()
    auth["clients"][client_id] = {"cle_hash": cle_hashee}
    _sauvegarder_auth(auth)

    return cle  # À donner au client — non stocké en clair


def lister_clients_auth() -> list[str]:
    return list(_charger_auth().get("clients", {}).keys())


# ── ROUTES ────────────────────────────────────────────────────────

def _login():
    error = None
    if request.method == "POST":
        client_id = request.form.get("client_id", "").strip()
        password = request.form.get("password", "").strip()

        if client_id == "admin" and password == ADMIN_PASSWORD:
            session["authenticated"] = True
            session["role"] = "admin"
            session["client_id"] = "admin"
            return redirect(url_for("index"))

        auth = _charger_auth()
        client_data = auth.get("clients", {}).get(client_id)
        if client_data and client_data["cle_hash"] == _hasher(password):
            session["authenticated"] = True
            session["role"] = "client"
            session["client_id"] = client_id
            return redirect(url_for("dashboard", client_id=client_id))

        error = "Identifiants incorrects"

    return render_template_string(LOGIN_HTML, error=error)


def _logout():
    session.clear()
    return redirect(url_for("login"))


# ── UTILITAIRES ───────────────────────────────────────────────────

def _hasher(valeur: str) -> str:
    return hashlib.sha256(valeur.encode()).hexdigest()


def _charger_auth() -> dict:
    AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not AUTH_FILE.exists():
        return {"clients": {}}
    with open(AUTH_FILE, encoding="utf-8") as f:
        return json.load(f)


def _sauvegarder_auth(auth: dict):
    with open(AUTH_FILE, "w", encoding="utf-8") as f:
        json.dump(auth, f, ensure_ascii=False, indent=2)


# ── CLI ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage : python dashboard/auth.py create <client_id>")
        sys.exit(1)
    if sys.argv[1] == "create":
        cid = sys.argv[2]
        cle = creer_cle_client(cid)
        print(f"Clé API créée pour '{cid}' :")
        print(f"  {cle}")
        print("Donne cette clé au client — elle ne sera plus affichée.")
