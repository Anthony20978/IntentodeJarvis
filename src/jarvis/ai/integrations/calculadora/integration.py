from .dev import calcular
def calculate(parameters: dict) -> float:
    expresion = parameters["expresion"]
    unidad = parameters.get("unidad_angular", "GRADOS")
    return str(calcular(expresion,unidad_angular=unidad))
def calculate_ult(parameters: dict) -> str:
    expresion = parameters["expresion"]
    unidad = parameters.get("unidad_angular", "GRADOS")
    return "El resultado es: " + str(calcular(expresion,unidad_angular=unidad))