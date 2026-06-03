import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Modèles Claude
MODEL_MAIN = "claude-sonnet-4-6"
MODEL_FAST = "claude-haiku-4-5-20251001"

# Limites LinkedIn (imitation comportement humain)
LINKEDIN_LIMITS = {
    "connections_per_day": 20,
    "messages_per_day": 15,
    "comments_per_day": 30,
    "posts_per_day": 2,
    "min_delay_seconds": 45,
    "max_delay_seconds": 180,
}

# Scoring leads
LEAD_SCORE_THRESHOLD = 60  # score /100 pour qualifier un lead chaud

# Sécurité
CRISIS_KEYWORDS = [
    "arnaque", "fraude", "faux", "bot", "automatisé", "spam",
    "honteux", "scandaleux", "fake", "scam", "report", "signaler",
]

# Formats de posts supportés
POST_FORMATS = ["liste", "storytelling", "avant_apres", "opinion", "coulisses", "tips"]

# Horaires optimaux de publication (heure locale)
OPTIMAL_HOURS = [7, 8, 12, 13, 17, 18]
OPTIMAL_DAYS = [1, 2, 3, 4]  # Lundi=0, Vendredi=4
