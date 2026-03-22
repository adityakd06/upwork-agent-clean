from llm_client import query_llm, stream_llm
from config import MIN_WORDS, MAX_WORDS
from rag import build_index, retrieve


def _remove_most_sentences(text: str) -> str:
    """Remove any sentence that starts with the word 'Most'."""
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text)
    cleaned = [s for s in sentences if not s.strip().startswith("Most")]
    return " ".join(cleaned)


def _build_prompt(job_text: str, client_questions: str, knowledge: str, prompt_style: str) -> str:
    index, chunks = build_index(knowledge)
    relevant_knowledge = retrieve(job_text, index, chunks)

    return f"""You are writing an Upwork proposal on behalf of a senior freelance data analyst with 7+ years of experience on Upwork.

STRICT RULES — follow these or the output is wrong:
- ONLY use information from the PAST WORK section below. Do NOT invent projects, clients, numbers, or tools that are not mentioned there.
- If you don't have a relevant past example, say "I've worked on similar data challenges" — never fabricate specifics.
- Do NOT use bullet points. Write in short paragraphs only.
- Do NOT add a subject line, title, or any preamble. Start the proposal directly.
- Keep it strictly between {MIN_WORDS} and {MAX_WORDS} words.
- IMPORTANT: Before writing anything, scan the job description for any special instructions like writing a specific word or phrase at the top (e.g. "write Banana at the top"). If found, place that exact word or phrase on the very first line.
- Do NOT copy any name, signature, or sign-off from the PAST WORK section.
- Always sign off with "Warm regards, Sagar" at the end of the closure paragraph.
- Always reference specific tools, platforms, and deliverables mentioned in the job description. Never write a generic proposal.
- Always start with "Hey," or "Hi there,". NEVER use a client's name unless the user explicitly provides it separately. Do not guess or extract names from the job description.
- The FIRST WORD of the proposal must be "Hey," or "Hi there," — no exceptions. If the output does not start with "Hey" or "Hi there", it is wrong.
- If you catch yourself writing "Most [profession]" or "Most [company type]" — stop and rewrite that sentence completely.

--- PAST WORK & WRITING STYLE (only use what's here) ---
{relevant_knowledge}

--- BEHAVIOURAL INSTRUCTIONS ---
{prompt_style}

--- PROPOSAL FORMAT TO FOLLOW ---

PARAGRAPH 1 — HOOK:
One or two punchy lines that show you immediately understand the client's core problem. Make it specific to their job, not generic.

PARAGRAPH 2 — BODY:
Show you've solved this exact type of problem before. Mention only tools and skills relevant to THIS job description. Briefly explain your approach without giving everything away.

PARAGRAPH 3 — CLOSURE:
Warm, confident call to action. Ask when they're free for a quick call. Keep it human, not salesy. End with "Warm regards, Sagar".

--- JOB DESCRIPTION ---
{job_text}
"""


def stream_proposal(job_text: str, client_questions: str, knowledge: str, prompt_style: str):
    """Streams the proposal only — no question answers."""
    prompt = _build_prompt(job_text, client_questions, knowledge, prompt_style)
    yield from stream_llm(prompt)


def stream_answers(job_text: str, client_questions: str, knowledge: str, prompt_style: str):
    """Separate stream just for answering client questions."""
    index, chunks = build_index(knowledge)
    relevant_knowledge = retrieve(job_text, index, chunks)

    prompt = f"""You are a senior freelance data analyst with 7+ years of experience on Upwork.

--- PAST WORK & EXPERIENCE (use this as reference) ---
{relevant_knowledge}

STRICT RULES:
- Answer each question directly and honestly.
- Each answer should be 3-5 sentences.
- Draw from the PAST WORK section above where relevant.
- Do NOT be vague or say "we can discuss later."
- Do NOT add any preamble — just answer each question numbered.
- Do NOT sign off with a name or closing.
- Never fabricate projects, tools, or numbers not mentioned in PAST WORK.
- NEVER use sentences like "Most [profession] can do X, but few can do Y" or any variation of this pattern anywhere in the proposal. This is cliché and unprofessional.
- NEVER use the phrase "Most Power BI developers" or "Most [any profession]" anywhere.
- The hook must directly address the client's specific problem in the first line, not make a generic industry observation.
- The hook must be direct and specific to the client's problem, not a generic industry observation.

--- JOB CONTEXT ---
{job_text}

--- QUESTIONS TO ANSWER ---
{client_questions}
"""
    yield from stream_llm(prompt)


def generate_proposal(job_text: str, client_questions: str, knowledge: str, prompt_style: str) -> str:
    """Blocking call — used by CLI."""
    prompt = _build_prompt(job_text, client_questions, knowledge, prompt_style)
    return query_llm(prompt)