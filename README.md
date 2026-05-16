# EcoLLM-RAG — Green AI Token Burning Analysis Board

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ecollm-rag-tokenization-burning-analysis-board.streamlit.app/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?logo=github)](https://github.com/srushtidharmale/EcoLLM-RAG-tokenization-burning-analysis-board-)

**Green AI:** Reducing token-level energy consumption through efficient LLM inference and exploring alternatives to semiconductor-heavy AI computing.

## Live demo

**Open the dashboard:** [https://ecollm-rag-tokenization-burning-analysis-board.streamlit.app/](https://ecollm-rag-tokenization-burning-analysis-board.streamlit.app/)

If the link is not live yet, deploy once (free) via [Streamlit Community Cloud](https://share.streamlit.io/):

1. Sign in with GitHub
2. **New app** → select repo `EcoLLM-RAG-tokenization-burning-analysis-board-`
3. **Main file path:** `streamlit_app.py`
4. Click **Deploy**

## Problem

LLMs burn energy on every token — input (prompt + RAG context) and output (generation). Typical API usage (Claude, GPT, etc.) often sends **full context** to **large models** for every query. EcoLLM-RAG optimizes **accuracy + energy + latency**.

## What we built

| Module | Purpose |
|--------|---------|
| **Energy-Aware Router** | Simple → TinyLlama, medium → Phi-3 + compressed RAG, complex → Mistral-7B |
| **Adaptive RAG** | Skips vector retrieval when not needed |
| **Prompt Compression** | Trims retrieved chunks before inference |
| **Token Budget Controller** | Caps max output tokens per route |
| **Energy Tracker** | Per-token Wh estimates + optional CodeCarbon |
| **Live Dashboard** | Streamlit UI with real-time savings charts |

## Quick start (local)

```bash
git clone https://github.com/srushtidharmale/EcoLLM-RAG-tokenization-burning-analysis-board-.git
cd EcoLLM-RAG-tokenization-burning-analysis-board-
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

CLI demo: `python run_demo.py`

## Research question

Can an energy-aware RAG system reduce token usage, latency, and estimated carbon emissions while maintaining answer quality?

## Metrics tracked

- Tokens (input / output / saved vs baseline)
- Latency (ms)
- Energy (Wh, mWh)
- CO₂ (g, mg)
- Answer quality score (simulated per tier)

## Project structure

```
ecollm/              # Core library (router, RAG, inference, energy)
app/dashboard.py     # Streamlit UI
streamlit_app.py     # Cloud entry point
data/                # Knowledge base
run_demo.py          # CLI demo
```

## Note on models

The demo uses **simulated** TinyLlama / Phi-3 / Mistral tiers so it runs without GPU or API keys. Swap `ecollm/inference.py` for Hugging Face + 4-bit loaders for production.

## License

MIT
