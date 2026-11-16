import math
from .structures import Action, ActionPlan, AnalysisBatch, AnalysisResult
DEFAULT_MIN_CONFIDENCE = 0.5
def create_action_plan(analysis: AnalysisResult | AnalysisBatch, min_confidence: float = DEFAULT_MIN_CONFIDENCE) -> ActionPlan:
    """Convierte los análisis comprendidos en acciones ejecutables."""
    if not isinstance(analysis, (AnalysisResult, AnalysisBatch)):
        raise TypeError("Se esperaba un objeto AnalysisResult o AnalysisBatch.")
    if isinstance(min_confidence, bool) or not isinstance(min_confidence, (int, float)) or not math.isfinite(min_confidence) or not 0.0 <= min_confidence <= 1.0:
        raise ValueError("La confianza mínima debe estar entre 0 y 1.")
    results = analysis.results if isinstance(analysis, AnalysisBatch) else [analysis]
    actions, global_parameters, reasons = [], {}, []
    intent_actions = {"help": "show_help", "exit": "exit", "remember": "store_memory", "recall": "retrieve_memory"}
    for result in results:
        if not isinstance(result, AnalysisResult):
            raise TypeError("Todos los resultados deben ser AnalysisResult.")
        if isinstance(result.confidence, bool) or not isinstance(result.confidence, (int, float)) or not math.isfinite(result.confidence) or not 0.0 <= result.confidence <= 1.0:
            raise ValueError("La confianza del análisis debe estar entre 0 y 1.")
        entities = dict(result.entities)
        context = entities.pop("conversation_context", None)
        if isinstance(context, str) and context.strip():
            previous = global_parameters.get("conversation_context", "")
            if context not in previous.split("\n"):
                global_parameters["conversation_context"] = f"{previous}\n{context}".strip()
        if not result.understood:
            continue
        if result.confidence < min_confidence:
            reasons.append("La confianza del análisis es insuficiente.")
            continue
        if result.intent == "integration":
            action_name = entities.pop("integration", None)
            missing = entities.pop("missing_parameters", [])
            errors = entities.pop("errors", [])
            parameters = entities.pop("parameters", None)
            if errors:
                reasons.extend(str(error) for error in errors)
                continue
            if missing:
                reasons.append("Faltan parámetros obligatorios: " + ", ".join(missing) + ".")
                continue
            if not isinstance(action_name, str) or not action_name.strip():
                reasons.append("La integración no tiene un nombre válido.")
                continue
            if parameters is not None and not isinstance(parameters, dict):
                reasons.append("Los parámetros de la integración no son válidos.")
                continue
            action_parameters = parameters if parameters is not None else entities
        else:
            action_name = intent_actions.get(result.intent)
            if action_name is None:
                continue
            action_parameters = entities
        actions.append(Action(name=action_name.strip(), parameters=action_parameters))
        reasons.append(f"Acción propuesta para la intención: {result.intent}.")
    return ActionPlan(
        actions=actions,
        parameters=global_parameters,
        requires_confirmation=bool(actions),
        reason=" ".join(reasons) or "No se encontraron acciones válidas.",
    )