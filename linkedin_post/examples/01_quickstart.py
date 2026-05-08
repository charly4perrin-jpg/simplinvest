"""
Claude API — Démarrage ultra-rapide
Installer : pip install anthropic
"""
import anthropic

client = anthropic.Anthropic()  # lit ANTHROPIC_API_KEY depuis l'env

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Explique le prompt caching en 3 points."}
    ]
)

print(response.content[0].text)
