from collections.abc import Callable, Mapping
from .structures import Action, ActionPlan, ExecutionResult
ActionHandler = Callable[[dict], str]
def execute_action_plan(
    plan: ActionPlan,
    handlers: Mapping[str, ActionHandler],
    confirmed: bool = False,
) -> ExecutionResult:
    """Valida y ejecuta las acciones autorizadas de un plan."""
    if not isinstance(plan, ActionPlan):
        raise TypeError("Se esperaba un objeto ActionPlan.")
    if not isinstance(confirmed, bool):
        raise TypeError("confirmed debe ser un valor booleano.")
    if not plan.actions:
        return ExecutionResult(
            success=False,
            error="El plan no contiene acciones.",
        )
    if plan.requires_confirmation and not confirmed:
        return ExecutionResult(
            success=False,
            error="La acción requiere confirmación.",
        )
    outputs = []
    for action in plan.actions:
        if not isinstance(action, Action):
            return ExecutionResult(
                success=False,
                error="El plan contiene una acción inválida.",
            )
        handler = handlers.get(action.name)
        if handler is None:
            return ExecutionResult(
                success=False,
                error=f"Acción no disponible: {action.name}.",
            )
        try:
            output = handler(dict(action.parameters))
        except Exception as error:
            return ExecutionResult(
                success=False,
                error=f"Error al ejecutar {action.name}: {error}",
            )
        outputs.append(str(output))
    return ExecutionResult(
        success=True,
        output="\n".join(outputs),
    )