from .config import VERSION
from .memory import initialize_memory
from .brain import process_command
from .capabilities import get_capabilities
def start_jarvis():
    """Inicia el asistente."""
    initialize_memory()
    capabilities = get_capabilities()
    print("=" * 40)
    print(f"JARVIS v{VERSION}")
    print("Sistema iniciado correctamente.")
    print("=" * 40)
    print("\nCapacidades:")
    for name, available in capabilities.items():
        if name != "system_info":
            status = "Disponible" if available else "Pendiente"
            print(f"- {name}: {status}")
    print("\nInformación del sistema:")
    for name, value in capabilities["system_info"].items():
        print(f"- {name}: {value}")
    print("\nEscribe 'ayuda' para ver los comandos.")
    print("Escribe 'salir' para cerrar JARVIS.")
    try:
        while True:
            try:
                command = input("\nTú: ").strip()
            except EOFError:
                break
            if command.lower() in ("salir", "exit", "quit"):
                break
            response = process_command(command)
            print(f"JARVIS: {response}")
    except KeyboardInterrupt:
        pass
    print("\nJARVIS: Hasta pronto.")
if __name__ == "__main__":
    start_jarvis()