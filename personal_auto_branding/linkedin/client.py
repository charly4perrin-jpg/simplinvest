"""
Client LinkedIn — interface abstraite vers LinkedIn.
Mode MOCK pour développer sans compte réel.
Mode LIVE à brancher sur Playwright ou Phantombuster.
"""

import os
import json
import time
import random
from datetime import datetime
from config.settings import DATA_DIR

MODE = os.getenv("LINKEDIN_MODE", "mock")  # "mock" ou "live"


class LinkedInClient:
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.mode = MODE
        self._log(f"Client LinkedIn initialisé en mode {self.mode.upper()}")

    # ── PUBLICATIONS ──────────────────────────────────────────────

    def publier_post(self, contenu: str, image_path: str = None) -> dict:
        if self.mode == "mock":
            post_id = f"mock_{int(time.time())}"
            self._log(f"[MOCK] Post publié : {contenu[:60]}...")
            return {
                "succes": True,
                "post_id": post_id,
                "url": f"https://linkedin.com/feed/update/{post_id}",
                "publie_le": datetime.now().isoformat(),
            }
        return self._live_publier_post(contenu, image_path)

    def republier_post(self, post_url: str, commentaire: str = "") -> dict:
        if self.mode == "mock":
            self._log(f"[MOCK] Republication : {post_url[:60]}")
            return {"succes": True, "url": post_url}
        return self._live_republier(post_url, commentaire)

    # ── INTERACTIONS ──────────────────────────────────────────────

    def repondre_commentaire(self, post_id: str, commentaire_id: str, reponse: str) -> bool:
        if self.mode == "mock":
            self._log(f"[MOCK] Réponse commentaire : {reponse[:60]}...")
            return True
        return self._live_repondre_commentaire(post_id, commentaire_id, reponse)

    def envoyer_message(self, profil_id: str, message: str) -> bool:
        if self.mode == "mock":
            self._log(f"[MOCK] DM → {profil_id} : {message[:60]}...")
            return True
        return self._live_envoyer_message(profil_id, message)

    def envoyer_demande_connexion(self, profil_id: str, note: str = "") -> bool:
        if self.mode == "mock":
            self._log(f"[MOCK] Connexion → {profil_id}")
            return True
        return self._live_connexion(profil_id, note)

    # ── LECTURE ───────────────────────────────────────────────────

    def lire_notifications(self) -> list[dict]:
        if self.mode == "mock":
            return self._mock_notifications()
        return self._live_lire_notifications()

    def lire_messages_non_lus(self) -> list[dict]:
        if self.mode == "mock":
            return self._mock_messages()
        return self._live_lire_messages()

    def obtenir_metriques_post(self, post_id: str) -> dict:
        if self.mode == "mock":
            return self._mock_metriques()
        return self._live_metriques(post_id)

    def rechercher_profils(self, criteres: dict) -> list[dict]:
        if self.mode == "mock":
            return self._mock_profils(criteres)
        return self._live_rechercher_profils(criteres)

    # ── MOCK DATA ─────────────────────────────────────────────────

    def _mock_notifications(self) -> list[dict]:
        return [
            {
                "type": "commentaire",
                "auteur": "Jean Martin",
                "auteur_id": "jean_martin_42",
                "post_id": "mock_post_001",
                "contenu": "Super article ! Comment tu gères le posting automatique ?",
                "date": datetime.now().isoformat(),
            },
            {
                "type": "reaction",
                "auteur": "Sophie Bernard",
                "auteur_id": "sophie_bernard",
                "post_id": "mock_post_001",
                "date": datetime.now().isoformat(),
            },
        ]

    def _mock_messages(self) -> list[dict]:
        return [
            {
                "expediteur": "Marc Dupont",
                "expediteur_id": "marc_dupont_sales",
                "contenu": "Bonjour, j'ai vu ton post sur LinkedIn. Tu peux m'en dire plus sur ton service ?",
                "date": datetime.now().isoformat(),
                "profil": {
                    "titre": "Commercial B2B",
                    "entreprise": "TechCorp",
                    "secteur": "SaaS",
                },
            }
        ]

    def _mock_metriques(self) -> dict:
        return {
            "impressions": random.randint(800, 5000),
            "likes": random.randint(10, 150),
            "commentaires": random.randint(2, 30),
            "partages": random.randint(0, 15),
            "taux_engagement": round(random.uniform(1.5, 8.0), 2),
            "nouveaux_abonnes": random.randint(0, 20),
            "date_publication": datetime.now().isoformat(),
        }

    def _mock_profils(self, criteres: dict) -> list[dict]:
        noms = ["Alice Moreau", "Thomas Petit", "Emma Leroy", "Lucas Bernard", "Chloé Simon"]
        titres = ["BDR SaaS", "Account Executive", "SDR B2B", "Sales Manager", "Commercial terrain"]
        return [
            {
                "nom": nom,
                "titre": random.choice(titres),
                "entreprise": f"Entreprise_{i}",
                "secteur": "B2B SaaS",
                "localisation": "Paris",
                "connexions_communes": random.randint(0, 15),
                "actif_recemment": random.choice([True, False]),
                "id": f"profil_{i}",
            }
            for i, nom in enumerate(noms)
        ]

    # ── LIVE (à implémenter) ──────────────────────────────────────

    def _live_publier_post(self, contenu: str, image_path: str = None) -> dict:
        # TODO: implémenter via Playwright ou API LinkedIn officielle
        raise NotImplementedError("Mode LIVE non configuré. Définir LINKEDIN_MODE=live et implémenter.")

    def _live_republier(self, post_url: str, commentaire: str) -> dict:
        raise NotImplementedError

    def _live_repondre_commentaire(self, post_id: str, commentaire_id: str, reponse: str) -> bool:
        raise NotImplementedError

    def _live_envoyer_message(self, profil_id: str, message: str) -> bool:
        raise NotImplementedError

    def _live_connexion(self, profil_id: str, note: str) -> bool:
        raise NotImplementedError

    def _live_lire_notifications(self) -> list[dict]:
        raise NotImplementedError

    def _live_lire_messages(self) -> list[dict]:
        raise NotImplementedError

    def _live_metriques(self, post_id: str) -> dict:
        raise NotImplementedError

    def _live_rechercher_profils(self, criteres: dict) -> list[dict]:
        raise NotImplementedError

    def _log(self, message: str):
        log_path = DATA_DIR / "metrics" / f"{self.client_id}_linkedin.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
