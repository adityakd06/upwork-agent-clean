import streamlit as st
from app.loader import load_knowledge, load_prompt
from app.generate import stream_proposal
from app.config import KNOWLEDGE_PATH, PROMPT_PATH, OUTPUT_PATH

st.set_page_config(page_title="Upwork AI Agent", layout="wide")

@st.cache_resource
def get_knowledge():
    return load_knowledge(KNOWLEDGE_PATH)

@st.cache_resource
def get_prompt_style():
    return load_prompt(PROMPT_PATH)

knowledge    = get_knowledge()
prompt_style = get_prompt_style()

# ── Keep proposal alive across reruns ────────────────────────────────────────
if "proposal" not in st.session_state:
    st.session_state.proposal = ""

# ── UI ───────────────────────────────────────────────────────────────────────
st.title("📊 Upwork Proposal Generator")
st.caption("Powered by your local LLM via Ollama")

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

            try:
                with open(OUTPUT_PATH, "a", encoding="utf-8") as f:
                    f.write("\n\n-----------------------------\n")
                    f.write(full_proposal)
                st.success("✅ Saved to generated_proposals.txt")
            except Exception as e:
                st.error(f"Could not save output: {e}")

            st.code(full_proposal, language=None)

    elif st.session_state.proposal:
        # Restore proposal if page reruns (e.g. user edits the text area)
        output_box.markdown(st.session_state.proposal)
        st.code(st.session_state.proposal, language=None)

    else:
        output_box.info("Your proposal will appear here once generated.")
