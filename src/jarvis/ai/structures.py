from dataclasses import dataclass, field
from datetime import datetime
@dataclass
class InputData:
    """Representa la entrada recibida por JARVIS."""
    text: str
    timestamp: datetime
    source: str
@dataclass
class AnalysisResult:
    """Contiene el resultado de analizar una entrada."""
    intent: str
    entities: dict = field(default_factory=dict)
    confidence: float = 0.0
    understood: bool = False
@dataclass
class AnalysisBatch:
    """Agrupa varios resultados de análisis independientes."""
    results: list[AnalysisResult] = field(default_factory=list)
    def __post_init__(self):
        if not isinstance(self.results, list):
            raise TypeError("results debe ser una lista.")
        if not all(
            isinstance(result, AnalysisResult)
            for result in self.results
        ):
            raise TypeError(
                "Todos los elementos deben ser AnalysisResult."
            )
@dataclass
class Action:
    #Representa una acción individual de JARVIS
    name: str
    parameters: dict = field(default_factory=dict)
@dataclass
class ActionPlan:
    #Representa un conjunto de acciones independientes.
    actions: list[Action] = field(default_factory=list)
    parameters: dict = field(default_factory=dict)
    requires_confirmation: bool = True
    reason: str = ""
@dataclass
class ExecutionResult:
    """Contiene el resultado de ejecutar un plan."""
    success: bool
    output: str = ""
    error: str | None = None