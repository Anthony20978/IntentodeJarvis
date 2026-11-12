import re
from collections.abc import Mapping
from .language import normalize_text
from .structures import InputData, AnalysisResult, AnalysisBatch
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
# Detecta el inicio de otra instrucción después de "y".
COMMAND_PATTERN = re.compile(
    r"\s+y\s+(?="
    r"recuerda\s+.+?:|"
    r"recupera\s+|"
    r"ejecuta\s+"
    r")",
    flags=re.IGNORECASE,
)
def _format_relevant_context(context, query: str) -> str:
    """Recupera y formatea el contexto relacionado con una consulta."""
    if not callable(getattr(context, "find_relevant", None)):
        raise TypeError(
            "context debe proporcionar find_relevant()."
        )
    relevant = context.find_relevant(
        query,
        limit=5,
        min_score=0.3,
    )
    lines = []
    for data in relevant:
        source = data.source.lower()
        if source == "user":
            label = "Usuario"
        elif source in ("assistant", "jarvis"):
            label = "JARVIS"
        else:
            label = data.source.capitalize()
        lines.append(f"{label}: {data.text}")
    return "\n".join(lines)
def _analyze_single(
    data: InputData,
    context=None,
    available_integrations: Mapping[str, object] | None = None,
) -> AnalysisResult:
    """Analiza una instrucción individual."""
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
    integration_match = re.fullmatch(
        r"(?:ejecuta|execute)\s+(.+)",
        normalized_text,
    )
    if integration_match and available_integrations is not None:
        requested_name = integration_match.group(1).strip()
        registered_names = {
            name.strip().lower(): name
            for name in available_integrations
            if isinstance(name, str) and name.strip()
        }
        integration_name = registered_names.get(requested_name)
        if integration_name is not None:
            return AnalysisResult(
                intent="integration",
                entities={"integration": integration_name},
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
                entities={"key": key},
                confidence=1.0,
                understood=True,
            )
    entities = {}
    if context is not None:
        relevant_context = _format_relevant_context(
            context,
            original_text,
        )
        if relevant_context:
            entities["conversation_context"] = relevant_context
    return AnalysisResult(
        intent="unknown",
        entities=entities,
        confidence=0.0,
        understood=False,
    )
def analyze_input(
    data: InputData,
    context=None,
    available_integrations: Mapping[str, object] | None = None,
) -> AnalysisResult | AnalysisBatch:
    """Analiza una entrada y reconoce una o varias instrucciones."""
    if not isinstance(data, InputData):
        raise TypeError("Se esperaba un objeto InputData.")
    if (
        available_integrations is not None
        and not isinstance(available_integrations, Mapping)
    ):
        raise TypeError("available_integrations debe ser un Mapping.")
    original_text = data.text.strip()
    if not original_text:
        return AnalysisResult(
            intent="unknown",
            understood=False,
        )
    instructions = [
        part.strip()
        for part in COMMAND_PATTERN.split(original_text)
        if part.strip()
    ]
    if len(instructions) == 1:
        return _analyze_single(
            data,
            context,
            available_integrations,
        )
    results = []
    for instruction in instructions:
        individual_input = InputData(
            text=instruction,
            timestamp=data.timestamp,
            source=data.source,
        )
        results.append(
            _analyze_single(
                individual_input,
                context,
                available_integrations,
            )
        )
    return AnalysisBatch(results=results)