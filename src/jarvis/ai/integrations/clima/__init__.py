from jarvis.ai.structures import IntegrationDefinition, IntegrationParameter
from .integration import consultar_clima
parametro_ciudad = IntegrationParameter(
    name="ciudad",
    description="Ciudad para consultar el clima, por ejemplo San Jose",
    type=str,
    flag="-c",
    required=True,
)
clima_integracion = IntegrationDefinition(
    name="clima",
    description="Consulta el clima actual de una ciudad",
    version="1.0.0",
    parameters=[parametro_ciudad],
    handler=consultar_clima,
)
INTEGRATIONS = [clima_integracion]
