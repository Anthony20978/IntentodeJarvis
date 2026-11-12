from collections.abc import Callable, Mapping
IntegrationHandler = Callable[[dict], str]
class IntegrationRegistry:
    """Administra las funciones externas disponibles para el núcleo de IA."""
    def __init__(
        self,
        handlers: Mapping[str, IntegrationHandler] | None = None,
    ) -> None:
        self._handlers: dict[str, IntegrationHandler] = {}
        if handlers is not None:
            if not isinstance(handlers, Mapping):
                raise TypeError("handlers debe ser un diccionario o Mapping.")
            for name, handler in handlers.items():
                self.register(name, handler)
    def register(
        self,
        name: str,
        handler: IntegrationHandler,
        *,
        replace: bool = False,
    ) -> None:
        """Registra una función y evita sobrescribirla accidentalmente."""
        if not isinstance(name, str) or not name.strip():
            raise ValueError("El nombre de la integración no puede estar vacío.")
        if not callable(handler):
            raise TypeError("La integración debe ser una función ejecutable.")
        if not isinstance(replace, bool):
            raise TypeError("replace debe ser un valor booleano.")
        name = name.strip()
        if name in self._handlers and not replace:
            raise ValueError(f"La integración '{name}' ya está registrada.")
        self._handlers[name] = handler
    def unregister(self, name: str) -> bool:
        """Elimina una integración; indica si existía."""
        if not isinstance(name, str):
            raise TypeError("El nombre de la integración debe ser texto.")
        return self._handlers.pop(name.strip(), None) is not None
    def get_handler(self, name: str) -> IntegrationHandler | None:
        """Obtiene una integración por su nombre."""
        if not isinstance(name, str):
            raise TypeError("El nombre de la integración debe ser texto.")
        return self._handlers.get(name.strip())
    def get_handlers(self) -> dict[str, IntegrationHandler]:
        """Devuelve una copia de las integraciones registradas."""
        return self._handlers.copy()
    def has_handler(self, name: str) -> bool:
        """Comprueba si existe una integración."""
        return self.get_handler(name) is not None
    def __len__(self) -> int:
        return len(self._handlers)