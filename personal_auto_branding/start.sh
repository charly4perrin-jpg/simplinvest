#!/bin/bash
set -e

echo ""
echo "⚡ Personal Auto-Branding — Démarrage"
echo "══════════════════════════════════════"
echo ""

# ── Vérifications ──────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
  echo "❌ Python 3 requis. Installe-le depuis python.org"
  exit 1
fi

if [ ! -f ".env" ]; then
  echo "📋 Création du fichier .env..."
  cp .env.example .env
  echo ""
  echo "⚠️  Ouvre le fichier .env et remplis :"
  echo "   ANTHROPIC_API_KEY=ta_clé  (https://console.anthropic.com)"
  echo ""
  echo "Puis relance : ./start.sh"
  exit 0
fi

# ── Dépendances ────────────────────────────────────────────────
echo "📦 Installation des dépendances..."
pip install -r requirements.txt -q

echo "🌐 Installation de Chromium (automatisation LinkedIn)..."
python -m playwright install chromium --with-deps -q 2>/dev/null || true

# ── Répertoires de données ─────────────────────────────────────
mkdir -p data/{profiles,posts,leads,metrics,sessions}

# ── Choix du mode ─────────────────────────────────────────────
echo ""
echo "Que veux-tu faire ?"
echo "  1) Créer un nouveau client (onboarding CLI)"
echo "  2) Lancer le dashboard web  → http://localhost:5000"
echo "  3) Lancer le daemon 24/7 (pour un client existant)"
echo "  4) Voir les clients existants"
echo ""
read -rp "Choix [1-4] : " choix

case "$choix" in
  1)
    echo ""
    read -rp "ID client (ex: jean_dupont) : " client_id
    export $(grep -v '^#' .env | xargs)
    python main.py onboard "$client_id"
    echo ""
    echo "✅ Client créé. Lance maintenant : ./start.sh (option 2)"
    ;;
  2)
    echo ""
    echo "🚀 Dashboard disponible sur : http://localhost:5000/landing"
    echo "   Login admin : admin / (mot de passe dans .env DASHBOARD_ADMIN_PASSWORD)"
    echo ""
    echo "   Ctrl+C pour arrêter"
    echo ""
    export $(grep -v '^#' .env | xargs)
    python dashboard/app.py
    ;;
  3)
    echo ""
    python main.py onboard 2>/dev/null; clients=$(python -c "from onboarding.persona_builder import lister_clients; print(' '.join(lister_clients()))" 2>/dev/null)
    echo "Clients disponibles : $clients"
    read -rp "ID client : " client_id
    read -rp "Intervalle en minutes [5] : " interval
    interval=${interval:-5}
    echo ""
    echo "🤖 Daemon lancé pour $client_id (toutes les ${interval}min)"
    echo "   Ctrl+C pour arrêter"
    echo ""
    export $(grep -v '^#' .env | xargs)
    python agent/daemon.py "$client_id" --interval "$interval"
    ;;
  4)
    export $(grep -v '^#' .env | xargs)
    python -c "
from onboarding.persona_builder import lister_clients, charger_persona
clients = lister_clients()
if not clients:
    print('Aucun client. Choisis option 1.')
else:
    for c in clients:
        p = charger_persona(c)
        print(f'  → {c} ({p[\"profil\"][\"nom\"]}) — {p[\"profil\"][\"metier\"]}')
"
    ;;
  *)
    echo "Choix invalide."
    exit 1
    ;;
esac
