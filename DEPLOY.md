# Make the dashboard publicly viewable (no login for visitors)

## Option A — Streamlit Community Cloud (free)

### Deploy

1. Open: [Deploy EcoLLM-RAG](https://share.streamlit.io/deploy?repository=srushtidharmale/EcoLLM-RAG-tokenization-burning-analysis-board-&branch=main&mainModule=streamlit_app.py)
2. Sign in with GitHub as **srushtidharmale**.
3. **Main file path:** `streamlit_app.py` → **Deploy**.

### Set to PUBLIC (required)

Without this step, visitors may see *"You do not have access"*.

1. Go to [share.streamlit.io](https://share.streamlit.io/).
2. Click your app → **Settings** (gear icon).
3. Find **Sharing** or **App visibility**.
4. Select **Public** (not Private / Workspace only).
5. Save.

Test in an **incognito window** (not signed in). The dashboard should load without asking anyone to log in.

### Update GitHub README

Replace `YOUR-APP-NAME` in README with your real URL, e.g.  
`https://ecollm-rag-dashboard.streamlit.app`

---

## Option B — Render.com (public by default)

Good if Streamlit sharing settings are confusing.

1. Go to [render.com](https://render.com) and sign in with GitHub.
2. **New +** → **Blueprint**.
3. Connect repo: `EcoLLM-RAG-tokenization-burning-analysis-board-`.
4. Render reads `render.yaml` and deploys.
5. Share the URL: `https://ecollm-rag-dashboard.onrender.com` (or the name Render assigns).

Anyone with the link can open the app — no Streamlit account needed.

---

## Option C — Local only

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

---

## Troubleshooting

| Symptom | Fix |
|--------|-----|
| "App does not exist" | Deploy first; do not use a guessed URL |
| "No access" while logged in | Wrong URL, or app is **Private** → set **Public** |
| Visitors must sign in | App is Private — change to Public in Streamlit Settings |
| Broken badge image on GitHub | Normal until deploy; use the deploy link above |
