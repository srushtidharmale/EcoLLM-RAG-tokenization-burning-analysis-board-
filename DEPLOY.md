# Deploy live dashboard (Streamlit Community Cloud)

The error **"You do not have access to this app or it does not exist"** means the app is **not deployed yet** (or you opened the wrong URL). Follow these steps once.

## Step 1 — Open Streamlit Cloud

Go to: **https://share.streamlit.io/**

Sign in with **GitHub** (use the same account that owns the repo: `srushtidharmale`).

## Step 2 — Create the app

1. Click **"Create app"** (top right).
2. Under **Repository**, pick:
   `srushtidharmale/EcoLLM-RAG-tokenization-burning-analysis-board-`
3. Set:
   - **Branch:** `main`
   - **Main file path:** `streamlit_app.py`
4. Click **Deploy**.

Wait 2–3 minutes for the build to finish.

## Step 3 — Copy YOUR real URL

After deploy, Streamlit shows a URL like:

`https://ecollm-rag-tokenization-burning-analysis-board-xxxxx.streamlit.app`

That is your **live demo** link. Share that URL (not a guessed link from the README).

## Step 4 — Make it public

In the Streamlit app settings:

- **Sharing** → ensure the app is **Public** (not private to your workspace).

Public apps can be opened by anyone without signing in.

## Quick deploy link

[![Deploy to Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy?repository=srushtidharmale/EcoLLM-RAG-tokenization-burning-analysis-board-&branch=main&mainModule=streamlit_app.py)

Click the badge above (after signing into Streamlit with GitHub), then confirm settings and deploy.

## Troubleshooting

| Problem | Fix |
|--------|-----|
| "App does not exist" | Deploy first on share.streamlit.io — the README URL is only valid **after** you deploy |
| "No access" while signed in | Use the URL from **your** Streamlit dashboard, not someone else's |
| Build fails | Check logs; ensure `streamlit_app.py` and `requirements.txt` are in the repo root on `main` |
| Wrong GitHub account | Streamlit → Settings → reconnect GitHub as `srushtidharmale` |

## Run locally (always works)

```bash
git clone https://github.com/srushtidharmale/EcoLLM-RAG-tokenization-burning-analysis-board-.git
cd EcoLLM-RAG-tokenization-burning-analysis-board-
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Open http://localhost:8501
