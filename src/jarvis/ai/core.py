from collections.abc import Mapping
from .context import ConversationContext
from .executor import ActionHandler, execute_action_plan
from .reasoning import create_action_plan
from .structures import (
    ActionPlan,
    AnalysisResult,
    ExecutionResult,
    InputData,
)
from .understanding import analyze_input
class AICore:
    """Coordina los componentes principales de inteligencia."""
    def __init__(
        self,
        handlers: Mapping[str, ActionHandler] | None = None,
        max_history: int = 10,
    ):
        if handlers is not None and not isinstance(handlers, Mapping):
            raise TypeError("handlers debe ser un diccionario o Mapping.")
        self._handlers = dict(handlers) if handlers is not None else {}
        self._context = ConversationContext(max_history)
    def process_input(
        self,
        data: InputData,
    ) -> tuple[AnalysisResult, ActionPlan]:
        """Analiza una entrada utilizando el contexto disponible."""
        analysis = analyze_input(data, context=self._context)
        self._context.add_input(data)
        plan = create_action_plan(analysis)
        return analysis, plan
    def execute_plan(
        self,
        plan: ActionPlan,
        confirmed: bool = False,
    ) -> ExecutionResult:
        """Ejecuta un plan mediante los manejadores registrados."""
        return execute_action_plan(plan, self._handlers, confirmed)
    def get_history(
        self,
        limit: int | None = None,
    ) -> list[InputData]:
        """Devuelve el historial de entradas."""
        return self._context.get_recent(limit)
    def get_context_text(
        self,
        limit: int | None = None,
    ) -> str:
        """Devuelve el historial como texto."""
        return self._context.get_context_text(limit)
    def clear_history(self) -> None:
        """Limpia el historial."""
        self._context.clear()
    def find_relevant_context(
        self,
        query: str,
        limit: int = 5,
        min_score: float = 0.3,
    ) -> list[InputData]:
        """Recupera entradas relevantes del historial."""
        return self._context.find_relevant(
            query,
            limit=limit,
            min_score=min_score,
        )
    def get_relevant_context(
        self,
        query: str,
        limit: int = 5,
        min_score: float = 0.3,
    ) -> str:
        """Recupera el contexto relevante en formato conversacional."""
        return self._context.get_relevant_context(
            query,
            limit=limit,
            min_score=min_score,
        )