import os
import sys

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.loader import load_knowledge, load_prompt
from app.generate import generate_proposal
from app.config import KNOWLEDGE_PATH, PROMPT_PATH, OUTPUT_PATH


def main():
    # For CLI usage, load API key from environment variable
    if not os.getenv("GROQ_API_KEY"):
        print("ERROR: Set your GROQ_API_KEY environment variable first.")
        print("  Windows:  $env:GROQ_API_KEY='your_key_here'")
        print("  Mac/Linux: export GROQ_API_KEY='your_key_here'")
        sys.exit(1)

    print("Loading knowledge base and prompts...")
    knowledge    = load_knowledge(KNOWLEDGE_PATH)
    prompt_style = load_prompt(PROMPT_PATH)

    job = input("\nPaste Job Description:\n> ")
    if not job.strip():
        print("No job description provided. Exiting.")
        return

    print("\nGenerating proposal via Groq...\n")
    proposal = generate_proposal(job, knowledge, prompt_style)

    print("===== GENERATED PROPOSAL =====\n")
    print(proposal)

    try:
        with open(OUTPUT_PATH, "a", encoding="utf-8") as f:
            f.write("\n\n-----------------------------\n")
            f.write(proposal)
        print("\n[Saved to generated_proposals.txt]")
    except Exception as e:
        print(f"\n[Warning] Could not save output: {e}")


if __name__ == "__main__":
    main()
