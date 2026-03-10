import os
import datetime
from io import BytesIO

import streamlit as st
from docx import Document
from loader import load_knowledge, load_prompt
from generate import stream_proposal
from config import KNOWLEDGE_PATH, PROMPT_PATH, OUTPUT_PATH

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

st.title("📊 Upwork Proposal Generator")
st.caption("Powered by Groq")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📋 Job Description")
    job_description = st.text_area(
        label="Job description",
        height=350,
        placeholder="Paste the full job description...",
        label_visibility="collapsed",
    )
    generate_btn = st.button("✨ Generate Proposal", use_container_width=True, type="primary")

with col2:
    st.subheader("✍️ Generated Proposal")
    output_box = st.empty()

    if generate_btn:
        if not job_description.strip():
            st.warning("Please paste a job description first.")
        else:
            st.session_state.proposal = ""
            full_proposal = ""

            for token in stream_proposal(job_description, knowledge, prompt_style):
                full_proposal += token
                output_box.markdown(full_proposal + "▌")

            st.session_state.proposal = full_proposal
            output_box.markdown(full_proposal)
            st.code(full_proposal, language=None)

    if st.session_state.proposal:
        output_box.markdown(st.session_state.proposal)

        if st.button("✅ Save to Knowledge Base"):
            doc = Document()
            doc.add_paragraph("")
            doc.add_paragraph("PROPOSAL:")
            doc.add_paragraph(st.session_state.proposal)

            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            st.download_button(
                label="📥 Download .docx",
                data=buffer,
                file_name=f"proposal_{datetime.date.today()}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
    else:
        output_box.info("Your proposal will appear here once generated.")