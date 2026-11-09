import re
import unicodedata
def normalize_text(text: str) -> str:
    """Normaliza un texto para facilitar su procesamiento."""
    if not isinstance(text, str):
        raise TypeError("El texto debe ser una cadena.")
    text = text.strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text
def tokenize(text: str) -> list[str]:
    """Divide el texto en palabras y signos de puntuación."""
    normalized = unicodedata.normalize("NFC", normalize_text(text))
    return re.findall(r"[^\W_]+|[^\w\s]", normalized)
def prepare_text(text: str) -> str:
    """Prepara el texto para su posterior análisis."""
    return normalize_text(text)
def normalize_for_matching(text: str) -> str:
    """Normaliza texto para comparar expresiones ignorando tildes."""
    normalized = normalize_text(text)
    replacements = str.maketrans({
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ü": "u",
    })
    return normalized.translate(replacements)