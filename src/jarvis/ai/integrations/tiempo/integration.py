from .dev import (
    esperar_temporizador,
    iniciar_medicion,
    detener_medicion,
)
def iniciar_temporizador(parameters: dict) -> str:
    """Handler de Jarvis para iniciar una cuenta regresiva."""
    segundos = parameters["segundos"]
    segundos = segundos + (parameters.get("minutos",0)*60)
    segundos = segundos + (parameters.get("horas",0)*3600)        
    nombre = parameters.get("nombre", "")
    return esperar_temporizador(segundos, nombre=nombre)
def iniciar_cronometro(parameters: dict) -> str:
    """Inicia el cronómetro."""
    return iniciar_medicion()
def detener_cronometro(parameters: dict) -> str:
    """Detiene el cronómetro y devuelve el tiempo transcurrido."""
    return detener_medicion()