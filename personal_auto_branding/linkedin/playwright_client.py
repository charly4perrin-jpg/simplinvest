"""
Client LinkedIn LIVE — automatisation via Playwright.
Simule un comportement humain pour éviter la détection.

Prérequis :
  pip install playwright playwright-stealth
  playwright install chromium

Variables d'environnement :
  LINKEDIN_EMAIL, LINKEDIN_PASSWORD
"""

import os
import json
import time
import random
from datetime import datetime
from pathlib import Path
from config.settings import DATA_DIR
from linkedin.anti_ban import attendre_delai_humain


class PlaywrightLinkedIn:
    """
    Automatisation LinkedIn via Playwright avec techniques anti-détection.
    Utilisé par linkedin/client.py quand LINKEDIN_MODE=live.
    """

    SESSION_DIR = DATA_DIR / "sessions"

    def __init__(self, client_id: str):
        self.client_id = client_id
        self.browser = None
        self.context = None
        self.page = None
        self._session_path = self.SESSION_DIR / f"{client_id}_session.json"
        self.SESSION_DIR.mkdir(parents=True, exist_ok=True)

    def demarrer(self):
        """Lance le navigateur et restaure la session si disponible."""
        try:
            from playwright.sync_api import sync_playwright
            from playwright_stealth import stealth_sync
        except ImportError:
            raise RuntimeError(
                "Playwright non installé. Lance : pip install playwright playwright-stealth && playwright install chromium"
            )

        self._pw = sync_playwright().start()
        self.browser = self._pw.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--window-size=1366,768",
            ],
        )

        # Contexte avec viewport humain + locale FR
        context_options = {
            "viewport": {"width": 1366, "height": 768},
            "locale": "fr-FR",
            "timezone_id": "Europe/Paris",
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        }

        # Restaurer la session existante
        if self._session_path.exists():
            context_options["storage_state"] = str(self._session_path)

        self.context = self.browser.new_context(**context_options)
        self.page = self.context.new_page()

        stealth_sync(self.page)

        # Vérifier si la session est toujours valide
        if not self._session_valide():
            self._connecter()

    def arreter(self):
        if self.context:
            self.context.storage_state(path=str(self._session_path))
        if self.browser:
            self.browser.close()
        if hasattr(self, "_pw"):
            self._pw.stop()

    # ── PUBLICATIONS ──────────────────────────────────────────────

    def publier_post(self, contenu: str, image_path: str = None) -> dict:
        """Publie un post texte (ou avec image) sur LinkedIn."""
        self.page.goto("https://www.linkedin.com/feed/")
        self._attendre_chargement()

        # Cliquer sur "Commencer un post"
        bouton_post = self.page.locator("button[aria-label*='Commencer un post'], button[aria-label*='Start a post']")
        bouton_post.first.click()
        self._pause_humaine()

        # Zone de texte
        zone_texte = self.page.locator(".ql-editor, [data-placeholder*='post']").first
        zone_texte.click()
        self._taper_comme_humain(zone_texte, contenu)
        self._pause_humaine()

        if image_path and Path(image_path).exists():
            self._joindre_image(image_path)

        # Publier
        bouton_publier = self.page.locator("button[aria-label*='Publier'], button[aria-label*='Post']").last
        bouton_publier.click()
        self._attendre_chargement(3000)

        post_id = f"li_{int(time.time())}"
        self._log(f"Post publié : {contenu[:60]}...")
        return {
            "succes": True,
            "post_id": post_id,
            "url": f"https://www.linkedin.com/feed/",
            "publie_le": datetime.now().isoformat(),
        }

    def republier_post(self, post_url: str, commentaire: str = "") -> dict:
        """Republie (reshare) un post externe."""
        self.page.goto(post_url)
        self._attendre_chargement()

        bouton_reposter = self.page.locator("button[aria-label*='Republier'], button[aria-label*='Repost']").first
        bouton_reposter.click()
        self._pause_humaine()

        if commentaire:
            # Choisir "Republier avec vos commentaires"
            option_avec = self.page.locator("text=avec vos commentaires, text=with your thoughts").first
            option_avec.click()
            self._pause_humaine()
            zone = self.page.locator(".ql-editor").first
            self._taper_comme_humain(zone, commentaire)
            self._pause_humaine()

        bouton_valider = self.page.locator("button[aria-label*='Publier'], button[aria-label*='Post']").last
        bouton_valider.click()
        self._attendre_chargement(2000)
        self._log(f"Republication effectuée : {post_url[:60]}")
        return {"succes": True, "url": post_url}

    # ── INTERACTIONS ──────────────────────────────────────────────

    def repondre_commentaire(self, post_url: str, auteur: str, reponse: str) -> bool:
        """Répond à un commentaire sur un post LinkedIn."""
        self.page.goto(post_url)
        self._attendre_chargement(2000)

        # Trouver le commentaire de cet auteur et cliquer sur Répondre
        commentaires = self.page.locator(".comments-comment-item")
        for i in range(commentaires.count()):
            commentaire = commentaires.nth(i)
            if auteur.lower() in (commentaire.text_content() or "").lower():
                bouton_repondre = commentaire.locator("button[aria-label*='Répondre'], button[aria-label*='Reply']")
                if bouton_repondre.count() > 0:
                    bouton_repondre.first.click()
                    self._pause_humaine()
                    zone = self.page.locator(".comments-comment-texteditor .ql-editor").last
                    self._taper_comme_humain(zone, reponse)
                    self._pause_humaine()
                    zone.press("Enter")
                    self._attendre_chargement(1500)
                    self._log(f"Réponse commentaire → {auteur}")
                    return True
        return False

    def envoyer_message(self, profil_url: str, message: str) -> bool:
        """Envoie un message direct à un profil LinkedIn."""
        self.page.goto(profil_url)
        self._attendre_chargement()

        bouton_message = self.page.locator("button[aria-label*='Message'], a[aria-label*='Message']").first
        if bouton_message.count() == 0:
            return False

        bouton_message.click()
        self._pause_humaine()

        zone = self.page.locator(".msg-form__contenteditable, [placeholder*='Rédigez']").first
        self._taper_comme_humain(zone, message)
        self._pause_humaine()

        bouton_envoyer = self.page.locator("button[aria-label*='Envoyer'], button[aria-label*='Send']").last
        bouton_envoyer.click()
        self._attendre_chargement(1500)
        self._log(f"DM envoyé → {profil_url}")
        return True

    def envoyer_demande_connexion(self, profil_url: str, note: str = "") -> bool:
        """Envoie une demande de connexion avec note optionnelle."""
        self.page.goto(profil_url)
        self._attendre_chargement()

        bouton_connect = self.page.locator(
            "button[aria-label*='Se connecter'], button[aria-label*='Connect']"
        ).first
        if bouton_connect.count() == 0:
            return False

        bouton_connect.click()
        self._pause_humaine()

        if note:
            bouton_note = self.page.locator("button[aria-label*='Ajouter une note'], button[aria-label*='Add a note']")
            if bouton_note.count() > 0:
                bouton_note.first.click()
                self._pause_humaine()
                zone = self.page.locator("textarea[name='message']")
                self._taper_comme_humain(zone, note[:300])
                self._pause_humaine()

        bouton_envoyer = self.page.locator("button[aria-label*='Envoyer'], button[aria-label*='Send']").last
        bouton_envoyer.click()
        self._attendre_chargement(1500)
        self._log(f"Connexion envoyée → {profil_url}")
        return True

    # ── LECTURE ───────────────────────────────────────────────────

    def lire_notifications(self) -> list[dict]:
        """Lit les notifications récentes LinkedIn."""
        self.page.goto("https://www.linkedin.com/notifications/")
        self._attendre_chargement(2000)

        notifications = []
        items = self.page.locator(".nt-card-list .nt-card").all()[:10]
        for item in items:
            texte = item.text_content() or ""
            notifications.append({
                "type": self._detecter_type_notif(texte),
                "contenu": texte[:200].strip(),
                "date": datetime.now().isoformat(),
            })
        return notifications

    def lire_messages_non_lus(self) -> list[dict]:
        """Lit les messages non lus dans la messagerie."""
        self.page.goto("https://www.linkedin.com/messaging/")
        self._attendre_chargement(2000)

        messages = []
        conversations = self.page.locator(".msg-conversation-listitem").all()[:5]
        for conv in conversations:
            badge = conv.locator(".notification-badge")
            if badge.count() == 0:
                continue  # pas de message non lu

            conv.click()
            self._pause_humaine(500, 1000)

            dernier = self.page.locator(".msg-s-message-list-content .msg-s-event-listitem").last
            texte = dernier.text_content() or ""
            expediteur_el = conv.locator(".msg-conversation-listitem__participant-names")
            expediteur = expediteur_el.text_content().strip() if expediteur_el.count() > 0 else "Inconnu"

            messages.append({
                "expediteur": expediteur,
                "expediteur_id": expediteur.lower().replace(" ", "_"),
                "contenu": texte.strip(),
                "date": datetime.now().isoformat(),
            })

        return messages

    def obtenir_metriques_post(self, post_url: str) -> dict:
        """Extrait les métriques d'un post LinkedIn."""
        self.page.goto(post_url)
        self._attendre_chargement(2000)

        def extraire_nombre(selecteur: str) -> int:
            el = self.page.locator(selecteur).first
            if el.count() == 0:
                return 0
            texte = el.text_content() or "0"
            return self._parse_nombre(texte)

        return {
            "impressions": extraire_nombre("[aria-label*='impression'], .social-counts-reactions__count"),
            "likes": extraire_nombre(".social-counts-reactions__count"),
            "commentaires": extraire_nombre("button[aria-label*='commentaire'] span"),
            "partages": extraire_nombre("button[aria-label*='republication'] span"),
            "taux_engagement": 0.0,
            "date_publication": datetime.now().isoformat(),
        }

    def rechercher_profils(self, criteres: dict) -> list[dict]:
        """Recherche des profils LinkedIn selon des critères."""
        query = criteres.get("secteur", "commercial B2B")
        self.page.goto(f"https://www.linkedin.com/search/results/people/?keywords={query.replace(' ', '%20')}")
        self._attendre_chargement(2000)

        profils = []
        resultats = self.page.locator(".reusable-search__result-container").all()[:10]
        for r in resultats:
            nom_el = r.locator(".entity-result__title-text a span[aria-hidden='true']")
            titre_el = r.locator(".entity-result__primary-subtitle")
            lien_el = r.locator("a.app-aware-link").first
            nom = nom_el.text_content().strip() if nom_el.count() > 0 else ""
            titre = titre_el.text_content().strip() if titre_el.count() > 0 else ""
            url = lien_el.get_attribute("href") if lien_el.count() > 0 else ""

            if nom:
                profils.append({
                    "nom": nom,
                    "titre": titre,
                    "url": url,
                    "secteur": criteres.get("secteur", ""),
                    "connexions_communes": 0,
                    "actif_recemment": True,
                })

        return profils

    # ── PRIVÉ ─────────────────────────────────────────────────────

    def _connecter(self):
        """Se connecte à LinkedIn avec les identifiants du .env."""
        email = os.getenv("LINKEDIN_EMAIL")
        password = os.getenv("LINKEDIN_PASSWORD")
        if not email or not password:
            raise RuntimeError("LINKEDIN_EMAIL et LINKEDIN_PASSWORD requis dans .env")

        self.page.goto("https://www.linkedin.com/login")
        self._attendre_chargement(2000)

        self.page.fill("#username", email)
        self._pause_humaine(500, 1200)
        self.page.fill("#password", password)
        self._pause_humaine(800, 1500)
        self.page.click("button[type='submit']")
        self._attendre_chargement(4000)

        if "checkpoint" in self.page.url or "challenge" in self.page.url:
            raise RuntimeError(
                "LinkedIn demande une vérification manuelle. "
                "Connecte-toi manuellement une fois puis relance."
            )

        self.context.storage_state(path=str(self._session_path))
        self._log("Connexion réussie — session sauvegardée")

    def _session_valide(self) -> bool:
        """Vérifie que la session LinkedIn est toujours active."""
        self.page.goto("https://www.linkedin.com/feed/")
        self._attendre_chargement(2000)
        return "feed" in self.page.url and "login" not in self.page.url

    def _taper_comme_humain(self, element, texte: str):
        """Tape du texte caractère par caractère avec délais variables."""
        element.click()
        for char in texte:
            element.type(char, delay=random.randint(40, 140))
            if char in ".!?\n":
                time.sleep(random.uniform(0.2, 0.6))

    def _attendre_chargement(self, ms: int = 2000):
        self.page.wait_for_load_state("domcontentloaded")
        time.sleep(ms / 1000)

    def _pause_humaine(self, min_ms: int = 800, max_ms: int = 2500):
        time.sleep(random.uniform(min_ms / 1000, max_ms / 1000))

    def _detecter_type_notif(self, texte: str) -> str:
        texte = texte.lower()
        if "commenté" in texte or "comment" in texte:
            return "commentaire"
        if "aimé" in texte or "liked" in texte:
            return "reaction"
        if "partagé" in texte or "shared" in texte:
            return "partage"
        if "s'est connecté" in texte or "connected" in texte:
            return "connexion"
        return "autre"

    def _parse_nombre(self, texte: str) -> int:
        texte = texte.strip().replace(" ", "").replace(" ", "").replace(",", "")
        if "k" in texte.lower():
            return int(float(texte.lower().replace("k", "")) * 1000)
        try:
            return int("".join(filter(str.isdigit, texte)) or 0)
        except Exception:
            return 0

    def _joindre_image(self, image_path: str):
        input_file = self.page.locator("input[type='file']").first
        input_file.set_input_files(image_path)
        self._attendre_chargement(2000)

    def _log(self, message: str):
        log_path = DATA_DIR / "metrics" / f"{self.client_id}_playwright.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
