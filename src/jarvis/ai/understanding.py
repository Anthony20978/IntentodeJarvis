import re
from .language import normalize_text
from .structures import InputData, AnalysisResult
def analyze_input(data: InputData) -> AnalysisResult:
    """Analiza una entrada e identifica su intención."""
    if not isinstance(data, InputData):
        raise TypeError("Se esperaba un objeto InputData.")
    original_text = data.text.strip()
    normalized_text = normalize_text(original_text)
    if not normalized_text:
        return AnalysisResult(
            intent="unknown",
            understood=False,
        )
    # Identificar solicitudes de ayuda.
    if normalized_text == "ayuda":
        return AnalysisResult(
            intent="help",
            confidence=1.0,
            understood=True,
        )
    # Identificar solicitudes para salir.
    if normalized_text == "salir":
        return AnalysisResult(
            intent="exit",
            confidence=1.0,
            understood=True,
        )
    # Identificar solicitudes para guardar información.
    remember_match = re.fullmatch(
        r"recuerda\s+(.+?)\s*:\s*(.+)",
        original_text,
        flags=re.IGNORECASE,
    )
    if remember_match:
        return AnalysisResult(
            intent="remember",
            entities={
                "key": remember_match.group(1).strip(),
                "value": remember_match.group(2).strip(),
            },
            confidence=1.0,
            understood=True,
        )
    # Identificar solicitudes para recuperar información.
    recall_match = re.fullmatch(
        r"recupera\s+(.+)",
        original_text,
        flags=re.IGNORECASE,
    )
    if recall_match:
        return AnalysisResult(
            intent="recall",
            entities={
                "key": recall_match.group(1).strip(),
            },
            confidence=1.0,
            understood=True,
        )
    # No se reconoció ninguna intención.
    return AnalysisResult(
        intent="unknown",
        confidence=0.0,
        understood=False,
    )