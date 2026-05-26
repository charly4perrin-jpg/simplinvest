"""
Générateur de posts LinkedIn — Personal Branding pour Commerciaux
Usage : python generateur_posts.py
"""

import anthropic

SYSTEM_PROMPT = """Tu es un expert en personal branding LinkedIn pour commerciaux.
Tu génères des posts LinkedIn percutants pour quelqu'un qui vend des services de
personal branding et gestion de compte LinkedIn à des commerciaux/sales.

Style d'écriture :
- Phrases courtes. Une idée par ligne.
- Pas de jargon bullshit marketing
- Ton direct, authentique, parfois un peu provoc
- Toujours une valeur actionnable ou une insight concrète
- Terminer par une question d'engagement OU un CTA clair, jamais les deux
- Maximum 1300 caractères (limite LinkedIn)
- Pas d'emojis en excès (1-2 max, bien placés)
- Utiliser des tirets (→) plutôt que des puces classiques

Persona de l'auteur :
- Jeune entrepreneur français
- Vend du personal branding + gestion de compte LinkedIn
- Cible : commerciaux, BDR, SDR, indépendants sales
- Documente sa propre méthode en live
- A un chat comme mascotte récurrente (à intégrer quand pertinent)
- Ton Robin Tempe / Alexandre Dana mais version sales LinkedIn
"""

FORMATS = {
    "liste": "Format LISTE : Titre accrocheur + 5 points numérotés courts + conclusion + question",
    "story": "Format STORYTELLING : Situation → Problème → Action → Résultat → Leçon → Question",
    "avant_apres": "Format AVANT/APRÈS : Contraste clair + étapes concrètes + CTA",
    "opinion": "Format OPINION TRANCHÉE : Affirmation polarisante + 3 arguments + question finale",
    "coulisses": "Format COULISSES : Partage personnel + leçon + invitation à échanger",
}

def generer_post(sujet: str, format_post: str = "liste") -> str:
    client = anthropic.Anthropic()

    instruction_format = FORMATS.get(format_post, FORMATS["liste"])

    prompt = f"""Génère un post LinkedIn sur ce sujet : "{sujet}"

{instruction_format}

Le post doit parler directement aux commerciaux et leur donner envie de liker, commenter ou enregistrer.
Si pertinent, intègre subtilement le chat comme élément de storytelling ou d'illustration.
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text


def generer_serie(sujet_principal: str) -> list[str]:
    """Génère 4 posts sur le même sujet dans 4 formats différents."""
    client = anthropic.Anthropic()
    posts = []

    for nom_format, instruction in FORMATS.items():
        if nom_format == "avant_apres":
            continue  # nécessite un vrai cas client, skip en automatique

        prompt = f"""Génère un post LinkedIn sur ce sujet : "{sujet_principal}"

{instruction}

Le post doit parler directement aux commerciaux.
Si pertinent, intègre le chat comme élément récurrent.
"""
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        posts.append({
            "format": nom_format,
            "contenu": message.content[0].text,
        })

    return posts


def main():
    print("=== GÉNÉRATEUR DE POSTS LINKEDIN ===\n")

    print("Formats disponibles :")
    for i, (nom, desc) in enumerate(FORMATS.items(), 1):
        print(f"  {i}. {nom}")

    print()
    sujet = input("Sujet du post : ").strip()
    format_choix = input("Format (liste/story/avant_apres/opinion/coulisses) [liste] : ").strip() or "liste"

    print("\nGénération en cours...\n")
    print("─" * 50)

    post = generer_post(sujet, format_choix)

    print(post)
    print("─" * 50)
    print(f"\nLongueur : {len(post)} caractères (limite LinkedIn : 1300)")

    sauvegarder = input("\nSauvegarder ce post ? (o/n) [n] : ").strip().lower()
    if sauvegarder == "o":
        import os
        from datetime import datetime

        os.makedirs("posts", exist_ok=True)
        nom_fichier = f"posts/{datetime.now().strftime('%Y%m%d_%H%M')}_{format_choix}.md"
        with open(nom_fichier, "w", encoding="utf-8") as f:
            f.write(f"# Post LinkedIn — {sujet}\n")
            f.write(f"Format : {format_choix}\n")
            f.write(f"Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")
            f.write("---\n\n")
            f.write(post)

        print(f"Post sauvegardé : {nom_fichier}")


if __name__ == "__main__":
    main()
