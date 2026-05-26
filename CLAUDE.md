# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

`simplinvest` is a content + code repository for a French LinkedIn post demonstrating four key Claude API techniques. It contains:

- `linkedin_post/POST_LINKEDIN.md` — the ready-to-publish LinkedIn post text (French)
- `linkedin_post/assets/` — post images (banner, tweet card, linkedin mockup) in PNG and SVG
- `linkedin_post/examples/` — five standalone Python scripts illustrating each Claude API feature

## Running the Examples

**Prerequisite**: set `ANTHROPIC_API_KEY` in your environment, then install the SDK:

```bash
pip install anthropic
```

Run any example directly:

```bash
python linkedin_post/examples/01_quickstart.py
python linkedin_post/examples/02_prompt_caching.py
python linkedin_post/examples/03_streaming.py
python linkedin_post/examples/04_tool_use.py
python linkedin_post/examples/05_batch_processing.py
```

There is no build system, test suite, or linter configured in this repository.

## Code Architecture

All five examples are independent, self-contained scripts. They share a common pattern:

```python
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
```

**Examples overview:**

| File | Feature | Key detail |
|------|---------|-----------|
| `01_quickstart.py` | Basic request | Baseline `client.messages.create()` call |
| `02_prompt_caching.py` | Prompt caching | `cache_control: {"type": "ephemeral"}` on the system prompt block; logs cache hit tokens |
| `03_streaming.py` | Streaming | `client.messages.stream()` context manager, iterates `stream.text_stream` |
| `04_tool_use.py` | Tool use / agents | Agentic loop: runs until `stop_reason == "end_turn"`, dispatches `tool_use` blocks to a local function |
| `05_batch_processing.py` | Message Batches | `client.messages.batches.create()` with a list of `{custom_id, params}` dicts; uses `claude-haiku-4-5-20251001` for cost efficiency |

**Models used:**
- `claude-sonnet-4-6` — default across examples 01–04
- `claude-haiku-4-5-20251001` — batch processing (example 05) for cost/speed

## Key Conventions in the Examples

- Finance / investment domain is used as the illustrative context throughout (stock tickers, P/E ratios, portfolio analysis).
- The tool use example (`04`) simulates a real stock-price API — the `get_stock_price` function contains a hardcoded prices dict; replace it with a real API call (yfinance, Alpha Vantage, etc.) for production use.
- Batch results are not polled in `05`; the script prints the batch ID and exits. Results are retrieved separately via `client.messages.batches.results(batch_id)`.
