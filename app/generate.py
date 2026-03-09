from app.llm_client import query_llm, stream_llm
from app.config import MIN_WORDS, MAX_WORDS


def _build_prompt(job_text: str, knowledge: str, prompt_style: str) -> str:
    return f"""You are a senior freelance data analyst with 7+ years of experience.

--- YOUR WRITING STYLE & PAST WORK ---
{knowledge}

--- BEHAVIOURAL INSTRUCTIONS ---
{prompt_style}

--- TASK ---
Write a tailored Upwork proposal for the job description below.
Keep it {MIN_WORDS}–{MAX_WORDS} words. Focus on solving the client's business problem.
Do not add any preamble like "Here is your proposal" — just write the proposal directly.

--- JOB DESCRIPTION ---
{job_text}
"""


def generate_proposal(job_text: str, knowledge: str, prompt_style: str) -> str:
    """Returns the full proposal as a string (blocking). Used by CLI."""
    prompt = _build_prompt(job_text, knowledge, prompt_style)
    return query_llm(prompt)


def stream_proposal(job_text: str, knowledge: str, prompt_style: str):
    """Yields proposal tokens one by one (streaming). Used by Streamlit UI."""
    prompt = _build_prompt(job_text, knowledge, prompt_style)
    yield from stream_llm(prompt)
