# EcoLLM-RAG — Green AI Token Burning Analysis Board

[![Live Demo](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ecollm-rag-tokenization-burning-analysis-board.streamlit.app/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?logo=github)](https://github.com/srushtidharmale/EcoLLM-RAG-tokenization-burning-analysis-board-)

**Green AI:** Reducing token-level energy consumption through efficient LLM inference.

## 🌐 Live demo (public)

**Open the dashboard (no install, no login):**

### 👉 [https://ecollm-rag-tokenization-burning-analysis-board.streamlit.app/](https://ecollm-rag-tokenization-burning-analysis-board.streamlit.app/)

Anyone with this link can use the app. Share it on GitHub, LinkedIn, or your resume.

| What you can try | |
|------------------|--|
| Sidebar demos | Click **Hi there!**, token burning, Green AI, adaptive RAG |
| Custom question | Type a query → **Run EcoLLM** |
| Charts | Energy saved vs baseline (green vs red bars) |

Deploy / update instructions: [DEPLOY.md](DEPLOY.md)

## Problem

LLMs burn energy on every token. EcoLLM-RAG routes simple queries to small models, skips RAG when possible, and compresses context — vs always using a large model + full RAG (like typical Claude/GPT API usage).

## What we built

| Module | Purpose |
|--------|---------|
| **Energy-Aware Router** | TinyLlama / Phi-3 / Mistral by query difficulty |
| **Adaptive RAG** | Retrieval only when needed |
| **Prompt Compression** | Fewer input tokens |
| **Live Dashboard** | Tokens, energy (mWh), CO₂, latency, savings charts |

## Run locally (optional)

```bash
git clone https://github.com/srushtidharmale/EcoLLM-RAG-tokenization-burning-analysis-board-.git
cd EcoLLM-RAG-tokenization-burning-analysis-board-
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Then open http://localhost:8501

## Research question

Can an energy-aware RAG system reduce token usage, latency, and estimated CO₂ while maintaining answer quality?

## License

MIT
