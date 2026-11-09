import re
from .language import normalize_text
from .structures import InputData, AnalysisResult
HELP_PHRASES = {
    "ayuda",
    "help",
    "necesito ayuda",
    "puedes ayudarme",
    "que puedes hacer",
    "qué puedes hacer",
}
EXIT_PHRASES = {
    "salir",
    "exit",
    "quit",
    "cerrar jarvis",
    "apagar jarvis",
    "adios",
    "adiós",
}
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
    if normalized_text in HELP_PHRASES:
        return AnalysisResult(
            intent="help",
            confidence=1.0,
            understood=True,
        )
    if normalized_text in EXIT_PHRASES:
        return AnalysisResult(
            intent="exit",
            confidence=1.0,
            understood=True,
        )
    remember_match = re.fullmatch(
        r"recuerda\s+(.+?)\s*:\s*(.+)",
        original_text,
        flags=re.IGNORECASE,
    )
    if remember_match:
        key = remember_match.group(1).strip()
        value = remember_match.group(2).strip()
        if key and value:
            return AnalysisResult(
                intent="remember",
                entities={
                    "key": key,
                    "value": value,
                },
                confidence=1.0,
                understood=True,
            )
    recall_match = re.fullmatch(
        r"recupera\s+(.+)",
        original_text,
        flags=re.IGNORECASE,
    )
    if recall_match:
        key = recall_match.group(1).strip()
        if key:
            return AnalysisResult(
                intent="recall",
                entities={
                    "key": key,
                },
                confidence=1.0,
                understood=True,
            )
    return AnalysisResult(
        intent="unknown",
        confidence=0.0,
        understood=False,
    )