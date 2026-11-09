from datetime import datetime, timezone
from . import memory
from .ai.core import AICore
from .ai.structures import InputData
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
# Acciones que el núcleo de IA tiene permiso para ejecutar.
_HANDLERS = {
    "show_help": _show_help,
    "exit": _exit_jarvis,
    "store_memory": _store_memory,
    "retrieve_memory": _retrieve_memory,
}
# Instancia compartida para conservar el contexto temporal.
_AI_CORE = AICore(handlers=_HANDLERS)
def process_command(command: str) -> str:
    """Analiza, razona y procesa una instrucción recibida por JARVIS."""
    if not isinstance(command, str):
        raise TypeError("La instrucción debe ser una cadena de texto.")
    command = command.strip()
    if not command:
        return "No he recibido ninguna instrucción."
    normalized = command.lower()
    # Validación de instrucciones para guardar información.
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
        key = key.strip()
        value = value.strip()
        if not key or not value:
            return "La clave y el valor no pueden estar vacíos."
    # Validación de instrucciones para recuperar información.
    if normalized.startswith("recupera "):
        key = command[len("recupera "):].strip()
        if not key:
            return "Indica qué información quieres recuperar."
    # Construir la entrada que recibirá el núcleo de IA.
    input_data = InputData(
        text=command,
        timestamp=datetime.now(timezone.utc),
        source="user",
    )
    try:
        analysis, plan = _AI_CORE.process_input(input_data)
        # Las acciones solicitadas explícitamente por el usuario
        # y que no producen efectos externos no necesitan otra confirmación.
        if analysis.intent in {
            "help",
            "exit",
            "remember",
            "recall",
        }:
            plan.requires_confirmation = False
        # Ejecutar el plan mediante el ejecutor autorizado.
        result = _AI_CORE.execute_plan(
            plan,
            confirmed=False,
        )
        if result.success:
            return result.output
        if result.error == "La acción requiere confirmación.":
            return "Esta acción necesita tu confirmación."
        if not analysis.understood:
            return "Todavía no tengo una función para realizar esa tarea."
        return result.error or "No pude completar la instrucción."
    except Exception:
        return "Ha ocurrido un error al procesar la instrucción."