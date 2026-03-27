import json
from llm_client import query_llm, stream_llm
from config import MIN_WORDS, MAX_WORDS
from rag import build_index, retrieve


def _build_prompt(job_text: str, client_questions: str, knowledge: str, prompt_style: str) -> str:
    index, chunks = build_index(knowledge)
    relevant_knowledge = retrieve(job_text, index, chunks)

    return f"""You are writing an Upwork proposal on behalf of a senior freelance data analyst with 7+ years of experience on Upwork.

STRICT RULES — follow these or the output is wrong:
- ONLY use information from the PAST WORK section below. Do NOT invent projects, clients, numbers, or tools not mentioned there.
- If you don't have a relevant past example, say "I've worked on similar data challenges" — never fabricate specifics.
- Do NOT use bullet points. Write in short paragraphs only.
- Do NOT add a subject line, title, or any preamble. Start the proposal directly.
- Keep it strictly between {MIN_WORDS} and {MAX_WORDS} words.
- Before writing, scan the job description for special instructions like writing a specific word at the top. If found, place it on the very first line.
- Do NOT copy any name, signature, or sign-off from the PAST WORK section.
- Always sign off with "Warm regards, Sagar" at the end.
- Always reference specific tools and platforms mentioned in the job description. Never write a generic proposal.
- The FIRST WORD must be "Hey," or "Hi there," — no exceptions.
- NEVER start any sentence with the word "Most".
- NEVER use a client's name unless explicitly provided. Do not guess names from the job description.

--- PAST WORK & WRITING STYLE (only use what's here) ---
{relevant_knowledge}

--- BEHAVIOURAL INSTRUCTIONS ---
{prompt_style}

--- PROPOSAL FORMAT TO FOLLOW ---

PARAGRAPH 1 — HOOK:
One or two punchy lines showing you immediately understand the client's core problem. Specific to their job, not generic.

PARAGRAPH 2 — BODY:
Show you've solved this exact type of problem before. Mention only relevant tools and skills. Briefly explain your approach.

PARAGRAPH 3 — CLOSURE:
Warm, confident call to action. Ask when they're free for a quick call. End with "Warm regards, Sagar".

--- JOB DESCRIPTION ---
{job_text}
"""


def stream_proposal(job_text: str, client_questions: str, knowledge: str, prompt_style: str):
    """Streams the proposal only."""
    prompt = _build_prompt(job_text, client_questions, knowledge, prompt_style)
    yield from stream_llm(prompt)


def stream_answers(job_text: str, client_questions: str, knowledge: str, prompt_style: str):
    """Separate stream for answering client questions."""
    index, chunks = build_index(knowledge)
    relevant_knowledge = retrieve(job_text, index, chunks)

    prompt = f"""You are a senior freelance data analyst with 7+ years of experience on Upwork.

--- PAST WORK & EXPERIENCE ---
{relevant_knowledge}

STRICT RULES:
- Answer each question directly and honestly in 3-5 sentences.
- Draw from PAST WORK where relevant. Never fabricate.
- Do NOT add any preamble. Answer each question numbered.
- Do NOT sign off with a name or closing.
- Do not say "we can discuss later" — answer properly.
- Answer each question in one cohesive paragraph, not split into sub-points.

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


def extract_job_details(job_text: str) -> dict:
    """Extract structured job details from the pasted job page."""
    prompt = f"""Extract the following fields from the job description below.
Respond ONLY in JSON format with these exact keys, no extra text:
{{
  "title": "job title here",
  "budget": "e.g. $45/hr or $3500 fixed or Not specified",
  "duration": "e.g. 1-3 months or Ongoing or Not specified",
  "connects": "number only e.g. 6, or Not specified"
}}

JOB DESCRIPTION:
{job_text}
"""
    result = query_llm(prompt)
    try:
        clean = result.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except Exception:
        return {"title": "Unknown", "budget": "Unknown", "duration": "Unknown", "connects": "Unknown"}