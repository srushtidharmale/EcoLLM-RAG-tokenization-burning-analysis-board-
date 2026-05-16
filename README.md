# EcoLLM-RAG — Green AI Token Burning Analysis Board

[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?logo=github)](https://github.com/srushtidharmale/EcoLLM-RAG-tokenization-burning-analysis-board-)
[![Deploy to Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy?repository=srushtidharmale/EcoLLM-RAG-tokenization-burning-analysis-board-&branch=main&mainModule=streamlit_app.py)

**Green AI:** Reducing token-level energy consumption through efficient LLM inference.

## Live demo

The dashboard is **not online until you deploy it once** (free).

1. Click **Deploy to Streamlit** badge above (sign in with GitHub as `srushtidharmale`).
2. Confirm **Main file:** `streamlit_app.py` → **Deploy**.
3. Copy the URL Streamlit gives you (e.g. `https://your-app-name.streamlit.app`).

Full instructions: [DEPLOY.md](DEPLOY.md)

> If you see *"You do not have access to this app"* — that URL does not exist yet. Deploy first, then use the URL from your Streamlit dashboard.

## Problem

LLMs burn energy on every token. Typical API usage (Claude, GPT, etc.) sends **full context** to **large models** for every query. EcoLLM-RAG optimizes **accuracy + energy + latency**.

## What we built

| Module | Purpose |
|--------|---------|
| **Energy-Aware Router** | Simple → TinyLlama, medium → Phi-3 + compressed RAG, complex → Mistral-7B |
| **Adaptive RAG** | Skips retrieval when not needed |
| **Prompt Compression** | Trims context before inference |
| **Token Budget** | Caps output tokens per route |
| **Live Dashboard** | Streamlit UI with savings charts vs baseline |

## Local run

```bash
git clone https://github.com/srushtidharmale/EcoLLM-RAG-tokenization-burning-analysis-board-.git
cd EcoLLM-RAG-tokenization-burning-analysis-board-
pip install -r requirements.txt
streamlit run streamlit_app.py
```

CLI demo: `python run_demo.py`

## Research question

Can an energy-aware RAG system reduce token usage, latency, and estimated CO₂ while maintaining answer quality?

## Project structure

```
ecollm/              # Router, RAG, inference, energy tracker
app/dashboard.py     # Streamlit UI
streamlit_app.py     # Cloud entry point (use this for deploy)
data/                # Knowledge base
```

## License

MIT
