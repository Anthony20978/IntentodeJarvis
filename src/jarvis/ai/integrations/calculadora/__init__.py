from jarvis.ai.structures import IntegrationDefinition, IntegrationParameter
from .integration import calculate
parametro_expresion = IntegrationParameter(
    name="expresion",
    description="expresion que se va a calcular",
    type=str,
    flag="-x",
    required=True,
)
parametro_unidad = IntegrationParameter(
    name="unidad_angular",
    description="Unidad angular utilizada en la expresion",
    type=str,
    flag="-u",
    required=False
)
calcular_integracion = IntegrationDefinition(
    name= "calculadora",
    description="Recibe una expresion matematica y calcula su resultado",
    version="1.0.0",
    parameters=[parametro_expresion, parametro_unidad],
    handler=calculate
)
INTEGRATIONS = [calcular_integracion]