import math
from .structures import AnalysisResult, ActionPlan
DEFAULT_MIN_CONFIDENCE = 0.5
def create_action_plan(
    analysis: AnalysisResult,
    min_confidence: float = DEFAULT_MIN_CONFIDENCE,
) -> ActionPlan:
    """Genera un plan solo cuando el análisis tiene confianza suficiente."""
    if not isinstance(analysis, AnalysisResult):
        raise TypeError("Se esperaba un objeto AnalysisResult.")
    if (
        isinstance(min_confidence, bool)
        or not isinstance(min_confidence, (int, float))
        or not math.isfinite(min_confidence)
        or not 0.0 <= min_confidence <= 1.0
    ):
        raise ValueError("La confianza mínima debe estar entre 0 y 1.")
    if (
        isinstance(analysis.confidence, bool)
        or not isinstance(analysis.confidence, (int, float))
        or not math.isfinite(analysis.confidence)
        or not 0.0 <= analysis.confidence <= 1.0
    ):
        raise ValueError("La confianza del análisis debe estar entre 0 y 1.")
    parameters = dict(analysis.entities)
    if not analysis.understood:
        return ActionPlan(
            parameters=parameters,
            requires_confirmation=False,
            reason="No se pudo identificar la intención.",
        )
    if analysis.confidence < min_confidence:
        return ActionPlan(
            parameters=parameters,
            requires_confirmation=False,
            reason=(
                "La confianza del análisis es insuficiente para proponer "
                "una acción."
            ),
        )
    if analysis.intent == "integration":
        integration_name = analysis.entities.get("integration")
        if (
            not isinstance(integration_name, str)
            or not integration_name.strip()
        ):
            return ActionPlan(
                parameters=parameters,
                requires_confirmation=False,
                reason="No se indicó una integración válida.",
            )
        return ActionPlan(
            actions=[integration_name.strip()],
            parameters=parameters,
            reason=(
                "Ejecución solicitada para la integración: "
                f"{integration_name.strip()}."
            ),
        )
    intent_actions = {
        "help": "show_help",
        "exit": "exit",
        "remember": "store_memory",
        "recall": "retrieve_memory",
    }
    action = intent_actions.get(analysis.intent)
    if action is None:
        return ActionPlan(
            parameters=parameters,
            reason="No existe una acción asociada a esta intención.",
        )
    return ActionPlan(
        actions=[action],
        parameters=parameters,
        reason=f"Acción propuesta para la intención: {analysis.intent}.",
    )