import requests
import streamlit as st
from app.config import GROQ_API_URL, MODEL


def _get_api_key() -> str:
    """
    Reads the Groq API key from Streamlit secrets (cloud) or
    falls back to a local .streamlit/secrets.toml for local dev.
    """
    try:
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        raise ValueError(
            "GROQ_API_KEY not found. "
            "Add it to .streamlit/secrets.toml locally, "
            "or to Streamlit Cloud secrets in the dashboard."
        )


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {_get_api_key()}",
        "Content-Type": "application/json",
    }


def query_llm(prompt: str) -> str:
    """Blocking call — returns full response as a string. Used by CLI."""
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }
    response = requests.post(GROQ_API_URL, headers=_headers(), json=payload, timeout=60)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def stream_llm(prompt: str):
    """Generator that yields text tokens one by one. Used by Streamlit UI."""
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
    }
    with requests.post(
        GROQ_API_URL, headers=_headers(), json=payload, stream=True, timeout=60
    ) as response:
        response.raise_for_status()
        for raw_line in response.iter_lines():
            if raw_line:
                line = raw_line.decode("utf-8")
                if line.startswith("data: ") and line != "data: [DONE]":
                    import json
                    chunk = json.loads(line[6:])
                    delta = chunk["choices"][0]["delta"].get("content", "")
                    if delta:
                        yield delta
