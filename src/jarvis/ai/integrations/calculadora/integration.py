from .dev import calcular
def calculate(parameters: dict) -> str:
    expresion = parameters["expresion"]
    unidad = parameters.get("unidad_angular", "GRADOS")
    return str(calcular(expresion,unidad_angular=unidad))