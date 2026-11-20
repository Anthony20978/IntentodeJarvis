import re
import shlex
from collections.abc import Mapping
from .language import normalize_text
from .structures import AnalysisBatch, AnalysisResult, InputData, IntegrationDefinition
HELP_PHRASES = {"ayuda", "help", "necesito ayuda", "puedes ayudarme", "que puedes hacer", "qué puedes hacer"}
EXIT_PHRASES = {"salir", "exit", "quit", "cerrar jarvis", "apagar jarvis", "adios", "adiós"}
COMMAND_PATTERN = re.compile(r"\s+y\s+(?=recuerda\s+.+?:|recupera\s+|ejecuta\s+|ejecutar\s+)", re.IGNORECASE)
def _format_relevant_context(context, query: str) -> str:
    if not callable(getattr(context, "find_relevant", None)):
        raise TypeError("context debe proporcionar find_relevant().")
    relevant = context.find_relevant(query, limit=5, min_score=0.3)
    lines = []
    for data in relevant:
        source = data.source.lower()
        label = "Usuario" if source == "user" else "JARVIS" if source in ("assistant", "jarvis") else data.source.capitalize()
        lines.append(f"{label}: {data.text}")
    return "\n".join(lines)
def _convert_parameter(value: str, target_type: type):
    if target_type is bool:
        normalized = normalize_text(value)
        if normalized in {"true", "verdadero", "si", "1"}:
            return True
        if normalized in {"false", "falso", "no", "0"}:
            return False
        raise ValueError("Introduce un valor booleano válido.")
    try:
        return target_type(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"El valor '{value}' debe ser de tipo {target_type.__name__}.") from error
def _parse_integration_parameters(arguments: str, definition: IntegrationDefinition):
    try:
        tokens = shlex.split(arguments)
    except ValueError as error:
        return {}, [], [f"No pude interpretar los parámetros: {error}"]
    by_flag = {parameter.flag: parameter for parameter in definition.parameters}
    parameters, errors = {}, []
    index = 0
    while index < len(tokens):
        flag = tokens[index]
        index += 1
        parameter = by_flag.get(flag)
        if parameter is None:
            errors.append(f"Bandera desconocida: {flag}.")
            continue
        if parameter.name in parameters:
            errors.append(f"La bandera {flag} está repetida.")
            if index < len(tokens) and tokens[index] not in by_flag:
                index += 1
            continue
        if index >= len(tokens) or tokens[index] in by_flag:
            errors.append(f"Falta un valor para la bandera {flag}.")
            continue
        raw_value = tokens[index]
        index += 1
        try:
            parameters[parameter.name] = _convert_parameter(raw_value, parameter.type)
        except ValueError as error:
            errors.append(str(error))
    missing = [p.name for p in definition.parameters if p.required and p.name not in parameters]
    return parameters, missing, errors
def _analyze_single(data: InputData, context=None, available_integrations: Mapping[str, object] | None = None, integration_definitions: Mapping[str, IntegrationDefinition] | None = None) -> AnalysisResult:
    original_text = data.text.strip()
    normalized_text = normalize_text(original_text)
    if not normalized_text:
        return AnalysisResult(intent="unknown", understood=False)
    if normalized_text in HELP_PHRASES:
        return AnalysisResult(intent="help", confidence=1.0, understood=True)
    if normalized_text in EXIT_PHRASES:
        return AnalysisResult(intent="exit", confidence=1.0, understood=True)
    if normalized_text in {
        "clear",
        "limpia la terminal",
        "limpiar la terminal",
        "limpia la pantalla",
        "limpiar pantalla",
    }:
        return AnalysisResult(
            intent="clear",
            confidence=1.0,
            understood=True,
        )
    if normalized_text == "see_integrations" or normalized_text == "ver_integraciones":
        return AnalysisResult(intent="integration", entities={"integration": "see_integrations"}, confidence=1.0, understood=True)
    remember = re.fullmatch(r"recuerda\s+(.+?)\s*:\s*(.+)", original_text, re.IGNORECASE | re.DOTALL)
    if remember:
        return AnalysisResult(intent="remember", entities={"key": remember.group(1).strip(), "value": remember.group(2).strip()}, confidence=1.0, understood=True)
    recall = re.fullmatch(r"recupera\s+(.+)", original_text, re.IGNORECASE | re.DOTALL)
    if recall and recall.group(1).strip():
        return AnalysisResult(intent="recall", entities={"key": recall.group(1).strip()}, confidence=1.0, understood=True)
    match = re.fullmatch(r"(?:ejecuta|ejecutar|execute)\s+(\S+)(?:\s+(.*))?", original_text, re.IGNORECASE | re.DOTALL)
    if match and available_integrations is not None:
        requested_name, arguments = match.group(1), match.group(2) or ""
        registered = {normalize_text(name.strip()): name for name in available_integrations if isinstance(name, str) and name.strip()}
        integration_name = registered.get(normalize_text(requested_name))
        if integration_name is not None:
            definition = integration_definitions.get(integration_name) if integration_definitions is not None else None
            if definition is None:
                return AnalysisResult(intent="integration", entities={"integration": integration_name}, confidence=1.0, understood=True)
            if not isinstance(definition, IntegrationDefinition):
                return AnalysisResult(intent="unknown", understood=False)
            parameters, missing, errors = _parse_integration_parameters(arguments, definition)
            return AnalysisResult(intent="integration", entities={"integration": integration_name, "parameters": parameters, "missing_parameters": missing, "errors": errors}, confidence=1.0, understood=True)
    if context is not None:
        relevant_context = _format_relevant_context(context, original_text)
        if relevant_context:
            return AnalysisResult(intent="unknown", entities={"conversation_context": relevant_context}, confidence=0.3, understood=False)
    return AnalysisResult(intent="unknown", confidence=0.0, understood=False)
def analyze_input(data: InputData, context=None, available_integrations: Mapping[str, object] | None = None, integration_definitions: Mapping[str, IntegrationDefinition] | None = None) -> AnalysisResult | AnalysisBatch:
    if not isinstance(data, InputData):
        raise TypeError("Se esperaba un objeto InputData.")
    if available_integrations is not None and not isinstance(available_integrations, Mapping):
        raise TypeError("available_integrations debe ser un Mapping.")
    if integration_definitions is not None and not isinstance(integration_definitions, Mapping):
        raise TypeError("integration_definitions debe ser un Mapping.")
    original_text = data.text.strip()
    if not original_text:
        return AnalysisResult(intent="unknown", understood=False)
    instructions = [part.strip() for part in COMMAND_PATTERN.split(original_text) if part.strip()]
    if len(instructions) == 1:
        return _analyze_single(data, context, available_integrations, integration_definitions)
    results = []
    for instruction in instructions:
        individual = InputData(text=instruction, timestamp=data.timestamp, source=data.source)
        results.append(_analyze_single(individual, context, available_integrations, integration_definitions))
    return AnalysisBatch(results=results)