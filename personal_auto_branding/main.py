"""
Personal Auto-Branding — Orchestrateur principal
Gère un profil LinkedIn de A à Z via IA, 24h/24.

Usage :
  python main.py onboard <client_id>       → Créer un nouveau client
  python main.py generate <client_id>      → Générer des posts
  python main.py schedule <client_id>      → Planifier la semaine
  python main.py dashboard <client_id>     → Voir le tableau de bord
  python main.py leads <client_id>         → Voir les leads chauds
"""

import sys
import json
from datetime import datetime

from onboarding.persona_builder import creer_persona, charger_persona, lister_clients
from core.content_generator import generer_post, generer_serie_semaine, charger_posts_client
from core.trend_radar import generer_idees_posts
from core.feedback_loop import charger_apprentissage
from linkedin.scheduler import planifier_post, generer_planning_semaine, obtenir_posts_a_publier
from linkedin.anti_ban import rapport_activite_jour
from memory.lead_tracker import charger_leads_chauds


def cmd_onboard(client_id: str):
    persona = creer_persona(client_id)
    print(f"\nOnboarding terminé pour {persona['profil']['nom']}")
    print(f"Empreinte vocale : {persona['voix']['empreinte'][:200]}...")


def cmd_generate(client_id: str):
    persona = charger_persona(client_id)
    apprentissage = charger_apprentissage(client_id)

    print(f"\nGénération de contenu pour {persona['profil']['nom']}")
    print("Analyse des tendances...")

    idees = generer_idees_posts(persona, nb_idees=5)

    if apprentissage.get("patterns"):
        p = apprentissage["patterns"]
        print(f"Insight appris : meilleur format = {p.get('meilleur_format')}")
        print(f"Recommandation : {p.get('recommandation_principale')}\n")

    print(f"{len(idees)} idées générées :\n")
    for i, idee in enumerate(idees, 1):
        urgence_icon = "🔥" if idee.get("urgence") == "haute" else "→"
        print(f"{urgence_icon} {i}. [{idee['format']}] {idee['sujet']}")

    print()
    choix = input("Générer tous ces posts ? (o/n) [o] : ").strip().lower()
    if choix != "n":
        sujets = [idee["sujet"] for idee in idees]
        posts = generer_serie_semaine(persona, sujets)
        print(f"\n{len(posts)} posts générés et sauvegardés.")
        _afficher_posts(posts)


def cmd_schedule(client_id: str):
    posts = charger_posts_client(client_id, statut="valide")
    if not posts:
        posts = charger_posts_client(client_id, statut="genere")

    if not posts:
        print("Aucun post à planifier. Lance d'abord : python main.py generate")
        return

    post_ids = [p["id"] for p in posts[:5]]
    planning = generer_planning_semaine(client_id, post_ids)

    print(f"\nPlanning semaine — {len(planning)} posts planifiés :\n")
    for entree in planning:
        post = next((p for p in posts if p["id"] == entree["post_id"]), None)
        if post:
            date = datetime.fromisoformat(entree["planifie_pour"])
            print(f"  {date.strftime('%A %d/%m à %Hh')} — [{post['format']}] {post['sujet']}")


def cmd_dashboard(client_id: str):
    persona = charger_persona(client_id)
    activite = rapport_activite_jour(client_id)
    posts_generes = charger_posts_client(client_id, statut="genere")
    posts_valides = charger_posts_client(client_id, statut="valide")
    posts_publies = charger_posts_client(client_id, statut="publie")
    leads = charger_leads_chauds(client_id)
    a_publier = obtenir_posts_a_publier(client_id)
    apprentissage = charger_apprentissage(client_id)

    print(f"\n{'='*50}")
    print(f"  DASHBOARD — {persona['profil']['nom']}")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*50}\n")

    print("── POSTS ──")
    print(f"  En attente de validation : {len(posts_generes)}")
    print(f"  Validés (à publier) : {len(posts_valides)}")
    print(f"  Publiés total : {len(posts_publies)}")
    if a_publier:
        print(f"  ⚡ À publier maintenant : {len(a_publier)}")

    print("\n── ACTIVITÉ DU JOUR ──")
    for action, stats in activite.items():
        barre = "█" * stats["effectue"] + "░" * stats["restant"]
        print(f"  {action:15} {barre} {stats['effectue']}/{stats['limite']}")

    print(f"\n── LEADS ──")
    print(f"  Leads chauds : {len(leads)}")
    for lead in leads[:3]:
        print(f"  → {lead['contact']} (score {lead['score']}/100)")

    if apprentissage.get("patterns"):
        p = apprentissage["patterns"]
        print(f"\n── APPRENTISSAGE ──")
        print(f"  Posts analysés : {apprentissage.get('nb_posts_analyses', 0)}")
        print(f"  Meilleur format : {p.get('meilleur_format', '?')}")
        print(f"  Engagement moyen : {p.get('score_moyen_engagement', 0):.1f}%")

    print()


def cmd_leads(client_id: str):
    leads = charger_leads_chauds(client_id)
    if not leads:
        print("Aucun lead chaud pour l'instant.")
        return

    print(f"\n{len(leads)} leads chauds :\n")
    for lead in leads:
        print(f"  {lead['contact']} — score {lead['score']}/100")
        print(f"  Actions : {', '.join(lead['actions'])}")
        print()


def _afficher_posts(posts: list):
    for post in posts:
        score = post["validation"].get("score_global", "?")
        print(f"\n[{post['format'].upper()}] Score : {score}/40")
        print("─" * 40)
        print(post["contenu"][:400] + ("..." if len(post["contenu"]) > 400 else ""))
        print()


def main():
    args = sys.argv[1:]

    if not args:
        print(__doc__)
        return

    commande = args[0]
    client_id = args[1] if len(args) > 1 else None

    if commande == "onboard":
        client_id = client_id or input("ID client (ex: marie_dupont) : ").strip()
        cmd_onboard(client_id)

    elif commande == "generate":
        if not client_id:
            clients = lister_clients()
            if not clients:
                print("Aucun client. Lance d'abord : python main.py onboard")
                return
            print("Clients disponibles :", ", ".join(clients))
            client_id = input("ID client : ").strip()
        cmd_generate(client_id)

    elif commande == "schedule":
        client_id = client_id or input("ID client : ").strip()
        cmd_schedule(client_id)

    elif commande == "dashboard":
        client_id = client_id or input("ID client : ").strip()
        cmd_dashboard(client_id)

    elif commande == "leads":
        client_id = client_id or input("ID client : ").strip()
        cmd_leads(client_id)

    else:
        print(f"Commande inconnue : {commande}")
        print(__doc__)


if __name__ == "__main__":
    main()
