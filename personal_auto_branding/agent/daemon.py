"""
Daemon — boucle principale qui orchestre tout le système 24h/24.
Vérifie toutes les N minutes : posts à publier, interactions à traiter, leads à scorer.

Usage :
  python agent/daemon.py <client_id>
  python agent/daemon.py <client_id> --interval 10   (toutes les 10 minutes)
"""

import sys
import time
import signal
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from onboarding.persona_builder import charger_persona
from core.content_generator import generer_serie_semaine, charger_posts_client, valider_post
from core.response_engine import repondre_commentaire, repondre_dm
from core.trend_radar import generer_idees_posts
from core.feedback_loop import enregistrer_metriques
from linkedin.client import LinkedInClient
from linkedin.scheduler import obtenir_posts_a_publier, marquer_publie, generer_planning_semaine
from linkedin.anti_ban import peut_effectuer_action, attendre_delai_humain, heure_optimale_pour_poster
from linkedin.connection_filter import filtrer_et_connecter
from memory.lead_tracker import scorer_contact
from memory.conversation_memory import charger_historique
from safety.crisis_manager import creer_rapport_crise
from config.settings import DATA_DIR

RUNNING = True


def signal_handler(sig, frame):
    global RUNNING
    print("\n[DAEMON] Arrêt propre en cours...")
    RUNNING = False


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


class Daemon:
    def __init__(self, client_id: str, interval_minutes: int = 5):
        self.client_id = client_id
        self.interval = interval_minutes * 60
        self.persona = charger_persona(client_id)
        self.linkedin = LinkedInClient(client_id)
        self.cycle = 0
        self._log(f"Daemon démarré pour {self.persona['profil']['nom']}")

    def run(self):
        self._log("═" * 50)
        self._log(f"DÉMARRAGE — intervalle : {self.interval // 60} min")
        self._log("═" * 50)

        while RUNNING:
            self.cycle += 1
            self._log(f"\n── Cycle #{self.cycle} — {datetime.now().strftime('%H:%M:%S')} ──")

            try:
                self._etape_publier()
                self._etape_interactions()
                self._etape_connexions()
                self._etape_metriques()
                self._etape_contenu_si_necessaire()
            except Exception as e:
                self._log(f"[ERREUR] Cycle #{self.cycle} : {e}")

            if RUNNING:
                self._log(f"Prochain cycle dans {self.interval // 60} min...")
                time.sleep(self.interval)

        self._log("Daemon arrêté proprement.")

    # ── ÉTAPES ────────────────────────────────────────────────────

    def _etape_publier(self):
        """Publie les posts dont l'heure est venue."""
        if not heure_optimale_pour_poster():
            return

        posts_a_publier = obtenir_posts_a_publier(self.client_id)
        if not posts_a_publier:
            return

        self._log(f"{len(posts_a_publier)} post(s) à publier")

        for entree in posts_a_publier[:1]:  # 1 post max par cycle
            post = self._charger_post(entree["post_id"])
            if not post:
                continue

            resultat = self.linkedin.publier_post(post["contenu"])
            if resultat["succes"]:
                marquer_publie(self.client_id, entree["post_id"])
                self._log(f"Post publié : {post['sujet'][:50]}")
                attendre_delai_humain("post")

    def _etape_interactions(self):
        """Traite les commentaires et DMs entrants."""
        notifications = self.linkedin.lire_notifications()
        messages = self.linkedin.lire_messages_non_lus()

        for notif in notifications:
            if notif["type"] != "commentaire":
                continue

            post = self._charger_post(notif.get("post_id", ""))
            post_contenu = post["contenu"] if post else ""
            historique = charger_historique(self.client_id, notif["auteur_id"])

            resultat = repondre_commentaire(
                persona=self.persona,
                post_contenu=post_contenu,
                commentaire=notif["contenu"],
                auteur=notif["auteur"],
                historique_auteur=historique,
            )

            if resultat["action"] == "escalade_humain":
                creer_rapport_crise(self.client_id, {
                    "type": "commentaire_sensible",
                    "auteur": notif["auteur"],
                    "contenu": notif["contenu"],
                    "raison": resultat["raison"],
                })
                self._log(f"[CRISE] Escalade humain — {notif['auteur']}")
            else:
                self.linkedin.repondre_commentaire(
                    notif["post_id"], notif.get("id", ""), resultat["contenu"]
                )
                scorer_contact(self.client_id, notif["auteur_id"], ["commentaire_post"])
                self._log(f"Commentaire traité — {notif['auteur']}")
                attendre_delai_humain("commentaire")

        for msg in messages:
            historique = charger_historique(self.client_id, msg["expediteur_id"])
            resultat = repondre_dm(
                persona=self.persona,
                message_recu=msg["contenu"],
                expediteur=msg["expediteur"],
                profil_expediteur=msg.get("profil"),
            )

            if resultat["action"] == "escalade_humain":
                creer_rapport_crise(self.client_id, {
                    "type": "dm_sensible",
                    "expediteur": msg["expediteur"],
                    "contenu": msg["contenu"],
                    "raison": resultat["raison"],
                })
                self._log(f"[CRISE] DM escaladé — {msg['expediteur']}")
            else:
                self.linkedin.envoyer_message(msg["expediteur_id"], resultat["contenu"])
                actions = ["dm_entrant"]
                if resultat.get("intention") == "interet_service":
                    actions.append("question_sur_offre")
                scorer_contact(self.client_id, msg["expediteur_id"], actions)
                self._log(f"DM traité — {msg['expediteur']} (intention: {resultat.get('intention')})")
                attendre_delai_humain("message")

    def _etape_connexions(self):
        """Envoie des demandes de connexion ciblées."""
        verification = peut_effectuer_action(self.client_id, "connection")
        if not verification["autorise"]:
            return

        criteres = {
            "secteur": self.persona["strategie"]["client_ideal"],
            "localisation": self.persona["profil"]["ville"],
            "actif": True,
        }
        profils = self.linkedin.rechercher_profils(criteres)

        if not profils:
            return

        resultats = filtrer_et_connecter(self.client_id, self.persona, profils)
        if resultats["connectes"]:
            self._log(f"{len(resultats['connectes'])} connexion(s) envoyée(s)")

    def _etape_metriques(self):
        """Récupère les métriques des posts récemment publiés."""
        posts_publies = charger_posts_client(self.client_id, statut="publie")
        # Ne récupérer les métriques que pour les posts sans données
        sans_metriques = [p for p in posts_publies if not p.get("metriques")][:3]

        for post in sans_metriques:
            metriques = self.linkedin.obtenir_metriques_post(post["id"])
            enregistrer_metriques(self.client_id, post["id"], metriques)
            self._log(f"Métriques mises à jour — {post['sujet'][:40]}")

    def _etape_contenu_si_necessaire(self):
        """Génère du contenu si la file de posts est vide."""
        posts_en_attente = charger_posts_client(self.client_id, statut="genere")
        posts_valides = charger_posts_client(self.client_id, statut="valide")

        if len(posts_en_attente) + len(posts_valides) >= 5:
            return

        self._log("File de contenu faible — génération automatique...")
        idees = generer_idees_posts(self.persona, nb_idees=5)
        sujets = [i["sujet"] for i in idees]
        posts = generer_serie_semaine(self.persona, sujets)

        # Auto-valider si le mode validation humaine est désactivé
        for post in posts:
            valider_post(post["id"], self.client_id)

        post_ids = [p["id"] for p in posts]
        generer_planning_semaine(self.client_id, post_ids)
        self._log(f"{len(posts)} nouveaux posts générés et planifiés")

    # ── UTILITAIRES ───────────────────────────────────────────────

    def _charger_post(self, post_id: str) -> dict | None:
        import glob
        pattern = str(DATA_DIR / "posts" / self.client_id / f"{post_id}.json")
        import os
        if os.path.exists(pattern):
            with open(pattern, encoding="utf-8") as f:
                return json.load(f)
        return None

    def _log(self, message: str):
        horodatage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ligne = f"[{horodatage}] {message}"
        print(ligne)

        log_path = DATA_DIR / "metrics" / f"{self.client_id}_daemon.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(ligne + "\n")


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage : python agent/daemon.py <client_id> [--interval <minutes>]")
        sys.exit(1)

    client_id = args[0]
    interval = 5
    if "--interval" in args:
        idx = args.index("--interval")
        interval = int(args[idx + 1])

    daemon = Daemon(client_id, interval)
    daemon.run()


if __name__ == "__main__":
    main()
