from .dev import obtener_clima
def consultar_clima(parameters: dict) -> str:
    """Handler de Jarvis para consultar el clima."""
    ciudad = parameters["ciudad"]
    return obtener_clima(ciudad)
