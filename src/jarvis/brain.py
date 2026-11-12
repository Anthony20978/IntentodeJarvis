from datetime import datetime, timezone
from collections.abc import Callable
from . import memory
from .ai.core import AICore
from .ai.integrations import IntegrationRegistry
from .ai.structures import InputData,ActionPlan
IntegrationHandler = Callable[[dict], str]
def _save_memory(key: str, value: str) -> str:
    """Guarda información en la memoria persistente."""
    with memory.MemoryStore(memory.DATABASE_PATH) as store:
        store.remember(key, value)
    return f"He guardado: {key}."
def _get_memory(key: str) -> str:
    """Recupera información de la memoria persistente."""
    with memory.MemoryStore(memory.DATABASE_PATH) as store:
        result = store.recall(key)
    if result is None:
        return "No encuentro esa información en mi memoria."
    return result
def _show_help(parameters: dict) -> str:
    """Devuelve los comandos disponibles."""
    return (
        "Comandos disponibles:\n"
        "- recuerda clave: valor\n"
        "- recupera clave\n"
        "- ayuda\n"
        "- salir"
    )
def _exit_jarvis(parameters: dict) -> str:
    """Responde a una solicitud de salida."""
    return "Hasta pronto."
def _store_memory(parameters: dict) -> str:
    """Ejecuta la acción de guardar un recuerdo."""
    key = parameters.get("key")
    value = parameters.get("value")
    if not isinstance(key, str) or not isinstance(value, str):
        raise ValueError("Faltan los datos necesarios para guardar el recuerdo.")
    return _save_memory(key, value)
def _retrieve_memory(parameters: dict) -> str:
    """Ejecuta la acción de recuperar un recuerdo."""
    key = parameters.get("key")
    if not isinstance(key, str) or not key.strip():
        raise ValueError("No se indicó qué recuerdo recuperar.")
    return _get_memory(key)
# Registro central de las funciones que JARVIS puede ejecutar.
_INTEGRATIONS = IntegrationRegistry({
    "show_help": _show_help,
    "exit": _exit_jarvis,
    "store_memory": _store_memory,
    "retrieve_memory": _retrieve_memory,
    })
_AI_CORE = AICore(handlers=_INTEGRATIONS.get_handlers())
_PENDING_PLAN: ActionPlan | None = None
_PENDING_ACTION_INDEX = 0
def _sync_integrations() -> None:
    """Actualiza los manejadores disponibles para el núcleo de IA."""
    _AI_CORE._handlers = _INTEGRATIONS.get_handlers()
def register_integration(
    name: str,
    handler: IntegrationHandler,
    *,
    replace: bool = False,
) -> None:
    """Registra una función nueva que podrá ejecutar un plan de IA."""
    _INTEGRATIONS.register(name, handler, replace=replace)
    _sync_integrations()
def unregister_integration(name: str) -> bool:
    """Elimina una función registrada y actualiza el núcleo de IA."""
    removed = _INTEGRATIONS.unregister(name)
    if removed:
        _sync_integrations()
    return removed
def get_integrations() -> dict[str, IntegrationHandler]:
    """Devuelve una copia de las funciones disponibles."""
    return _INTEGRATIONS.get_handlers()
def process_command(command: str) -> str:
    """Analiza, razona y procesa una instrucción recibida por JARVIS."""
    global _PENDING_PLAN, _PENDING_ACTION_INDEX
    if not isinstance(command, str):
        raise TypeError("La instrucción debe ser una cadena de texto.")
    command = command.strip()
    # Resolver primero cualquier autorización pendiente.
    if _PENDING_PLAN is not None:
        return _handle_pending_confirmation(command)
    if not command:
        return "No he recibido ninguna instrucción."
    normalized = command.lower()
    if normalized.startswith("recuerda "):
        content = command[len("recuerda "):].strip()
        if not content:
            return "¿Qué información quieres que recuerde?"
        if ":" not in content:
            return (
                "Indica la información con este formato: "
                "recuerda clave: valor"
            )
        key, value = content.split(":", 1)
        if not key.strip() or not value.strip():
            return "La clave y el valor no pueden estar vacíos."
    if normalized.startswith("recupera "):
        key = command[len("recupera "):].strip()
        if not key:
            return "Indica qué información quieres recuperar."
    input_data = InputData(
        text=command,
        timestamp=datetime.now(timezone.utc),
        source="user",
    )
    try:
        analysis, plan = _AI_CORE.process_input(input_data)
        # Estas operaciones no requieren confirmación.
        if analysis.intent in {"help", "exit", "recall"}:
            plan.requires_confirmation = False
        if not analysis.understood:
            return "Todavía no tengo una función para realizar esa tarea."
        if not plan.actions:
            return plan.reason or "No pude generar un plan de ejecución."
        # Las acciones que requieren autorización quedan pendientes.
        if plan.requires_confirmation:
            _PENDING_PLAN = plan
            _PENDING_ACTION_INDEX = 0
            return _format_action_plan(plan)
        result = _AI_CORE.execute_plan(
            plan,
            confirmed=False,
        )
        if result.success:
            return result.output
        return result.error or "No pude completar la instrucción."
    except Exception:
        _PENDING_PLAN = None
        _PENDING_ACTION_INDEX = 0
        return "Ha ocurrido un error al procesar la instrucción."
def _format_action_plan(plan: ActionPlan) -> str:
    """Presenta el plan y sus opciones de autorización."""
    lines = [
        "He preparado el siguiente plan:",
        "",
        "PLAN DE EJECUCIÓN:",
    ]
    for index, action in enumerate(plan.actions, start=1):
        lines.append(f"{index}. {action}")
        for key, value in plan.parameters.items():
            lines.append(f"   {key} = {value}")
    if plan.reason:
        lines.extend(("", f"Motivo: {plan.reason}"))
    lines.extend((
        "",
        "¿Cómo deseas continuar?",
        "S = Ejecutar solamente la siguiente acción",
        "O = Autorizar todas las acciones restantes",
        "N = Cancelar las acciones restantes",
    ))
    return "\n".join(lines)
def _format_next_action(plan: ActionPlan, index: int) -> str:
    """Presenta la siguiente acción que requiere autorización."""
    action = plan.actions[index]
    lines = [
        f"Siguiente acción ({index + 1}/{len(plan.actions)}):",
        f"Acción: {action}",
    ]
    for key, value in plan.parameters.items():
        lines.append(f"   {key} = {value}")
    lines.extend((
        "",
        "S = Ejecutar esta acción",
        "O = Autorizar todas las acciones restantes",
        "N = Cancelar las acciones restantes",
    ))
    return "\n".join(lines)
def _execute_pending_actions(
    start: int,
    all_remaining: bool,
) -> str:
    """Ejecuta las acciones autorizadas mediante AICore."""
    global _PENDING_PLAN, _PENDING_ACTION_INDEX
    plan = _PENDING_PLAN
    stop = len(plan.actions) if all_remaining else start + 1
    outputs = []
    for action in plan.actions[start:stop]:
        single_plan = ActionPlan(
            actions=[action],
            parameters=dict(plan.parameters),
            requires_confirmation=True,
            reason=plan.reason,
        )
        try:
            result = _AI_CORE.execute_plan(
                single_plan,
                confirmed=True,
            )
        except Exception as error:
            _PENDING_PLAN = None
            _PENDING_ACTION_INDEX = 0
            return f"Error al ejecutar {action}: {error}"
        if not result.success:
            _PENDING_PLAN = None
            _PENDING_ACTION_INDEX = 0
            return result.error or f"No se pudo ejecutar: {action}."
        if result.output:
            outputs.append(result.output)
    _PENDING_ACTION_INDEX = stop
    if stop >= len(plan.actions):
        _PENDING_PLAN = None
        _PENDING_ACTION_INDEX = 0
        return (
            "Plan autorizado. Todas las acciones se ejecutaron correctamente.\n"
            + "\n".join(outputs)
        )
    next_action = _format_next_action(plan, stop)
    return (
        "Acción ejecutada correctamente.\n"
        + "\n".join(outputs)
        + "\n\n"
        + next_action
    )
def _handle_pending_confirmation(command: str) -> str:
    """Procesa las respuestas de autorización del usuario."""
    global _PENDING_PLAN, _PENDING_ACTION_INDEX
    answer = command.strip().casefold()
    if answer == "s":
        return _execute_pending_actions(
            _PENDING_ACTION_INDEX,
            all_remaining=False,
        )
    if answer == "o":
        return _execute_pending_actions(
            _PENDING_ACTION_INDEX,
            all_remaining=True,
        )
    if answer == "n":
        _PENDING_PLAN = None
        _PENDING_ACTION_INDEX = 0
        return "Plan cancelado. No se ejecutarán más acciones."
    return (
        "Respuesta no válida. Escribe S para ejecutar la siguiente acción, "
        "O para autorizar todas las restantes o N para cancelar."
    )