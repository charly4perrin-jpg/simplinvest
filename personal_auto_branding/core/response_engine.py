"""
Moteur de réponses — gère les commentaires et DMs en maintenant la voix du client.
Intègre la mémoire conversationnelle pour des échanges cohérents dans le temps.
"""

import anthropic
from config.settings import MODEL_FAST, MODEL_MAIN
from core.voice_engine import construire_system_prompt
from safety.crisis_manager import analyser_risque
from memory.conversation_memory import charger_historique, sauvegarder_echange


def repondre_commentaire(
    persona: dict,
    post_contenu: str,
    commentaire: str,
    auteur: str,
    historique_auteur: list = None,
) -> dict:
    """Génère une réponse à un commentaire LinkedIn."""
    risque = analyser_risque(commentaire)
    if risque["flag"]:
        return {
            "action": "escalade_humain",
            "raison": risque["raison"],
            "commentaire_original": commentaire,
            "auteur": auteur,
        }

    historique = historique_auteur or charger_historique(persona["id"], auteur)
    client = anthropic.Anthropic()
    system_prompt = construire_system_prompt(persona)

    contexte_historique = ""
    if historique:
        derniers = historique[-3:]
        contexte_historique = "\nÉchanges précédents avec cette personne :\n" + "\n".join(
            f"- {e['role']}: {e['contenu'][:100]}..." for e in derniers
        )

    prompt = f"""Tu réponds à un commentaire LinkedIn sur ce post :

POST : {post_contenu[:300]}...

COMMENTAIRE de {auteur} : {commentaire}
{contexte_historique}

Consignes :
- Réponse courte (2-4 lignes max)
- Chaleureuse mais sans excès
- Ajoute de la valeur ou pose une question de relance
- Ne répète pas ce qui est déjà dans le post
- Tutoie si le commentaire est en tutoiement, vouvoie sinon"""

    message = client.messages.create(
        model=MODEL_FAST,
        max_tokens=256,
        system=system_prompt,
        messages=[{"role": "user", "content": prompt}],
    )

    reponse = message.content[0].text
    sauvegarder_echange(persona["id"], auteur, "commentaire", commentaire, reponse)

    return {"action": "repondre", "contenu": reponse, "auteur": auteur}


def repondre_dm(
    persona: dict,
    message_recu: str,
    expediteur: str,
    profil_expediteur: dict = None,
) -> dict:
    """Génère une réponse à un message direct LinkedIn."""
    risque = analyser_risque(message_recu)
    if risque["flag"]:
        return {
            "action": "escalade_humain",
            "raison": risque["raison"],
            "message_original": message_recu,
            "expediteur": expediteur,
        }

    historique = charger_historique(persona["id"], expediteur)
    client = anthropic.Anthropic()
    system_prompt = construire_system_prompt(persona)

    contexte_profil = ""
    if profil_expediteur:
        contexte_profil = f"\nProfil de l'expéditeur : {profil_expediteur.get('titre', '')} chez {profil_expediteur.get('entreprise', '')}"

    contexte_historique = ""
    if historique:
        derniers = historique[-5:]
        contexte_historique = "\nHistorique de conversation :\n" + "\n".join(
            f"[{e['role']}] {e['contenu'][:150]}" for e in derniers
        )

    # Détecter l'intention du message
    intention = _detecter_intention(message_recu)

    prompt = f"""Tu réponds à un message direct LinkedIn.

Expéditeur : {expediteur}
{contexte_profil}
{contexte_historique}

Message reçu : {message_recu}

Intention détectée : {intention}

Consignes selon l'intention :
- "curiosite" → Engage la conversation, pose une question qualifiante
- "interet_service" → Décris brièvement la valeur, propose un appel découverte
- "objection" → Réponds calmement avec un argument concret
- "compliment" → Remercie brièvement et relance sur leur situation
- "autre" → Réponds avec naturel et curiosité

Réponse en 3-6 lignes. Naturelle, pas commerciale."""

    message = client.messages.create(
        model=MODEL_MAIN,
        max_tokens=512,
        system=system_prompt,
        messages=[{"role": "user", "content": prompt}],
    )

    reponse = message.content[0].text
    sauvegarder_echange(persona["id"], expediteur, "dm", message_recu, reponse)

    return {
        "action": "repondre",
        "contenu": reponse,
        "expediteur": expediteur,
        "intention": intention,
    }


def _detecter_intention(message: str) -> str:
    """Classifie rapidement l'intention d'un message entrant."""
    client = anthropic.Anthropic()
    prompt = f"""Classifie ce message LinkedIn en une seule catégorie :
- curiosite (veut en savoir plus sans intention d'achat)
- interet_service (potentiellement intéressé par un service)
- objection (résistance, scepticisme)
- compliment (félicitation, remerciement)
- autre

Message : "{message}"

Réponds uniquement avec le nom de la catégorie, rien d'autre."""

    msg = client.messages.create(
        model=MODEL_FAST,
        max_tokens=20,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip().lower()
