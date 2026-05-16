# EcoLLM-RAG — Green AI Token Burning Analysis Board

[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?logo=github)](https://github.com/srushtidharmale/EcoLLM-RAG-tokenization-burning-analysis-board-)
[![Deploy to Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy?repository=srushtidharmale/EcoLLM-RAG-tokenization-burning-analysis-board-&branch=main&mainModule=streamlit_app.py)

**Green AI:** Reducing token-level energy consumption through efficient LLM inference.

## Live demo (public — anyone can open)

After you deploy once, share this link. **No sign-in required** for visitors when the app is set to **Public**.

| Platform | Your link (fill in after deploy) |
|----------|----------------------------------|
| **Streamlit Cloud** | `https://YOUR-APP-NAME.streamlit.app` |
| **Render** (recommended for public access) | `https://ecollm-rag-dashboard.onrender.com` |

### Make Streamlit publicly viewable (important)

If people see *"You do not have access"* or must sign in:

1. Go to [share.streamlit.io](https://share.streamlit.io/) → open your app.
2. Click **⚙️ Settings** (or **Manage app**).
3. Under **Sharing** / **Visibility**, choose **Public** (not Private).
4. Save → copy the `.streamlit.app` URL into this README.

[![Deploy to Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy?repository=srushtidharmale/EcoLLM-RAG-tokenization-burning-analysis-board-&branch=main&mainModule=streamlit_app.py)

- **Repository:** `srushtidharmale/EcoLLM-RAG-tokenization-burning-analysis-board-`
- **Main file:** `streamlit_app.py`

### Alternative: Render (always public URL)

1. [render.com](https://render.com) → sign in with GitHub.
2. **New +** → **Blueprint** → connect this repo (uses `render.yaml`).
3. Deploy → share the `onrender.com` link (no viewer login).

Details: [DEPLOY.md](DEPLOY.md)

## Problem

LLMs burn energy on every token. EcoLLM-RAG routes simple queries to small models, skips RAG when possible, and compresses context — vs always using a large model + full RAG.

## What we built

| Module | Purpose |
|--------|---------|
| **Energy-Aware Router** | TinyLlama / Phi-3 / Mistral by difficulty |
| **Adaptive RAG** | Retrieval only when needed |
| **Prompt Compression** | Fewer input tokens |
| **Live Dashboard** | Metrics + charts vs wasteful baseline |

## Local run

```bash
git clone https://github.com/srushtidharmale/EcoLLM-RAG-tokenization-burning-analysis-board-.git
cd EcoLLM-RAG-tokenization-burning-analysis-board-
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Open http://localhost:8501

## License

MIT
