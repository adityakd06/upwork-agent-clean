import json
import time
import requests
import streamlit as st
from config import GROQ_API_URL, MODEL


def _get_api_key() -> str:
    try:
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        raise ValueError("GROQ_API_KEY not found in Streamlit secrets.")


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {_get_api_key()}",
        "Content-Type": "application/json",
    }


def query_llm(prompt: str) -> str:
    """Blocking call with retry on 429."""
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "temperature": 0.7,
        "max_tokens": 1024,
        "top_p": 0.9,
        "frequency_penalty": 0.4,
    }
    for attempt in range(3):
        response = requests.post(GROQ_API_URL, headers=_headers(), json=payload, timeout=60)
        if response.status_code == 429:
            wait = 20 * (attempt + 1)
            time.sleep(wait)
            continue
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    raise Exception("Groq rate limit hit after 3 retries. Please wait a minute and try again.")


def stream_llm(prompt: str):
    """Streaming call with retry on 429."""
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
        "temperature": 0.7,
        "max_tokens": 1024,
        "top_p": 0.9,
        "frequency_penalty": 0.4,
    }
    for attempt in range(3):
        response = requests.post(GROQ_API_URL, headers=_headers(), json=payload, stream=True, timeout=60)
        if response.status_code == 429:
            wait = 20 * (attempt + 1)
            time.sleep(wait)
            continue
        response.raise_for_status()
        for raw_line in response.iter_lines():
            if raw_line:
                line = raw_line.decode("utf-8")
                if line.startswith("data: ") and line != "data: [DONE]":
                    chunk = json.loads(line[6:])
                    delta = chunk["choices"][0]["delta"].get("content", "")
                    if delta:
                        yield delta
        return
    raise Exception("Groq rate limit hit after 3 retries. Please wait a minute and try again.")