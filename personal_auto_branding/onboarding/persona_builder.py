"""
Onboarding client — construit l'empreinte vocale et le profil stratégique.
C'est la fondation de tout le système : sans persona solide, tout le contenu sonne faux.
"""

import json
from pathlib import Path
from datetime import datetime
import anthropic
from config.settings import MODEL_MAIN, DATA_DIR


def creer_persona(client_id: str) -> dict:
    """Collecte les informations du client via un questionnaire interactif."""
    print(f"\n=== ONBOARDING — {client_id} ===\n")

    persona = {
        "id": client_id,
        "cree_le": datetime.now().isoformat(),
        "profil": {},
        "voix": {},
        "strategie": {},
    }

    print("── PROFIL DE BASE ──")
    persona["profil"]["nom"] = input("Prénom et nom : ").strip()
    persona["profil"]["metier"] = input("Métier / secteur : ").strip()
    persona["profil"]["entreprise"] = input("Entreprise ou 'indépendant' : ").strip()
    persona["profil"]["ville"] = input("Ville : ").strip()
    persona["profil"]["annees_experience"] = input("Années d'expérience dans ton domaine : ").strip()

    print("\n── OBJECTIFS LINKEDIN ──")
    persona["strategie"]["objectif_principal"] = input(
        "Objectif principal (ex: leads, recrutement, visibilité, partenariats) : "
    ).strip()
    persona["strategie"]["client_ideal"] = input(
        "Décris ton client/prospect idéal (poste, secteur, taille entreprise) : "
    ).strip()
    persona["strategie"]["resultat_promis"] = input(
        "Quel résultat concret tu veux montrer sur LinkedIn ? : "
    ).strip()

    print("\n── VOIX ET STYLE ──")
    persona["voix"]["ton"] = input(
        "Ton préféré (ex: direct, inspirant, éducatif, provocateur, humble) : "
    ).strip()
    persona["voix"]["sujets_forces"] = input(
        "Tes 3 sujets d'expertise (séparés par virgule) : "
    ).strip()
    persona["voix"]["sujets_interdits"] = input(
        "Sujets à éviter absolument (politique, concurrents, etc.) : "
    ).strip()
    persona["voix"]["exemples_posts"] = input(
        "Colle 1-2 posts que tu as écrits ou que tu aimes (ou tape 'skip') : "
    ).strip()

    print("\n── CONCURRENTS / INSPIRATIONS ──")
    persona["strategie"]["inspirations"] = input(
        "Comptes LinkedIn qui t'inspirent (noms, séparés par virgule) : "
    ).strip()

    # Génération de l'empreinte vocale via Claude
    print("\nAnalyse de ta voix en cours...")
    persona["voix"]["empreinte"] = _generer_empreinte_vocale(persona)

    # Sauvegarde
    chemin = DATA_DIR / "profiles" / f"{client_id}.json"
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(persona, f, ensure_ascii=False, indent=2)

    print(f"\nPersona créé et sauvegardé : {chemin}")
    return persona


def _generer_empreinte_vocale(persona: dict) -> str:
    """Synthétise une empreinte vocale réutilisable pour tous les prompts de génération."""
    client = anthropic.Anthropic()

    prompt = f"""Voici le profil d'un client LinkedIn :

Métier : {persona['profil']['metier']}
Entreprise : {persona['profil']['entreprise']}
Expérience : {persona['profil']['annees_experience']} ans
Objectif LinkedIn : {persona['strategie']['objectif_principal']}
Client idéal : {persona['strategie']['client_ideal']}
Résultat promis : {persona['strategie']['resultat_promis']}
Ton souhaité : {persona['voix']['ton']}
Sujets forts : {persona['voix']['sujets_forces']}
Sujets interdits : {persona['voix']['sujets_interdits']}
Exemples de posts : {persona['voix']['exemples_posts']}
Inspirations : {persona['strategie']['inspirations']}

Génère une "empreinte vocale" en 200 mots maximum.
Ce texte sera injecté comme instruction dans chaque prompt de génération de contenu.
Il doit décrire : le style d'écriture, le niveau de langage, les tournures typiques,
ce qu'il dit souvent, ce qu'il ne dit jamais, l'énergie générale du compte.
Sois précis et actionnable — c'est un guide pour une IA qui va écrire à sa place."""

    message = client.messages.create(
        model=MODEL_MAIN,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def charger_persona(client_id: str) -> dict:
    chemin = DATA_DIR / "profiles" / f"{client_id}.json"
    if not chemin.exists():
        raise FileNotFoundError(f"Persona introuvable pour : {client_id}")
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


def lister_clients() -> list[str]:
    dossier = DATA_DIR / "profiles"
    dossier.mkdir(parents=True, exist_ok=True)
    return [p.stem for p in dossier.glob("*.json")]
