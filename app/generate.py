from llm_client import query_llm, stream_llm
from config import MIN_WORDS, MAX_WORDS
from rag import build_index, retrieve


def _build_prompt(job_text: str, knowledge: str, prompt_style: str) -> str:
    index, chunks = build_index(knowledge)
    relevant_knowledge = retrieve(job_text, index, chunks)  # only relevant chunks

    return f"""You are a senior freelance data analyst with 7+ years of experience on Upwork.


--- YOUR PAST WORK & WRITING STYLE ---
{relevant_knowledge}

--- BEHAVIOURAL INSTRUCTIONS ---
{prompt_style}

--- PROPOSAL STRUCTURE TO FOLLOW ---

1. HOOK (first 2 lines):
   Start with a bold, attention-grabbing opening that speaks directly to the client's problem.
   Make them feel like you've done this exact thing before.

2. BODY:
   - Clearly state you understand their problem
   - Mention specific skills and tools relevant to THIS job
   - Show how you've solved a similar problem before (use past work above as reference)
   - Briefly explain your approach to solving their specific problem

3. SPECIAL CONDITION:
   If the job description contains questions like "explain your approach", "how would you solve this",
   "what are your rates", or "what is your hourly rate" — do NOT answer them directly.
   Instead say something like: "I'd love to discuss the details once we connect — happy to walk you through my approach then."

4. CLOSURE:
   End with a warm, confident call to action. Ask when they're available to connect,
   suggest a quick call, and make it easy for them to say yes.

--- TASK ---
Write a tailored Upwork proposal following the structure above.
Keep it {MIN_WORDS}–{MAX_WORDS} words. Be conversational, not robotic.
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