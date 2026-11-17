from dataclasses import dataclass, field
from datetime import datetime
from collections.abc import Callable
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
@dataclass
class IntegrationParameter:
    """Describe un parámetro que necesita una integración."""
    name: str
    description: str
    type: str
    flag: str
    required: bool = True
    def __post_init__(self):
        if not isinstance(self.flag, str) or not self.flag.strip():
            raise ValueError("La bandera no puede estar vacía.")
        if not self.flag.startswith("-"):
            raise ValueError("La bandera debe comenzar con un guion.")
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("El nombre del parámetro no puede estar vacío.")
        if not isinstance(self.description, str):
            raise TypeError("description debe ser texto.")
        if not isinstance(self.type, type):
            raise TypeError("type debe ser un tipo válido de Python.")
        if not isinstance(self.required, bool):
            raise TypeError("required debe ser un booleano.")
@dataclass
class IntegrationDefinition:
    """Describe una acción ejecutable de una integración."""
    name: str
    description: str
    version: str
    parameters: list[IntegrationParameter] = field(default_factory=list)
    handler: Callable[[dict], str] = field(default=None)
    visible: bool = True
    def __post_init__(self):
        flags = [parameter.flag for parameter in self.parameters]
        if not isinstance(self.visible,bool):
            raise ValueError("Visible tiene que ser un booleano")
        if len(flags) != len(set(flags)):
            raise ValueError("No puede haber banderas duplicadas.")
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("El nombre de la integración no puede estar vacío.")
        if not isinstance(self.description, str):
            raise TypeError("description debe ser texto.")
        if not isinstance(self.version, str) or not self.version.strip():
            raise ValueError("La versión no puede estar vacía.")
        if not isinstance(self.parameters, list):
            raise TypeError("parameters debe ser una lista.")
        if not all(
            isinstance(parameter, IntegrationParameter)
            for parameter in self.parameters
        ):
            raise TypeError(
                "Todos los parámetros deben ser IntegrationParameter."
            )
        names = [parameter.name for parameter in self.parameters]
        if len(names) != len(set(names)):
            raise ValueError("No puede haber parámetros duplicados.")
        if not callable(self.handler):
            raise TypeError("handler debe ser una función ejecutable.")