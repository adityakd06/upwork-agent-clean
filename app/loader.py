import os
from docx import Document


def _extract_text(path: str) -> str:
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def load_knowledge(folder_path: str) -> str:
    """Reads ALL .docx files in the knowledge_base folder and combines them."""
    all_text = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".docx"):
            full_path = os.path.join(folder_path, filename)
            all_text.append(_extract_text(full_path))
    return "\n\n".join(all_text)


def load_prompt(path: str) -> str:
    return _extract_text(path)