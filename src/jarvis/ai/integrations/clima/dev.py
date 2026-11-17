"""Funciones auxiliares para la integración de clima.

Utiliza la API pública de Open-Meteo; no requiere clave ni dependencias externas.
"""
import json
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import URLError, HTTPError


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    0: "Despejado",
    1: "Mayormente despejado",
    2: "Parcialmente nublado",
    3: "Nublado",
    45: "Niebla",
    48: "Niebla con escarcha",
    51: "Llovizna ligera",
    53: "Llovizna moderada",
    55: "Llovizna intensa",
    56: "Llovizna helada ligera",
    57: "Llovizna helada intensa",
    61: "Lluvia ligera",
    63: "Lluvia moderada",
    65: "Lluvia intensa",
    66: "Lluvia helada ligera",
    67: "Lluvia helada intensa",
    71: "Nevada ligera",
    73: "Nevada moderada",
    75: "Nevada intensa",
    77: "Granizo pequeño",
    80: "Chubascos ligeros",
    81: "Chubascos moderados",
    82: "Chubascos fuertes",
    85: "Chubascos de nieve ligeros",
    86: "Chubascos de nieve fuertes",
    95: "Tormenta",
    96: "Tormenta con granizo ligero",
    99: "Tormenta con granizo fuerte",
}


def _get_json(url: str, params: dict) -> dict:
    query = urlencode(params)
    request_url = f"{url}?{query}"
    with urlopen(request_url, timeout=12) as response:
        return json.loads(response.read().decode("utf-8"))


def obtener_clima(ciudad: str) -> str:
    """Devuelve el clima actual y la probabilidad de lluvia de hoy."""
    if not isinstance(ciudad, str) or not ciudad.strip():
        raise ValueError("Debes indicar una ciudad.")

    try:
        ubicaciones = _get_json(
            GEOCODING_URL,
            {"name": ciudad.strip(), "count": 1, "language": "es", "format": "json"},
        )
        resultados = ubicaciones.get("results") or []
        if not resultados:
            return f"No encontré la ciudad '{ciudad}'. Revisa el nombre e inténtalo de nuevo."

        lugar = resultados[0]
        pronostico = _get_json(
            FORECAST_URL,
            {
                "latitude": lugar["latitude"],
                "longitude": lugar["longitude"],
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,wind_speed_10m",
                "daily": "precipitation_probability_max",
                "forecast_days": 1,
                "timezone": "auto",
            },
        )

        actual = pronostico["current"]
        diario = pronostico.get("daily", {})
        codigo = actual.get("weather_code")
        estado = WEATHER_CODES.get(codigo, "Estado del tiempo no disponible")
        probabilidad = (diario.get("precipitation_probability_max") or [None])[0]
        nombre = lugar.get("name", ciudad.strip())
        region = lugar.get("admin1")
        pais = lugar.get("country")
        ubicacion = ", ".join(parte for parte in (nombre, region, pais) if parte)

        lineas = [
            f"Clima actual en {ubicacion}:",
            f"- Estado: {estado}",
            f"- Temperatura: {actual.get('temperature_2m')} °C",
            f"- Sensación térmica: {actual.get('apparent_temperature')} °C",
            f"- Humedad: {actual.get('relative_humidity_2m')}%",
            f"- Viento: {actual.get('wind_speed_10m')} km/h",
            f"- Precipitación actual: {actual.get('precipitation')} mm",
            f"- Probabilidad máxima de lluvia hoy: {probabilidad if probabilidad is not None else 'No disponible'}%",
        ]
        return "\n".join(lineas)
    except (HTTPError, URLError, TimeoutError, OSError, KeyError, ValueError) as error:
        return f"No pude consultar el clima en este momento. Comprueba tu conexión e inténtalo de nuevo. Detalle: {error}"
