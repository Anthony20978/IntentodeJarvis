from collections.abc import Callable, Mapping
from importlib import import_module
from pathlib import Path
from .structures import IntegrationDefinition
IntegrationHandler = Callable[[dict], str]
class IntegrationRegistry:
    """Administra y descubre las integraciones disponibles para la IA."""
    def __init__(
        self,
        handlers: Mapping[str, IntegrationHandler] | None = None,
        *,
        auto_discover: bool = True,
    ) -> None:
        self._handlers: dict[str, IntegrationHandler] = {}
        self._definitions: dict[str, IntegrationDefinition] = {}
        self._discovery_errors: dict[str, str] = {}
        if not isinstance(auto_discover, bool):
            raise TypeError("auto_discover debe ser un valor booleano.")
        if handlers is not None:
            if not isinstance(handlers, Mapping):
                raise TypeError("handlers debe ser un diccionario o Mapping.")
            for name, handler in handlers.items():
                self.register(name, handler)
        if auto_discover:
            self._discovery_errors = self.discover_integrations()
    def register(
        self,
        name: str,
        handler: IntegrationHandler,
        *,
        replace: bool = False,
    ) -> None:
        """Registra una función ejecutable."""
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
        self._definitions.pop(name, None)
    def register_definition(
        self,
        definition: IntegrationDefinition,
        *,
        replace: bool = False,
    ) -> None:
        """Registra una acción con todos sus metadatos."""
        if not isinstance(definition, IntegrationDefinition):
            raise TypeError(
                "definition debe ser una IntegrationDefinition."
            )
        if not isinstance(replace, bool):
            raise TypeError("replace debe ser un valor booleano.")
        name = definition.name.strip()
        self.register(
            name,
            definition.handler,
            replace=replace,
        )
        self._definitions[name] = definition
    def discover_integrations(self) -> dict[str, str]:
        """Descubre integraciones mediante sus archivos __init__.py."""
        errors: dict[str, str] = {}
        integrations_dir = Path(__file__).with_name("integrations")
        if not integrations_dir.is_dir():
            return errors
        for folder in sorted(integrations_dir.iterdir()):
            if not folder.is_dir() or folder.name.startswith("_"):
                continue
            init_file = folder / "__init__.py"
            if not init_file.is_file():
                continue
            try:
                module = import_module(
                    f".integrations.{folder.name}",
                    package=__package__,
                )
                definitions = getattr(module, "INTEGRATIONS", None)
                if not isinstance(definitions, (list, tuple)):
                    raise TypeError(
                        "__init__.py debe definir INTEGRATIONS como una lista."
                    )
                names = set()
                # Validar todas las definiciones antes de registrarlas.
                for definition in definitions:
                    if not isinstance(definition, IntegrationDefinition):
                        raise TypeError(
                            "INTEGRATIONS solo puede contener "
                            "IntegrationDefinition."
                        )
                    name = definition.name.strip()
                    if name in names:
                        raise ValueError(
                            f"La acción '{name}' está duplicada."
                        )
                    if name in self._handlers:
                        raise ValueError(
                            f"La acción '{name}' ya está registrada."
                        )
                    names.add(name)
                for definition in definitions:
                    self.register_definition(definition)
            except Exception as error:
                errors[folder.name] = str(error)
        return errors
    def unregister(self, name: str) -> bool:
        """Elimina una integración y sus metadatos."""
        if not isinstance(name, str):
            raise TypeError("El nombre de la integración debe ser texto.")
        name = name.strip()
        removed = self._handlers.pop(name, None) is not None
        self._definitions.pop(name, None)
        return removed
    def get_handler(self, name: str) -> IntegrationHandler | None:
        """Obtiene una función por su nombre."""
        if not isinstance(name, str):
            raise TypeError("El nombre de la integración debe ser texto.")
        return self._handlers.get(name.strip())
    def get_handlers(self) -> dict[str, IntegrationHandler]:
        """Devuelve una copia de los handlers registrados."""
        return self._handlers.copy()
    def get_definition(
        self,
        name: str,
    ) -> IntegrationDefinition | None:
        """Obtiene los metadatos de una acción."""
        if not isinstance(name, str):
            raise TypeError("El nombre de la integración debe ser texto.")
        return self._definitions.get(name.strip())
    def get_definitions(self) -> dict[str, IntegrationDefinition]:
        """Devuelve una copia de las definiciones registradas."""
        return self._definitions.copy()
    def get_discovery_errors(self) -> dict[str, str]:
        """Devuelve los errores encontrados durante el descubrimiento."""
        return self._discovery_errors.copy()
    def has_handler(self, name: str) -> bool:
        """Comprueba si existe una integración."""
        return self.get_handler(name) is not None
    def __len__(self) -> int:
        return len(self._handlers)