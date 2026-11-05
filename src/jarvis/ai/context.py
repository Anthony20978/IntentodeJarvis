from collections import deque
from .structures import InputData
class ConversationContext:
    """Gestiona el contexto temporal de una conversación."""
    def __init__(self, max_history: int = 10):
        if not isinstance(max_history, int) or isinstance(max_history, bool):
            raise TypeError("max_history debe ser un número entero.")
        if max_history <= 0:
            raise ValueError("max_history debe ser mayor que cero.")
        self._history = deque(maxlen=max_history)
    def add_input(self, data: InputData) -> None:
        """Añade una entrada al historial."""
        if not isinstance(data, InputData):
            raise TypeError("Se esperaba un objeto InputData.")
        self._history.append(data)
    def get_recent(self, limit: int | None = None) -> list[InputData]:
        """Devuelve las entradas más recientes."""
        if limit is not None:
            if not isinstance(limit, int) or isinstance(limit, bool):
                raise TypeError("limit debe ser un número entero.")
            if limit <= 0:
                raise ValueError("limit debe ser mayor que cero.")
        history = list(self._history)
        if limit is not None:
            history = history[-limit:]
        return history
    def clear(self) -> None:
        """Limpia el historial de conversación."""
        self._history.clear()