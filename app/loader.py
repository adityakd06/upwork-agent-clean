from docx import Document


def _extract_text(path: str) -> str:
    """Read a .docx file and return all non-empty paragraphs as a single string."""
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def load_knowledge(path: str) -> str:
    return _extract_text(path)


def load_prompt(path: str) -> str:
    return _extract_text(path)
