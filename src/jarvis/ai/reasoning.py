from .structures import AnalysisResult, ActionPlan
def create_action_plan(analysis: AnalysisResult) -> ActionPlan:
    """Genera un plan a partir del resultado del análisis."""
    if not isinstance(analysis, AnalysisResult):
        raise TypeError("Se esperaba un objeto AnalysisResult.")
    if not analysis.understood:
        return ActionPlan(
            reason="No se pudo identificar la intención.",
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
            reason="No existe una acción asociada a esta intención.",
        )
    return ActionPlan(
        actions=[action],
        parameters=dict(analysis.entities),
        reason=f"Acción propuesta para la intención: {analysis.intent}.",
    )