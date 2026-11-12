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
"""
@dataclass
class Action:
    #Representa una acción individual de JARVIS
    name: str
    parameters: dict = field(default_factory=dict)
@dataclass
class ActionPlan:
    #Representa un conjunto de acciones independientes.
    actions: list[Action] = field(default_factory=list)
    requires_confirmation: bool = True
    reason: str = ""
"""
@dataclass
class ActionPlan:
    """Representa las acciones que JARVIS pretende realizar."""
    actions: list[str] = field(default_factory=list)
    parameters: dict = field(default_factory=dict)
    requires_confirmation: bool = True
    reason: str = ""
@dataclass
class ExecutionResult:
    """Contiene el resultado de ejecutar un plan."""
    success: bool
    output: str = ""
    error: str | None = None