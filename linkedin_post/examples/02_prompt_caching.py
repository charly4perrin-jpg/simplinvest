"""
Prompt Caching — Réduire les coûts jusqu'à 90 %
Le cache stocke les tokens du system prompt côté serveur pendant 5 minutes.
Idéal quand vous envoyez de nombreux messages avec le même contexte.
"""
import anthropic

client = anthropic.Anthropic()

SYSTEM_CONTEXT = """
Tu es un expert en finance quantitative avec 20 ans d'expérience.
Tu analyses les données de marché, construis des modèles de valorisation
et fournis des recommandations précises basées sur des faits chiffrés.
[... imaginez ici 10 000 tokens de contexte métier ...]
"""

def ask_claude(question: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=[
            {
                "type": "text",
                "text": SYSTEM_CONTEXT,
                "cache_control": {"type": "ephemeral"},  # ← la magie est ici
            }
        ],
        messages=[{"role": "user", "content": question}],
    )
    usage = response.usage
    cache_hit = getattr(usage, "cache_read_input_tokens", 0)
    print(f"Cache hit: {cache_hit} tokens économisés 💰")
    return response.content[0].text


# Premier appel : cache miss (tokens facturés normalement)
print(ask_claude("Analyse le P/E ratio d'Apple à 28x."))

# Appels suivants : cache hit (coût réduit de 90 % sur le system prompt)
print(ask_claude("Que penses-tu du beta de Tesla ?"))
print(ask_claude("Compare Nvidia et AMD sur les marges brutes."))
