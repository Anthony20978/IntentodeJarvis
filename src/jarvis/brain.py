from .memory import get_memory, save_memory
def process_command(command: str) -> str:
    """Procesa una instrucción básica."""
    command = command.strip()
    if not command:
        return "No he recibido ninguna instrucción."
    normalized = command.lower()
    if normalized in ("ayuda", "help"):
        return (
            "Comandos disponibles:\n"
            "- recuerda clave: valor\n"
            "- recupera clave\n"
            "- salir"
        )
    if normalized.startswith("recuerda "):
        content = command[len("recuerda "):].strip()
        if not content:
            return "¿Qué información quieres que recuerde?"
        if ":" not in content:
            return "Indica la información con este formato: recuerda clave: valor"
        key, value = content.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key or not value:
            return "La clave y el valor no pueden estar vacíos."
        save_memory(key, value)
        return f"He guardado: {key}."
    if normalized.startswith("recupera "):
        key = command[len("recupera "):].strip()
        if not key:
            return "Indica qué información quieres recuperar."
        result = get_memory(key)
        if result is None:
            return "No encuentro esa información en mi memoria."
        return result
    return "Todavía no tengo una función para realizar esa tarea."