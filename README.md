# Upwork AI Agent

Generate tailored Upwork proposals using Groq's free, ultra-fast LLM API.

## Step 1 — Get a Free Groq API Key

1. Go to https://console.groq.com
2. Sign up for free
3. Go to **API Keys** → **Create API Key**
4. Copy the key

## Step 2 — Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 3 — Run Locally

Paste your Groq API key into `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "gsk_your_key_here"
```

Then run:

```bash
streamlit run streamlit_app.py
```

---

## Deploy to Streamlit Community Cloud (Free Hosting)

1. Push this project to a **GitHub repo**
   - Make sure `.streamlit/secrets.toml` is in `.gitignore` ✅ (already set)

2. Go to https://share.streamlit.io and sign in with GitHub

3. Click **New app** → select your repo → set main file to `streamlit_app.py`

4. Before deploying, click **Advanced settings** → **Secrets** and paste:
   ```toml
   GROQ_API_KEY = "gsk_your_key_here"
   ```

5. Hit **Deploy** — you'll get a public URL in ~60 seconds!

---

## Project Structure

```
upwork-ai-agent/
├── streamlit_app.py        ← entry point (run this)
├── main.py                 ← CLI entry point
├── app/
│   ├── config.py           ← all settings in one place
│   ├── loader.py           ← loads .docx files (cached)
│   ├── llm_client.py       ← talks to Groq API (streaming)
│   ├── generate.py         ← builds prompt, calls LLM
│   └── ui.py               ← Streamlit UI
├── .streamlit/
│   ├── secrets.toml        ← your API key (never commit this)
│   └── config.toml         ← app theme
├── data/
│   ├── knowledge_base/     ← your past proposals (.docx)
│   ├── prompts/            ← behavioral instructions (.docx)
│   └── outputs/            ← saved generated proposals
└── requirements.txt
```
