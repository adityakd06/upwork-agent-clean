import os

# ── Base Paths ───────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

KNOWLEDGE_PATH = os.path.join(DATA_DIR, "knowledge_base", "PowerBI_Healthcare_Proposal.docx")
PROMPT_PATH    = os.path.join(DATA_DIR, "prompts", "PROMPTS.docx")
OUTPUT_PATH    = os.path.join(DATA_DIR, "outputs", "generated_proposals.txt")

# ── Groq Settings ────────────────────────────────────────────────────────────
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL        = "llama3-8b-8192"   # fast & free on Groq

# ── Proposal Settings ────────────────────────────────────────────────────────
MIN_WORDS = 120
MAX_WORDS = 180
