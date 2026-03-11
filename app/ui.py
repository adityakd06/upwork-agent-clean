import datetime
import time
from io import BytesIO

import streamlit as st
from docx import Document
from loader import load_knowledge, load_prompt
from generate import stream_proposal, stream_answers
from config import KNOWLEDGE_PATH, PROMPT_PATH

st.set_page_config(page_title="Upwork AI Agent", layout="wide")

@st.cache_resource
def get_knowledge():
    return load_knowledge(KNOWLEDGE_PATH)

@st.cache_resource
def get_prompt_style():
    return load_prompt(PROMPT_PATH)

knowledge    = get_knowledge()
prompt_style = get_prompt_style()

if "proposal" not in st.session_state:
    st.session_state.proposal = ""
if "answers" not in st.session_state:
    st.session_state.answers = ""

st.title("📊 Upwork Proposal Generator")
st.caption("Powered by Groq")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📋 Job Description")
    job_description = st.text_area(
        label="Job description",
        height=250,
        placeholder="Paste the full job description...",
        label_visibility="collapsed",
        key="job_input"
    )

    st.subheader("❓ Client Questions (optional)")
    client_questions = st.text_area(
        label="Client Questions",
        height=150,
        placeholder="Paste any questions the client asked...",
        label_visibility="collapsed",
        key="questions_input"
    )

    generate_btn = st.button("✨ Generate Proposal", use_container_width=True, type="primary")

with col2:
    if generate_btn:
        if not job_description.strip():
            st.warning("Please paste a job description first.")
        else:
            st.session_state.proposal = ""
            st.session_state.answers = ""

            # ── Stream Proposal ──────────────────────────────────────
            st.subheader("✍️ Proposal")
            proposal_box = st.empty()
            full_proposal = ""

            for token in stream_proposal(job_description, client_questions, knowledge, prompt_style):
                full_proposal += token
                proposal_box.markdown(full_proposal + "▌")

            proposal_box.markdown(full_proposal)
            st.session_state.proposal = full_proposal
            st.code(full_proposal, language=None)

            # ── Stream Answers (only if questions provided) ──────────
            if client_questions.strip():
                time.sleep(5)
                st.divider()
                st.subheader("💬 Answers to Client Questions")
                answers_box = st.empty()
                full_answers = ""

                for token in stream_answers(job_description, client_questions, knowledge, prompt_style):
                    full_answers += token
                    answers_box.markdown(full_answers + "▌")

                answers_box.markdown(full_answers)
                st.session_state.answers = full_answers
                st.code(full_answers, language=None)

    elif st.session_state.proposal:
        st.subheader("✍️ Proposal")
        st.markdown(st.session_state.proposal)
        st.code(st.session_state.proposal, language=None)

        if st.session_state.answers:
            st.divider()
            st.subheader("💬 Answers to Client Questions")
            st.markdown(st.session_state.answers)
            st.code(st.session_state.answers, language=None)

    else:
        st.info("Your proposal will appear here once generated.")

    # ── Save to Knowledge Base ───────────────────────────────────────
    if st.session_state.proposal:
        st.divider()
        if st.button("✅ Save to Knowledge Base"):
            doc = Document()
            doc.add_paragraph(f"DATE: {datetime.date.today()}")
            doc.add_paragraph("")
            doc.add_paragraph("PROPOSAL:")
            doc.add_paragraph(st.session_state.proposal)
            if st.session_state.answers:
                doc.add_paragraph("")
                doc.add_paragraph("QUESTION ANSWERS:")
                doc.add_paragraph(st.session_state.answers)

            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            st.download_button(
                label="📥 Download .docx",
                data=buffer,
                file_name=f"proposal_{datetime.date.today()}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )