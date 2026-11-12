import math
from .structures import (
    AnalysisResult,
    AnalysisBatch,
    Action,
    ActionPlan,
)
DEFAULT_MIN_CONFIDENCE = 0.5
def create_action_plan(
    analysis: AnalysisResult | AnalysisBatch,
    min_confidence: float = DEFAULT_MIN_CONFIDENCE,
) -> ActionPlan:
    """Genera un plan con una o varias acciones independientes."""
    if not isinstance(analysis, (AnalysisResult, AnalysisBatch)):
        raise TypeError(
            "Se esperaba un objeto AnalysisResult o AnalysisBatch."
        )
    if (
        isinstance(min_confidence, bool)
        or not isinstance(min_confidence, (int, float))
        or not math.isfinite(min_confidence)
        or not 0.0 <= min_confidence <= 1.0
    ):
        raise ValueError(
            "La confianza mínima debe estar entre 0 y 1."
        )
    results = (
        analysis.results
        if isinstance(analysis, AnalysisBatch)
        else [analysis]
    )
    actions = []
    global_parameters = {}
    reasons = []
    intent_actions = {
        "help": "show_help",
        "exit": "exit",
        "remember": "store_memory",
        "recall": "retrieve_memory",
    }
    for result in results:
        if not isinstance(result, AnalysisResult):
            raise TypeError(
                "Todos los resultados deben ser AnalysisResult."
            )
        if (
            isinstance(result.confidence, bool)
            or not isinstance(result.confidence, (int, float))
            or not math.isfinite(result.confidence)
            or not 0.0 <= result.confidence <= 1.0
        ):
            raise ValueError(
                "La confianza del análisis debe estar entre 0 y 1."
            )
        entities = dict(result.entities)
        # Conservar contexto independientemente de la intención.
        context = entities.pop("conversation_context", None)
        if isinstance(context, str) and context.strip():
            previous_context = global_parameters.get(
                "conversation_context", ""
            )
            if context not in previous_context.split("\n"):
                global_parameters["conversation_context"] = (
                    f"{previous_context}\n{context}".strip()
                )
        # Ignorar intenciones que no fueron comprendidas.
        if not result.understood:
            continue
        # Rechazar análisis con confianza insuficiente.
        if result.confidence < min_confidence:
            reasons.append(
                "La confianza del análisis es insuficiente."
            )
            continue
        if result.intent == "integration":
            action_name = entities.pop("integration", None)
            if (
                not isinstance(action_name, str)
                or not action_name.strip()
            ):
                reasons.append(
                    "La integración no tiene un nombre válido."
                )
                continue
            action_name = action_name.strip()
        else:
            action_name = intent_actions.get(result.intent)
            if action_name is None:
                continue
        # Los parámetros de remember y recall son globales.
        """
        if result.intent in ("remember", "recall"):
            global_parameters.update(entities)
            action_parameters = {}
        else:
            action_parameters = entities
        """
        action_parameters = entities
        actions.append(
            Action(
                name=action_name,
                parameters=action_parameters,
            )
        )
        reasons.append(
            f"Acción propuesta para la intención: {result.intent}."
        )
    if not actions:
        return ActionPlan(
            actions=[],
            parameters=global_parameters,
            requires_confirmation=False,
            reason=(
                " ".join(reasons)
                or "No se encontraron acciones válidas."
            ),
        )
    return ActionPlan(
        actions=actions,
        parameters=global_parameters,
        requires_confirmation=True,
        reason=" ".join(reasons),
    )