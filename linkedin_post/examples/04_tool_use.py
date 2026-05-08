"""
Tool Use (Function Calling) — Connecter Claude au monde réel
Claude décide quand appeler vos fonctions et comment utiliser les résultats.
Exemple : récupérer le cours d'une action en temps réel.
"""
import json
import anthropic

client = anthropic.Anthropic()

tools = [
    {
        "name": "get_stock_price",
        "description": "Récupère le cours actuel d'une action boursière.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Le symbole boursier, ex: AAPL, TSLA, NVDA",
                }
            },
            "required": ["ticker"],
        },
    }
]


def get_stock_price(ticker: str) -> dict:
    """Simulé — remplacez par votre vrai appel API (yfinance, Alpha Vantage…)"""
    prices = {"AAPL": 189.50, "TSLA": 248.30, "NVDA": 875.20}
    price = prices.get(ticker.upper(), 100.0)
    return {"ticker": ticker.upper(), "price": price, "currency": "USD"}


def run_agent(user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            tools=tools,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            return next(b.text for b in response.content if b.type == "text")

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = get_stock_price(**block.input)
                tool_results.append(
                    {"type": "tool_result", "tool_use_id": block.id, "content": json.dumps(result)}
                )

        messages += [
            {"role": "assistant", "content": response.content},
            {"role": "user", "content": tool_results},
        ]


print(run_agent("Compare les cours d'AAPL, TSLA et NVDA. Laquelle est la plus performante ?"))
