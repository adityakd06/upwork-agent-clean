from llm_client import query_llm, stream_llm
from config import MIN_WORDS, MAX_WORDS
from rag import build_index, retrieve


def _build_prompt(job_text: str, knowledge: str, prompt_style: str) -> str:
    index, chunks = build_index(knowledge)
    relevant_knowledge = retrieve(job_text, index, chunks)  # only relevant chunks

#     return f"""You are a senior freelance data analyst with 7+ years of experience on Upwork.


# --- YOUR PAST WORK & WRITING STYLE ---
# {relevant_knowledge}

# --- BEHAVIOURAL INSTRUCTIONS ---
# {prompt_style}

# --- PROPOSAL STRUCTURE TO FOLLOW ---

# 1. HOOK (first 2 lines):
#    Start with a bold, attention-grabbing opening that speaks directly to the client's problem.
#    Make them feel like you've done this exact thing before. It must and should contain one of these things
#    hi, hello, hey there, 

# 2. BODY:
#    - Clearly state you understand their problem
#    - Mention specific skills and tools relevant to THIS job
#    - Show how you've solved a similar problem before (use past work above as reference)
#    - Briefly explain your approach to solving their specific problem
#    - i do not want this to be generated in points only paragraphs and sentences

# 3. SPECIAL CONDITION:
#    If the job description contains questions like "explain your approach", "how would you solve this",
#    "what are your rates", or "what is your hourly rate" — do NOT answer them directly.
#    Instead say something like: "I'd love to discuss the details once we connect — happy to walk you through my approach then."

# 4. CLOSURE:
#    End with a warm, confident call to action. Ask when they're available to connect,
#    suggest a quick call, and make it easy for them to say yes.

# --- TASK ---
# Write a tailored Upwork proposal following the structure above.
# Keep it {MIN_WORDS}–{MAX_WORDS} words. Be conversational, not robotic.
# Do not add any preamble like "Here is your proposal" — just write the proposal directly.

# --- JOB DESCRIPTION ---
# {job_text}
# """

    return f"""You are writing an Upwork proposal on behalf of a freelance data analyst.

STRICT RULES — follow these or the output is wrong:
-If there is is any mention of giving a wlk through or give a systematic plan in the text itself then just politely say that "we can discuss that during the call or when the proposal is accepted"
- ONLY use information from the PAST WORK section below. Do NOT invent projects, clients, numbers, or tools that are not mentioned there.
- If you don't have a relevant past example, say "I've worked on similar data challenges" — never fabricate specifics.
- Do NOT use bullet points. Write in short paragraphs only.
- Do NOT add a subject line, title, or any preamble. Start the proposal directly.
- Keep it strictly between {MIN_WORDS} and {MAX_WORDS} words.

--- PAST WORK & WRITING STYLE (only use what's here) ---
{relevant_knowledge}

--- BEHAVIOURAL INSTRUCTIONS ---
{prompt_style}

--- PROPOSAL FORMAT TO FOLLOW ---

PARAGRAPH 1 — HOOK:
Star with "Hi, Hello, Hey"One or two punchy lines that show you immediately understand the client's core problem. Make it specific to their job, not generic.

PARAGRAPH 2 — BODY:
Show you've solved this exact type of problem before. Mention only tools and skills that are relevant to THIS job description. Briefly explain your approach without giving everything away.

PARAGRAPH 3 — CONDITION (only include if the job asks about approach, methodology, or rates):
If the job description asks how you would solve it or what your rates are, say something like: "I'd love to walk you through my exact approach once we connect — happy to discuss details then."
If the job does NOT ask this, skip this paragraph entirely.

PARAGRAPH 4 — CLOSURE:
Warm, confident call to action. Ask when they're free for a quick call. Keep it human, not salesy.

REGARDS:always write /n best regards/n sagar "or" /n warm regards/n sagar

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