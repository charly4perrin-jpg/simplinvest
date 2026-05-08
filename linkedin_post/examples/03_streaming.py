"""
Streaming — Afficher la réponse en temps réel
L'utilisateur voit les tokens s'afficher au fur et à mesure,
comme ChatGPT. Réduit la latence perçue de 80 %.
"""
import anthropic

client = anthropic.Anthropic()

print("Claude répond : ", end="", flush=True)

with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=512,
    messages=[
        {
            "role": "user",
            "content": "Donne-moi 5 stratégies pour optimiser un portefeuille actions en 2025.",
        }
    ],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

print()  # saut de ligne final
final = stream.get_final_message()
print(f"\n✅ Terminé — {final.usage.output_tokens} tokens générés")
