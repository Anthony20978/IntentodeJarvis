from .config import VERSION
from .memory import initialize_memory
from .brain import (
    process_command,
    get_background_notifications,
    shutdown_background_tasks,
)
from .capabilities import get_capabilities
EXIT_COMMANDS = {"salir", "exit", "quit"}
def _show_background_notifications() -> None:
    """Muestra las notificaciones de tareas completadas."""
    for notification in get_background_notifications():
        status = notification.status.value
        if status == "completed":
            print(
                f"\nJARVIS: La tarea '{notification.name}' "
                "ha terminado correctamente."
            )
        elif status == "failed":
            print(
                f"\nJARVIS: La tarea '{notification.name}' "
                f"ha fallado: {notification.error}"
            )
        elif status == "cancelled":
            print(
                f"\nJARVIS: La tarea '{notification.name}' "
                "fue cancelada."
            )
def _show_startup() -> None:
    """Muestra la información inicial de JARVIS."""
    capabilities = get_capabilities()
    print("=" * 40)
    print(f"JARVIS v{VERSION}")
    print("Sistema iniciado correctamente.")
    print("=" * 40)
    print("\nCapacidades:")
    for name, available in capabilities.items():
        if name == "system_info":
            continue
        status = "Disponible" if available else "Pendiente"
        print(f"- {name}: {status}")
    system_info = capabilities.get("system_info", {})
    if system_info:
        print("\nInformación del sistema:")
        for name, value in system_info.items():
            print(f"- {name}: {value}")
    print("\nEscribe 'ayuda' para ver los comandos.")
    print("Escribe 'salir' para cerrar JARVIS.")
def _conversation_loop() -> None:
    """Gestiona el ciclo principal de conversación."""
    while True:
        try:
            command = input("\nTú: ").strip()
            _show_background_notifications()
        except EOFError:
            break
        if command.lower() in EXIT_COMMANDS:
            break
        try:
            response = process_command(command)
            print(f"JARVIS: {response}")
        except Exception as error:
            print(f"JARVIS: No pude procesar la instrucción.")
            print(f"Error interno: {error}")
def start_jarvis() -> None:
    """Inicializa y ejecuta el asistente."""
    try:
        initialize_memory()
        _show_startup()
        _conversation_loop()
    except KeyboardInterrupt:
        pass
    except Exception as error:
        print(f"\nJARVIS: No pude iniciar correctamente.")
        print(f"Error interno: {error}")
    finally:
        shutdown_background_tasks()
        print("\nJARVIS: Hasta pronto.")