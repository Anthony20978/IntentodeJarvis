from jarvis.ai.structures import IntegrationDefinition, IntegrationParameter
from .integration import calculate, calculate_ult
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
    description="Recibe una expresion matematica y calcula su resultado (Versión con resultado directo)",
    version="1.0.0",
    visible=False,
    parameters=[parametro_expresion, parametro_unidad],
    handler=calculate
)
mostrar_integracion = IntegrationDefinition(
    name= "calcular",
    description="Recibe una expresion matematica y calcula su resultado (Versión con resultado en formato textual)",
    version="1.0.0",
    visible=True,
    parameters=[parametro_expresion, parametro_unidad],
    handler = calculate_ult
)
INTEGRATIONS = [calcular_integracion,mostrar_integracion]