"""Funciones auxiliares para temporizador y cronómetro."""
import time
MAX_SEGUNDOS = 24 * 60 * 60
_inicio_cronometro = None
def esperar_temporizador(segundos: int, nombre: str = "") -> str:
    """Espera la duración indicada y devuelve un aviso al terminar."""
    if isinstance(segundos, bool) or not isinstance(segundos, int):
        raise TypeError("La duración debe ser un número entero de segundos.")
    if not 1 <= segundos <= MAX_SEGUNDOS:
        raise ValueError("La duración debe estar entre 1 y 86400 segundos.")
    if not isinstance(nombre, str):
        raise TypeError("El nombre del temporizador debe ser texto.")
    time.sleep(segundos)
    etiqueta = f" ({nombre.strip()})" if nombre.strip() else ""
    return f"Tiempo terminado{etiqueta}."
def iniciar_medicion() -> str:
    """Comienza una medición usando el reloj monotónico."""
    global _inicio_cronometro
    if _inicio_cronometro is not None:
        raise RuntimeError("El cronómetro ya está en marcha.")
    _inicio_cronometro = time.monotonic()
    return "Cronómetro iniciado."
def detener_medicion() -> str:
    """Finaliza la medición y devuelve el tiempo transcurrido."""
    global _inicio_cronometro
    if _inicio_cronometro is None:
        raise RuntimeError("No hay ningún cronómetro en marcha.")
    transcurrido = time.monotonic() - _inicio_cronometro
    _inicio_cronometro = None
    horas, resto = divmod(int(transcurrido), 3600)
    minutos, segundos = divmod(resto, 60)
    centesimas = int((transcurrido - int(transcurrido)) * 100)
    return (
        f"Tiempo transcurrido: {horas:02d}:{minutos:02d}:"
        f"{segundos:02d}.{centesimas:02d}"
    )