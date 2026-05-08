"""
Message Batches — Traitement en masse à -50 % de coût
Idéal pour analyser des centaines de documents hors ligne.
Les résultats sont disponibles en quelques minutes à quelques heures.
"""
import anthropic

client = anthropic.Anthropic()

tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA"]

requests = [
    {
        "custom_id": f"analyse-{ticker}",
        "params": {
            "model": "claude-haiku-4-5-20251001",  # modèle rapide et économique
            "max_tokens": 256,
            "messages": [
                {
                    "role": "user",
                    "content": f"En 2 phrases, donne les forces et risques clés de {ticker} pour un investisseur long terme.",
                }
            ],
        },
    }
    for ticker in tickers
]

batch = client.messages.batches.create(requests=requests)
print(f"Batch créé : {batch.id}")
print(f"Statut : {batch.processing_status}")
print(f"→ Récupérez les résultats avec : client.messages.batches.results('{batch.id}')")
