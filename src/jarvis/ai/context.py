from collections import deque
import re
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
        self._validate_limit(limit)
        history = list(self._history)
        if limit is not None:
            history = history[-limit:]
        return history
    def get_last_input(self, source: str | None = None) -> InputData | None:
        """Recupera la última entrada, opcionalmente filtrada por origen."""
        if source is not None and not isinstance(source, str):
            raise TypeError("source debe ser una cadena de texto.")
        for data in reversed(self._history):
            if source is None or data.source == source:
                return data
        return None
    def get_context_text(self, limit: int | None = None) -> str:
        """Convierte el historial reciente en contexto textual."""
        history = self.get_recent(limit)
        if not history:
            return ""
        lines = []
        for data in history:
            source = data.source.lower()
            if source == "user":
                label = "Usuario"
            elif source in ("assistant", "jarvis"):
                label = "JARVIS"
            else:
                label = data.source.capitalize()
            lines.append(f"{label}: {data.text}")
        return "\n".join(lines)
    def find_relevant(
        self,
        query: str,
        limit: int = 5,
        min_score: float = 0.3,
    ) -> list[InputData]:
        """
        Busca entradas anteriores relacionadas con una consulta.
        Solo devuelve coincidencias que superen el score mínimo.
        """
        if not isinstance(query, str):
            raise TypeError("query debe ser una cadena de texto.")
        self._validate_limit(limit)
        if (
            not isinstance(min_score, (int, float))
            or isinstance(min_score, bool)
        ):
            raise TypeError("min_score debe ser un número.")
        if not 0.0 <= min_score <= 1.0:
            raise ValueError("min_score debe estar entre 0 y 1.")
        query_words = self._extract_words(query)
        if not query_words:
            return []
        matches = []
        for index, data in enumerate(self._history):
            message_words = self._extract_words(data.text)
            common_words = query_words.intersection(message_words)
            if common_words:
                score = len(common_words) / len(query_words)
                if score >= min_score:
                    matches.append((score, index, data))
        matches.sort(
            key=lambda item: (item[0], item[1]),
            reverse=True,
        )
        return [
            data
            for _, _, data in matches[:limit]
        ]
    def get_relevant_context(
        self,
        query: str,
        limit: int = 5,
        min_score: float = 0.3
    ) -> str:
        """Devuelve las entradas relacionadas con una consulta como texto."""
        relevant = self.find_relevant(query, limit,min_score)
        if not relevant:
            return ""
        lines = []
        for data in relevant:
            source = data.source.lower()
            if source == "user":
                label = "Usuario"
            elif source in ("assistant", "jarvis"):
                label = "JARVIS"
            else:
                label = data.source.capitalize()
            lines.append(f"{label}: {data.text}")
        return "\n".join(lines)
    def clear(self) -> None:
        """Vacía el historial de conversación."""
        self._history.clear()
    @staticmethod
    def _extract_words(text: str) -> set[str]:
        """Extrae palabras normalizadas para comparar mensajes."""
        return set(re.findall(r"\w+", text.casefold()))
    @staticmethod
    def _validate_limit(limit: int | None) -> None:
        if limit is not None:
            if not isinstance(limit, int) or isinstance(limit, bool):
                raise TypeError("limit debe ser un número entero.")
            if limit <= 0:
                raise ValueError("limit debe ser mayor que cero.")