from jarvis.ai.structures import IntegrationDefinition, IntegrationParameter
from .integration import iniciar_temporizador, iniciar_cronometro, detener_cronometro
parametro_segundos = IntegrationParameter(
    name="segundos",
    description="Duración del temporizador en segundos (entre 1 y 60)",
    type=int,
    flag="-s",
    required=True,
)
parametro_minutos = IntegrationParameter(
    name="minutos",
    description="Duración del temporizador en minutos (entre 1 y 60)",
    type=int,
    flag="-m",
    required=False,
)
parametro_horas = IntegrationParameter(
    name="horas",
    description="Duración del temporizador en horas (entre 1 y 24)",
    type=int,
    flag="-h",
    required=False,
)
parametro_nombre = IntegrationParameter(
    name="nombre",
    description="Nombre opcional del temporizador",
    type=str,
    flag="-n",
    required=False,
)
temporizador_integracion = IntegrationDefinition(
    name="temporizador",
    description="Inicia una cuenta regresiva y avisa cuando termina",
    version="1.0.0",
    parameters=[parametro_segundos,parametro_minutos,parametro_horas, parametro_nombre],
    handler=iniciar_temporizador,
)
cronometro_integracion = IntegrationDefinition(
    name="cronometro",
    description="Inicia un cronómetro",
    version="1.0.0",
    parameters=[],
    handler=iniciar_cronometro,
)
detener_cronometro_integracion = IntegrationDefinition(
    name="detener_cronometro",
    description="Detiene el cronómetro y muestra el tiempo transcurrido",
    version="1.0.0",
    parameters=[],
    handler=detener_cronometro,
)
INTEGRATIONS = [
    temporizador_integracion,
    cronometro_integracion,
    detener_cronometro_integracion,
]