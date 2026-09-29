import os
from pathlib import Path

def extract_text(path: Path) -> str:
    """
    Extracts text content from recovered document artifacts.
    Handles PDF, DOCX, TXT, MD, CSV files. Gracefully returns empty text if file is corrupted/partial.
    """
    path = Path(path)
    if not path.exists() or not path.is_file():
        return ""

    suffix = path.suffix.lower()
    try:
        if suffix == ".pdf":
            try:
                from pypdf import PdfReader
                reader = PdfReader(str(path))
                pages_text = [page.extract_text() or "" for page in reader.pages]
                return "\n".join(pages_text)
            except Exception:
                return ""
        elif suffix == ".docx":
            try:
                import docx
                doc = docx.Document(str(path))
                return "\n".join(p.text for p in doc.paragraphs)
            except Exception:
                return ""
        elif suffix in (".txt", ".md", ".csv", ".json", ".log", ".rtf", ".xml", ".html"):
            try:
                return path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                return ""
    except Exception:
        return ""
    return ""

def is_image(path: Path) -> bool:
    """Checks whether file is a supported visual image artifact."""
    return Path(path).suffix.lower() in (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tiff")
