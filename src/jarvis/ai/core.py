from collections.abc import Mapping
from .context import ConversationContext
from .executor import ActionHandler, execute_action_plan
from .reasoning import create_action_plan
from .structures import (
    ActionPlan, AnalysisBatch, AnalysisResult, ExecutionResult, InputData,
    IntegrationDefinition,
)
from .understanding import analyze_input
class AICore:
    """Coordina comprensión, razonamiento, contexto y ejecución."""
    def __init__(
        self,
        handlers: Mapping[str, ActionHandler] | None = None,
        max_history: int = 10,
        integration_definitions: Mapping[str, IntegrationDefinition] | None = None,
    ):
        if handlers is not None and not isinstance(handlers, Mapping):
            raise TypeError("handlers debe ser un diccionario o Mapping.")
        if integration_definitions is not None and not isinstance(integration_definitions, Mapping):
            raise TypeError("integration_definitions debe ser un Mapping.")
        self._handlers = dict(handlers) if handlers is not None else {}
        self._integration_definitions = dict(integration_definitions or {})
        if any(not isinstance(value, IntegrationDefinition) for value in self._integration_definitions.values()):
            raise TypeError("Cada definición debe ser IntegrationDefinition.")
        self._context = ConversationContext(max_history)
    def process_input(self, data: InputData) -> tuple[AnalysisResult | AnalysisBatch, ActionPlan]:
        """Analiza la entrada y genera un plan sin ejecutar acciones."""
        analysis = analyze_input(
            data,
            context=self._context,
            available_integrations=self._handlers,
            integration_definitions=self._integration_definitions,
        )
        self._context.add_input(data)
        return analysis, create_action_plan(analysis)
    def execute_plan(self, plan: ActionPlan, confirmed: bool = False) -> ExecutionResult:
        return execute_action_plan(plan, self._handlers, confirmed)
    def get_history(self, limit: int | None = None) -> list[InputData]:
        return self._context.get_recent(limit)
    def get_context_text(self, limit: int | None = None) -> str:
        return self._context.get_context_text(limit)
    def clear_history(self) -> None:
        self._context.clear()
    def find_relevant_context(self, query: str, limit: int = 5, min_score: float = 0.3) -> list[InputData]:
        return self._context.find_relevant(query, limit=limit, min_score=min_score)
    def get_relevant_context(self, query: str, limit: int = 5, min_score: float = 0.3) -> str:
        return self._context.get_relevant_context(query, limit=limit, min_score=min_score)