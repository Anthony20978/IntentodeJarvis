from datetime import datetime, timezone
from collections.abc import Callable
from . import memory
from .ai.core import AICore
from .ai.integrations_registry import IntegrationRegistry
from .ai.structures import (
    InputData,
    Action,
    ActionPlan,
    AnalysisResult,
    AnalysisBatch,
)
from .plan_store import PlanStore
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
        "- salir\n"
        "- ver integraciones\n"
        "- ver planes\n"
        "- editar_plan [nombre]\n"
        "- eliminar_plan [nombre]\n"
        "- ejecutar_plan [nombre]\n"
        "- G o Guardar: guardar el plan pendiente"
    )
def _exit_jarvis(parameters: dict) -> str:
    """Responde a una solicitud de salida."""
    return "Hasta pronto."
def _store_memory(parameters: dict) -> str:
    """Ejecuta la acción de guardar un recuerdo."""
    key = parameters.get("key")
    value = parameters.get("value")
    if not isinstance(key, str) or not isinstance(value, str):
        raise ValueError(
            "Faltan los datos necesarios para guardar el recuerdo."
        )
    return _save_memory(key, value)
def _retrieve_memory(parameters: dict) -> str:
    """Ejecuta la acción de recuperar un recuerdo."""
    key = parameters.get("key")
    if not isinstance(key, str) or not key.strip():
        raise ValueError("No se indicó qué recuerdo recuperar.")
    return _get_memory(key)
def _see_copy(parameters: dict) -> str:
    """Muestra las integraciones externas y sus metadatos."""
    builtin_commands = {
        "show_help",
        "exit",
        "store_memory",
        "retrieve_memory",
        "see_integrations",
    }
    handlers = _INTEGRATIONS.get_handlers()
    integrations = [
        name for name in handlers
        if name not in builtin_commands
    ]
    if not integrations:
        return "No hay integraciones externas disponibles."
    lines = ["Integraciones disponibles:"]
    for name in sorted(integrations):
        definition = _INTEGRATIONS.get_definition(name)
        if definition.visible:
            lines.append(f"\n- {name}")
            if definition is None:
                lines.append("  Sin metadatos disponibles.")
                continue
            lines.append(f"  Descripción: {definition.description}")
            lines.append(f"  Versión: {definition.version}")
            if definition.parameters:
                lines.append("  Parámetros:")
                for parameter in definition.parameters:
                    required = (
                        "obligatorio"
                        if parameter.required
                        else "opcional"
                    )
                    lines.append(
                        f"    - {parameter.name} "
                        f"({parameter.type.__name__}, {required}): "
                        f"{parameter.description}"
                        f"Bandera: {parameter.flag}"
                    )
            else:
                lines.append("  Sin parámetros.")
    return "\n".join(lines)
# Registro central de las funciones que JARVIS puede ejecutar.
_INTEGRATIONS = IntegrationRegistry({
    "show_help": _show_help,
    "exit": _exit_jarvis,
    "store_memory": _store_memory,
    "retrieve_memory": _retrieve_memory,
    "see_integrations": _see_copy,
})
_AI_CORE = AICore(handlers=_INTEGRATIONS.get_handlers(), integration_definitions=_INTEGRATIONS.get_definitions())
_PENDING_PLAN: ActionPlan | None = None
_PENDING_INTEGRATION: dict | None = None
_PENDING_ACTION_INDEX = 0
# Operaciones pendientes relacionadas con los planes guardados.
_PENDING_OPERATION: dict | None = None
def _sync_integrations() -> None:
    """Actualiza los manejadores disponibles para el núcleo de IA."""
    _AI_CORE._handlers = _INTEGRATIONS.get_handlers()
    _AI_CORE._integration_definitions = _INTEGRATIONS.get_definitions()
def register_integration(
    name: str,
    handler: IntegrationHandler,
    *,
    replace: bool = False,
) -> None:
    """Registra una integración."""
    _INTEGRATIONS.register(name, handler, replace=replace)
    _sync_integrations()
def unregister_integration(name: str) -> bool:
    """Elimina una integración y actualiza el núcleo de IA."""
    removed = _INTEGRATIONS.unregister(name)
    if removed:
        _sync_integrations()
    return removed
def get_integrations() -> dict[str, IntegrationHandler]:
    """Devuelve una copia de las funciones disponibles."""
    return _INTEGRATIONS.get_handlers()
def _has_understood_instruction(
    analysis: AnalysisResult | AnalysisBatch,
) -> bool:
    """Comprueba si alguna instrucción fue comprendida."""
    results = (
        analysis.results
        if isinstance(analysis, AnalysisBatch)
        else [analysis]
    )
    return any(result.understood for result in results)
def _requires_confirmation(
    analysis: AnalysisResult | AnalysisBatch,
) -> bool:
    """Determina si alguna instrucción requiere autorización."""
    results = (
        analysis.results
        if isinstance(analysis, AnalysisBatch)
        else [analysis]
    )
    safe_intents = {
        "help",
        "exit",
        "recall",
        "see_integrations",
    }
    return any(
        result.understood
        and not (
            result.intent in safe_intents
            or (
                result.intent == "integration"
                and result.entities.get("integration") == "see_integrations"
            )
        )
        for result in results
    )
def _list_saved_plans() -> str:
    """Muestra los planes almacenados."""
    with PlanStore() as store:
        plans = store.list_plans()
    if not plans:
        return "No hay planes guardados."
    lines = ["Planes guardados:"]
    for plan in plans:
        lines.append(f"- {plan['name']}: {plan['reason']}")
    return "\n".join(lines)
def _begin_edit_plan(name: str = "") -> str:
    """Inicia la edición de un plan guardado."""
    global _PENDING_OPERATION
    if not name:
        _PENDING_OPERATION = {"type": "edit_select"}
        return "¿Qué plan deseas editar? Escribe su nombre."
    with PlanStore() as store:
        plan = store.get_plan(name)
    if plan is None:
        return f"No existe un plan llamado '{name}'."
    if not plan.actions:
        return "El plan no contiene acciones que puedan editarse."
    lines = [f"Acciones del plan '{name}':"]
    for index, action in enumerate(plan.actions, start=1):
        lines.append(f"{index}. {action.name}")
        for key, value in action.parameters.items():
            lines.append(f"   {key} = {value}")
    lines.extend((
        "",
        "Puedes modificar parámetros con el formato:",
        "número_de_acción.nombre_del_parámetro",
        "Ejemplo: 1.city",
        "",
        "También podrás agregar o eliminar acciones.",
    ))
    _PENDING_OPERATION = {
        "type": "edit_target",
        "name": name,
        "plan": plan,
    }
    return "\n".join(lines)
def _format_edit_menu(name: str, plan: ActionPlan) -> str:
    """Muestra las acciones y opciones de edición."""
    lines = [f"Edición del plan '{name}':"]
    if not plan.actions:
        lines.append("El plan no contiene acciones.")
    else:
        for index, action in enumerate(plan.actions, start=1):
            lines.append(f"{index}. {action.name}")
            for key, value in action.parameters.items():
                lines.append(f"   {key} = {value}")
    lines.extend((
        "",
        "Comandos disponibles:",
        "editar 1",
        "agregar",
        "eliminar 1",
        "listar",
        "guardar",
        "cancelar",
    ))
    return "\n".join(lines)
def _begin_delete_plan(name: str = "") -> str:
    """Inicia la eliminación de un plan guardado."""
    global _PENDING_OPERATION
    if not name:
        _PENDING_OPERATION = {"type": "delete_select"}
        return "¿Qué plan deseas eliminar? Escribe su nombre."
    with PlanStore() as store:
        deleted = store.delete_plan(name)
    if not deleted:
        return f"No existe un plan llamado '{name}'."
    return f"El plan '{name}' ha sido eliminado."
def _begin_execute_plan(name: str = "") -> str:
    """Recupera un plan guardado y solicita autorización."""
    global _PENDING_PLAN, _PENDING_ACTION_INDEX
    global _PENDING_OPERATION
    if not name:
        _PENDING_OPERATION = {"type": "execute_select"}
        return "¿Qué plan deseas ejecutar? Escribe su nombre."
    with PlanStore() as store:
        plan = store.get_plan(name)
    if plan is None:
        return f"No existe un plan llamado '{name}'."
    if not plan.actions:
        return "El plan guardado no contiene acciones."
    # Los planes recuperados siempre requieren autorización.
    plan.requires_confirmation = True
    _PENDING_PLAN = plan
    _PENDING_ACTION_INDEX = 0
    return _format_action_plan(plan)
def _convert_parameter_value(
    action_name: str,
    parameter_name: str,
    value: str,
):
    """Convierte un parámetro según los metadatos de su integración."""
    definition = _INTEGRATIONS.get_definition(action_name)
    if definition is None:
        return value
    parameter = next(
        (
            item
            for item in definition.parameters
            if item.name == parameter_name
        ),
        None,
    )
    if parameter is None:
        return value
    target_type = parameter.type
    if target_type is bool:
        normalized = value.casefold()
        if normalized in {"true", "verdadero", "si", "sí", "1"}:
            return True
        if normalized in {"false", "falso", "no", "0"}:
            return False
        raise ValueError("Introduce un valor booleano válido.")
    try:
        return target_type(value)
    except (ValueError, TypeError) as error:
        raise ValueError(
            f"El valor debe ser de tipo {target_type.__name__}."
        ) from error
def _add_action_to_plan(operation: dict, action_name: str) -> str:
    """Prepara una acción nueva para incorporarla a un plan."""
    global _PENDING_OPERATION
    if action_name not in _INTEGRATIONS.get_handlers():
        return f"No existe una acción llamada '{action_name}'."
    definition = _INTEGRATIONS.get_definition(action_name)
    plan = operation["plan"]
    missing = []
    parameters = {}
    if definition is not None:
        missing = [
            parameter.name
            for parameter in definition.parameters
            if parameter.required
        ]
    pending = {
        "action": action_name,
        "parameters": parameters,
        "missing": missing,
    }
    if missing:
        _PENDING_OPERATION = {
            **operation,
            "type": "edit_add_parameter",
            "pending": pending,
        }
        return _prompt_edit_add_parameter(_PENDING_OPERATION)
    plan.actions.append(Action(action_name, parameters))
    with PlanStore() as store:
        updated = store.update_plan(operation["name"], plan)
    if not updated:
        plan.actions.pop()
        return "No se pudo actualizar el plan."
    _PENDING_OPERATION = {
        **operation,
        "type": "edit_target",
    }
    return f"Acción '{action_name}' agregada correctamente."
def _prompt_edit_add_parameter(operation: dict) -> str:
    """Solicita el siguiente parámetro obligatorio de una acción."""
    pending = operation["pending"]
    parameter_name = pending["missing"][0]
    definition = _INTEGRATIONS.get_definition(pending["action"])
    parameter = next(
        item for item in definition.parameters
        if item.name == parameter_name
    )
    return (
        f"Necesito '{parameter.name}' "
        f"({parameter.type.__name__}): "
        f"{parameter.description}\n"
        "Introduce su valor o escribe 'cancelar'."
    )
def _handle_plan_operation(command: str) -> str:
    """Procesa los pasos pendientes de gestión de planes."""
    global _PENDING_OPERATION
    operation = _PENDING_OPERATION
    if operation is None:
        return "No hay ninguna operación pendiente."
    value = command.strip()
    if value.casefold() == "cancelar":
        _PENDING_OPERATION = None
        return "Operación cancelada."
    if not value:
        return "Debes introducir un valor."
    operation_type = operation["type"]
    try:
        if operation_type == "save_name":
            with PlanStore() as store:
                store.save_plan(value, _PENDING_PLAN)
            _PENDING_OPERATION = None
            return f"Plan guardado como '{value}'."
        if operation_type == "edit_select":
            _PENDING_OPERATION = None
            return _begin_edit_plan(value)
        if operation_type == "edit_target":
            plan = operation["plan"]
            normalized = value.casefold()
            if normalized == "listar":
                return _format_edit_menu(operation["name"], plan)
            if normalized == "agregar":
                available = sorted(_INTEGRATIONS.get_handlers())
                _PENDING_OPERATION = {
                    **operation,
                    "type": "edit_add_select",
                }
                return (
                    "¿Qué acción deseas agregar?\n"
                    + "\n".join(f"- {name}" for name in available)
                )
            if normalized.startswith("agregar "):
                action_name = value[len("agregar "):].strip()
                return _add_action_to_plan(
                    operation,
                    action_name,
                )
            if normalized.startswith("eliminar "):
                try:
                    index = int(value.split(maxsplit=1)[1]) - 1
                except (ValueError, IndexError):
                    return "Indica el número. Ejemplo: eliminar 1"
                if not 0 <= index < len(plan.actions):
                    return "El número de acción no es válido."
                plan.actions.pop(index)
                with PlanStore() as store:
                    updated = store.update_plan(operation["name"], plan)
                if not updated:
                    return "No se pudo actualizar el plan."
                return "Acción eliminada correctamente.\n" + _format_edit_menu(
                    operation["name"], plan
                )
            try:
                action_number, parameter_name = value.split(".", 1)
                action_index = int(action_number) - 1
            except ValueError:
                return (
                    "Formato incorrecto. Usa 1.city, agregar "
                    "o eliminar 1."
                )
            if not 0 <= action_index < len(plan.actions):
                return "El número de acción no es válido."
            action = plan.actions[action_index]
            if parameter_name not in action.parameters:
                return "Ese parámetro no existe en la acción seleccionada."
            _PENDING_OPERATION = {
                "type": "edit_value",
                "name": operation["name"],
                "plan": plan,
                "action_index": action_index,
                "parameter": parameter_name,
            }
            return f"Nuevo valor para '{parameter_name}':"
        if operation_type == "edit_add_select":
            return _add_action_to_plan(operation, value)
        if operation_type == "edit_add_parameter":
            plan = operation["plan"]
            pending = operation["pending"]
            parameter_name = pending["missing"][0]
            converted = _convert_parameter_value(
                pending["action"],
                parameter_name,
                value,
            )
            pending["parameters"][parameter_name] = converted
            pending["missing"].pop(0)
            if pending["missing"]:
                return _prompt_edit_add_parameter(operation)
            action = Action(
                pending["action"],
                pending["parameters"],
            )
            plan.actions.append(action)
            with PlanStore() as store:
                updated = store.update_plan(operation["name"], plan)
            if not updated:
                plan.actions.pop()
                _PENDING_OPERATION = None
                return "No se pudo actualizar el plan."
            _PENDING_OPERATION = {
                **operation,
                "type": "edit_target",
            }
            return (
                f"Acción '{pending['action']}' agregada correctamente.\n"
                + _format_edit_menu(operation["name"], plan)
            )
        if operation_type == "edit_value":
            plan = operation["plan"]
            action = plan.actions[operation["action_index"]]
            parameter_name = operation["parameter"]
            new_value = _convert_parameter_value(
                action.name,
                parameter_name,
                value,
            )
            action.parameters[parameter_name] = new_value
            with PlanStore() as store:
                updated = store.update_plan(operation["name"], plan)
            _PENDING_OPERATION = None
            if not updated:
                return "El plan ya no existe."
            return f"Plan '{operation['name']}' actualizado correctamente."
        if operation_type == "delete_select":
            _PENDING_OPERATION = None
            return _begin_delete_plan(value)
        if operation_type == "execute_select":
            _PENDING_OPERATION = None
            return _begin_execute_plan(value)
    except (ValueError, TypeError) as error:
        return str(error)
    except Exception:
        _PENDING_OPERATION = None
        return "Ha ocurrido un error al gestionar el plan."
    _PENDING_OPERATION = None
    return "Operación desconocida."
def _start_pending_integration(analysis: AnalysisResult | AnalysisBatch) -> str | None:
    """Solicita los parámetros obligatorios que falten en una integración."""
    global _PENDING_INTEGRATION
    results = analysis.results if isinstance(analysis, AnalysisBatch) else [analysis]
    for result in results:
        if result.intent != "integration" or not result.understood:
            continue
        entities = result.entities
        errors = entities.get("errors", [])
        if errors:
            return "No puedo preparar la integración:\n" + "\n".join(errors)
        missing = list(entities.get("missing_parameters", []))
        if not missing:
            continue
        action_name = entities.get("integration")
        definition = _INTEGRATIONS.get_definition(action_name)
        if definition is None:
            return "No hay metadatos para solicitar los parámetros de esa integración."
        _PENDING_INTEGRATION = {
            "action": action_name,
            "definition": definition,
            "parameters": dict(entities.get("parameters", {})),
            "missing": missing,
        }
        return _prompt_pending_integration()
    return None
def _prompt_pending_integration() -> str:
    pending = _PENDING_INTEGRATION
    parameter_name = pending["missing"][0]
    parameter = next(p for p in pending["definition"].parameters if p.name == parameter_name)
    return (f"Necesito el parámetro '{parameter.name}' ({parameter.type.__name__}): "
            f"{parameter.description}\nIntroduce su valor o escribe 'cancelar'.")
def _handle_pending_integration(value: str) -> str:
    """Recoge los parámetros ausentes y presenta el plan para confirmación."""
    global _PENDING_INTEGRATION, _PENDING_PLAN, _PENDING_ACTION_INDEX
    pending = _PENDING_INTEGRATION
    if value.strip().casefold() == "cancelar":
        _PENDING_INTEGRATION = None
        return "Solicitud de integración cancelada."
    if not value.strip():
        return "El valor no puede estar vacío.\n" + _prompt_pending_integration()
    parameter_name = pending["missing"][0]
    try:
        converted = _convert_parameter_value(pending["action"], parameter_name, value.strip())
    except (TypeError, ValueError) as error:
        return f"{error}\n{_prompt_pending_integration()}"
    pending["parameters"][parameter_name] = converted
    pending["missing"].pop(0)
    if pending["missing"]:
        return _prompt_pending_integration()
    plan = ActionPlan(
        actions=[Action(pending["action"], pending["parameters"])],
        requires_confirmation=True,
        reason="Parámetros obligatorios completados.",
    )
    _PENDING_INTEGRATION = None
    _PENDING_PLAN = plan
    _PENDING_ACTION_INDEX = 0
    return _format_action_plan(plan)
def process_command(command: str) -> str:
    """Analiza, razona y procesa una instrucción recibida por JARVIS."""
    global _PENDING_PLAN, _PENDING_ACTION_INDEX
    global _PENDING_OPERATION, _PENDING_INTEGRATION
    if not isinstance(command, str):
        raise TypeError("La instrucción debe ser una cadena de texto.")
    command = command.strip()
    # Resolver primero la captura de parámetros de una integración.
    if _PENDING_INTEGRATION is not None:
        return _handle_pending_integration(command)
    # Resolver primero las operaciones pendientes.
    if _PENDING_OPERATION is not None:
        return _handle_plan_operation(command)
    # Resolver la autorización de un plan pendiente.
    if _PENDING_PLAN is not None:
        if command.casefold() in {"g", "guardar"}:
            _PENDING_OPERATION = {"type": "save_name"}
            return "¿Qué nombre deseas darle al plan?"
        return _handle_pending_confirmation(command)
    if not command:
        return "No he recibido ninguna instrucción."
    normalized = command.casefold()
    # Comandos de gestión de planes guardados.
    if normalized == "ver planes":
        return _list_saved_plans()
    if normalized == "editar_plan" or normalized.startswith("editar_plan "):
        name = command[len("editar_plan"):].strip()
        return _begin_edit_plan(name)
    if normalized == "eliminar_plan" or normalized.startswith("eliminar_plan "):
        name = command[len("eliminar_plan"):].strip()
        return _begin_delete_plan(name)
    if normalized == "ejecutar_plan" or normalized.startswith("ejecutar_plan "):
        name = command[len("ejecutar_plan"):].strip()
        return _begin_execute_plan(name)
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
        # Comprobar si alguna instrucción fue comprendida.
        if not _has_understood_instruction(analysis):
            return "Todavía no tengo una función para realizar esa tarea."
        # Completar por consola los parámetros obligatorios ausentes.
        pending_response = _start_pending_integration(analysis)
        if pending_response is not None:
            return pending_response
        # Determinar si el plan necesita autorización.
        if not _requires_confirmation(analysis):
            plan.requires_confirmation = False
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
        _PENDING_OPERATION = None
        return "Ha ocurrido un error al procesar la instrucción."
def _format_action_plan(plan: ActionPlan) -> str:
    """Presenta las acciones y sus parámetros."""
    lines = [
        "He preparado el siguiente plan:",
        "",
        "PLAN DE EJECUCIÓN:",
    ]
    for index, action in enumerate(plan.actions, start=1):
        lines.append(f"{index}. {action.name}")
        for key, value in action.parameters.items():
            lines.append(f"   {key} = {value}")
    if plan.reason:
        lines.extend(("", f"Motivo: {plan.reason}"))
    lines.extend((
        "",
        "¿Cómo deseas continuar?",
        "S = Ejecutar solamente la siguiente acción",
        "O = Autorizar todas las acciones restantes",
        "N = Cancelar las acciones restantes",
        "G = Guardar este plan",
    ))
    return "\n".join(lines)
def _format_next_action(plan: ActionPlan, index: int) -> str:
    """Presenta la siguiente acción pendiente."""
    action = plan.actions[index]
    lines = [
        f"Siguiente acción ({index + 1}/{len(plan.actions)}):",
        f"Acción: {action.name}",
    ]
    for key, value in action.parameters.items():
        lines.append(f"   {key} = {value}")
    lines.extend((
        "",
        "S = Ejecutar esta acción",
        "O = Autorizar todas las acciones restantes",
        "N = Cancelar las acciones restantes",
        "G = Guardar este plan",
    ))
    return "\n".join(lines)
def _execute_pending_actions(
    start: int,
    all_remaining: bool,
) -> str:
    """Ejecuta únicamente las acciones autorizadas."""
    global _PENDING_PLAN, _PENDING_ACTION_INDEX
    plan = _PENDING_PLAN
    if plan is None:
        return "No hay acciones pendientes de autorización."
    stop = len(plan.actions) if all_remaining else start + 1
    authorized_plan = ActionPlan(
        actions=plan.actions[start:stop],
        requires_confirmation=True,
        reason=plan.reason,
    )
    try:
        result = _AI_CORE.execute_plan(
            authorized_plan,
            confirmed=True,
        )
    except Exception as error:
        _PENDING_PLAN = None
        _PENDING_ACTION_INDEX = 0
        return f"Error al ejecutar el plan: {error}"
    if not result.success:
        _PENDING_PLAN = None
        _PENDING_ACTION_INDEX = 0
        return result.error or "No se pudo ejecutar el plan."
    _PENDING_ACTION_INDEX = stop
    if stop >= len(plan.actions):
        _PENDING_PLAN = None
        _PENDING_ACTION_INDEX = 0
        return (
            "Plan autorizado. Todas las acciones se ejecutaron correctamente.\n"
            + result.output
        )
    return (
        "Acción ejecutada correctamente.\n"
        + result.output
        + "\n\n"
        + _format_next_action(plan, stop)
    )
def _handle_pending_confirmation(command: str) -> str:
    """Procesa las respuestas de autorización del usuario."""
    global _PENDING_PLAN, _PENDING_ACTION_INDEX
    answer = command.strip().casefold()
    if answer in {"s", "si", "sí"}:
        return _execute_pending_actions(
            _PENDING_ACTION_INDEX,
            all_remaining=False,
        )
    if answer in {"o", "ok"}:
        return _execute_pending_actions(
            _PENDING_ACTION_INDEX,
            all_remaining=True,
        )
    if answer in {"n", "no"}:
        _PENDING_PLAN = None
        _PENDING_ACTION_INDEX = 0
        return "Plan cancelado. No se ejecutarán más acciones."
    return (
        "Respuesta no válida. Escribe S para ejecutar la siguiente acción, "
        "O para autorizar todas las restantes o N para cancelar."
    )