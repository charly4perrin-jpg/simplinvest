"""
Générateur de contenu — produit des posts LinkedIn dans la voix du client.
Supporte 6 formats. Intègre le feedback loop pour s'améliorer avec le temps.
"""

import json
from datetime import datetime
from pathlib import Path
import anthropic
from config.settings import MODEL_MAIN, DATA_DIR, POST_FORMATS
from core.voice_engine import construire_system_prompt, valider_ton

INSTRUCTIONS_FORMAT = {
    "liste": """Format LISTE :
- Titre accrocheur (chiffre + résultat contre-intuitif)
- 4 à 6 points numérotés, courts, chacun avec une explication en 1 ligne
- Conclusion en 1 phrase
- Question d'engagement finale""",

    "storytelling": """Format STORYTELLING :
- Situation de départ en 1 phrase (accrocheuse, concrète)
- Problème / tension
- Action prise
- Résultat obtenu
- Leçon applicable par le lecteur
- Question ou CTA court""",

    "avant_apres": """Format AVANT / APRÈS :
- Contraste immédiat : état avant vs état après
- 3 à 5 étapes concrètes de la transformation
- Chiffres si possible
- CTA direct à la fin""",

    "opinion": """Format OPINION TRANCHÉE :
- Affirmation polarisante en ouverture (pas de "selon moi", juste l'affirmation)
- 3 arguments courts qui la soutiennent
- Nuance optionnelle en 1 phrase
- "D'accord ou pas ? ⬇️" en fermeture""",

    "coulisses": """Format COULISSES :
- Partage personnel, moment de vulnérabilité ou d'honnêteté
- Ce que ça t'a appris
- Pourquoi c'est utile pour le lecteur
- Invitation à partager son expérience""",

    "tips": """Format TIPS RAPIDES :
- Promesse en titre : "X choses que tu peux faire aujourd'hui"
- Chaque tip en 2 lignes max : problème → solution
- Actionnable immédiatement
- Pas de théorie, que du concret""",
}


def generer_post(
    persona: dict,
    sujet: str,
    format_post: str = "liste",
    contexte_supplementaire: str = "",
) -> dict:
    """Génère un post LinkedIn dans la voix du client."""
    if format_post not in POST_FORMATS:
        format_post = "liste"

    client = anthropic.Anthropic()
    system_prompt = construire_system_prompt(persona)
    instruction = INSTRUCTIONS_FORMAT[format_post]

    contexte = f"\nContexte additionnel : {contexte_supplementaire}" if contexte_supplementaire else ""

    prompt = f"""Écris un post LinkedIn sur ce sujet : "{sujet}"

{instruction}
{contexte}

Le post doit résonner avec le client idéal : {persona['strategie']['client_ideal']}
Et mettre en valeur : {persona['strategie']['resultat_promis']}"""

    message = client.messages.create(
        model=MODEL_MAIN,
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": prompt}],
    )

    contenu = message.content[0].text
    validation = valider_ton(contenu, persona)

    post = {
        "id": f"{persona['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "client_id": persona["id"],
        "sujet": sujet,
        "format": format_post,
        "contenu": contenu,
        "longueur": len(contenu),
        "validation": validation,
        "statut": "genere",  # genere → valide → publie
        "cree_le": datetime.now().isoformat(),
        "publie_le": None,
        "metriques": {},
    }

    _sauvegarder_post(post)
    return post


def generer_serie_semaine(persona: dict, sujets: list[str]) -> list[dict]:
    """Génère une semaine de posts sur des sujets donnés avec formats variés."""
    formats_rotation = ["liste", "storytelling", "opinion", "tips", "coulisses"]
    posts = []

    for i, sujet in enumerate(sujets[:5]):
        format_post = formats_rotation[i % len(formats_rotation)]
        post = generer_post(persona, sujet, format_post)
        posts.append(post)
        print(f"Post {i+1}/{ min(len(sujets), 5)} généré — score : {post['validation'].get('score_global', '?')}/40")

    return posts


def _sauvegarder_post(post: dict):
    dossier = DATA_DIR / "posts" / post["client_id"]
    dossier.mkdir(parents=True, exist_ok=True)
    chemin = dossier / f"{post['id']}.json"
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(post, f, ensure_ascii=False, indent=2)


def charger_posts_client(client_id: str, statut: str = None) -> list[dict]:
    dossier = DATA_DIR / "posts" / client_id
    if not dossier.exists():
        return []
    posts = []
    for fichier in sorted(dossier.glob("*.json"), reverse=True):
        with open(fichier, encoding="utf-8") as f:
            post = json.load(f)
        if statut is None or post.get("statut") == statut:
            posts.append(post)
    return posts


def valider_post(post_id: str, client_id: str) -> bool:
    """Marque un post comme validé par le client."""
    dossier = DATA_DIR / "posts" / client_id
    chemin = dossier / f"{post_id}.json"
    if not chemin.exists():
        return False
    with open(chemin, encoding="utf-8") as f:
        post = json.load(f)
    post["statut"] = "valide"
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(post, f, ensure_ascii=False, indent=2)
    return True
