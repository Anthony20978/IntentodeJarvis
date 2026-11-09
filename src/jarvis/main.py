from .config import VERSION
from .memory import initialize_memory
from .brain import process_command
from .capabilities import get_capabilities
EXIT_COMMANDS = {"salir", "exit", "quit"}
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
        print("\nJARVIS: Hasta pronto.")