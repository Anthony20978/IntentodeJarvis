"""Calculadora de expresiones matemáticas.

Uso:
    resultado = calcular("2 + 3 * 4 - 5 / 2")
"""
from __future__ import annotations
import math
import re
_ALIASES = {
    # Operadores
    "×": "*",
    "·": "*",
    "÷": "/",
    "_": "-",
    "**": "^",
    # Trigonometría
    "sen": "sin",
    "seno": "sin",
    "coseno": "cos",
    "tg": "tan",
    "tangente": "tan",
    # Logaritmos y raíces
    "logaritmo": "log",
    "raiz": "sqrt",
    "raizcuadrada": "sqrt",
    # Otras funciones
    "valorabsoluto": "abs",
    "piso": "floor",
    "techo": "ceil",
    "truncar": "trunc",
    "redondear": "round",
    "exponencial": "exp",
    # Constantes
    "pi": "pi",
    "π": "pi",
    "euler": "e",
}
_FUNCTIONS = {
    "sin", "cos", "tan",
    "ln", "log",
    "sqrt", "abs", "exp",
    "floor", "ceil", "trunc", "round",
    "min", "max",
}
_TOKEN_PATTERN = re.compile(
    r"\d+(?:[.,]\d*)?|[.,]\d+|[A-Za-zñÑ]+|π|"
    r"\*\*|<=|>=|==|!=|<>|=<|=>|[+\-*/^!%(),;{}\[\]<>×·÷_=]"
)
def _tokenize(expression: str) -> list[str]:
    """Convierte la expresión en tokens y normaliza sus alias."""
    tokens: list[str] = []
    position = 0
    while position < len(expression):
        if expression[position].isspace():
            position += 1
            continue
        match = _TOKEN_PATTERN.match(expression, position)
        if match is None:
            raise ValueError(
                f"Carácter no reconocido en la posición {position}: "
                f"{expression[position]!r}"
            )
        token = match.group()
        position = match.end()
        if token[0].isalpha() or token == "π":
            token = _ALIASES.get(token.lower(), token.lower())
        elif token in _ALIASES:
            token = _ALIASES[token]
        if token == ",":
            token = ";"
        tokens.append(token)
    if not tokens:
        raise ValueError("La expresión está vacía.")
    return tokens
class _Parser:
    """Analizador y evaluador mediante precedencia de operadores."""
    _PRECEDENCE = {
        "+": 1,
        "-": 1,
        "*": 2,
        "/": 2,
        "implicit*": 2,
        "u+": 3,
        "u-": 3,
        "^": 4,
        "!": 5,
        "%": 5,
    }
    def __init__(self, tokens: list[str], angle_unit: str) -> None:
        self.tokens = tokens
        self.position = 0
        self.angle_unit = angle_unit
    def _peek(self) -> str | None:
        if self.position >= len(self.tokens):
            return None
        return self.tokens[self.position]
    def _take(self) -> str:
        token = self._peek()
        if token is None:
            raise ValueError("La expresión terminó inesperadamente.")
        self.position += 1
        return token
    @staticmethod
    def _starts_value(token: str | None) -> bool:
        if token is None:
            return False
        return (
            token == "("
            or token in {"[", "{"}
            or token in _FUNCTIONS
            or token in {"pi", "e"}
            or token[0].isdigit()
            or token[0] == "."
        )
    def parse(self) -> float:
        result = self._expression(0)
        if self._peek() is not None:
            raise ValueError(f"Token inesperado: {self._peek()!r}")
        return float(result)
    def _expression(self, min_precedence: int) -> float:
        left = self._prefix()
        while True:
            token = self._peek()
            # Operadores postfijos.
            if token in {"!", "%"} and self._PRECEDENCE[token] >= min_precedence:
                self._take()
                if token == "%":
                    left /= 100
                else:
                    if left < 0 or not left.is_integer() or left > 170:
                        raise ValueError(
                            "El factorial requiere un entero entre 0 y 170."
                        )
                    left = float(math.factorial(int(left)))
                continue
            # Multiplicación explícita o implícita.
            implicit = self._starts_value(token)
            operator = "implicit*" if implicit else token
            if operator not in self._PRECEDENCE:
                break
            precedence = self._PRECEDENCE[operator]
            if precedence < min_precedence:
                break
            if not implicit:
                self._take()
            # La potencia es asociativa por la derecha.
            next_min = precedence if operator == "^" else precedence + 1
            right = self._expression(next_min)
            if operator in {"*", "implicit*"}:
                left *= right
            elif operator == "/":
                if right == 0:
                    raise ValueError("División entre cero.")
                left /= right
            elif operator == "+":
                left += right
            elif operator == "-":
                left -= right
            elif operator == "^":
                if left == 0 and right <= 0:
                    raise ValueError("Potencia indefinida.")
                try:
                    left = left ** right
                except (OverflowError, ValueError) as error:
                    raise ValueError(
                        "Potencia fuera del dominio real."
                    ) from error
                if isinstance(left, complex):
                    raise ValueError(
                        "El resultado no pertenece a los números reales."
                    )
        return float(left)
    def _prefix(self) -> float:
        token = self._take()
        if token in {"+", "-"}:
            value = self._expression(self._PRECEDENCE["u" + token])
            return value if token == "+" else -value
        if token in {"(", "[", "{"}:
            closing = {"(": ")", "[": "]", "{": "}"}[token]
            value = self._expression(0)
            if self._take() != closing:
                raise ValueError(f"Se esperaba {closing!r}.")
            return value
        if token in _FUNCTIONS:
            return self._function(token)
        if token == "pi":
            return math.pi
        if token == "e":
            return math.e
        try:
            return float(token.replace(",", "."))
        except ValueError as error:
            raise ValueError(
                f"Valor o variable desconocida: {token!r}"
            ) from error
    def _function(self, name: str) -> float:
        if self._take() != "(":
            raise ValueError(f"La función {name} requiere paréntesis.")
        arguments: list[float] = []
        if self._peek() not in {")", "]", "}"}:
            arguments.append(self._expression(0))
            while self._peek() == ";":
                self._take()
                arguments.append(self._expression(0))
        closing = self._take()
        if closing != ")":
            raise ValueError(
                "Se esperaba ')' al terminar los argumentos."
            )
        return _apply_function(name, arguments, self.angle_unit)
def _apply_function(
    name: str,
    args: list[float],
    angle_unit: str
) -> float:
    if name in {"sin", "cos", "tan"}:
        if len(args) != 1:
            raise ValueError(f"{name} solo acepta un argumento.")
        value = (
            math.radians(args[0])
            if angle_unit == "GRADOS"
            else args[0]
        )
        if name == "sin":
            return math.sin(value)
        if name == "cos":
            return math.cos(value)
        if abs(math.cos(value)) <= 1e-12:
            raise ValueError("Tangente indefinida.")
        return math.tan(value)
    if name == "sqrt":
        if len(args) not in {1, 2}:
            raise ValueError("sqrt acepta uno o dos argumentos.")
        value = args[0]
        index = args[1] if len(args) == 2 else 2.0
        if index == 0:
            raise ValueError(
                "El índice de la raíz no puede ser cero."
            )
        if value < 0:
            if not index.is_integer():
                raise ValueError(
                    "El índice debe ser entero para la raíz "
                    "de un número negativo."
                )
            if int(index) % 2 == 0:
                raise ValueError(
                    "Raíz de índice par de un número negativo."
                )
            return -((-value) ** (1 / index))
        return value ** (1 / index)
    if name == "abs":
        _require_count(name, args, 1)
        return abs(args[0])
    if name == "exp":
        _require_count(name, args, 1)
        return math.exp(args[0])
    if name == "ln":
        _require_count(name, args, 1)
        if args[0] <= 0:
            raise ValueError(
                "ln requiere un argumento positivo."
            )
        return math.log(args[0])
    if name == "log":
        if len(args) not in {1, 2}:
            raise ValueError(
                "log acepta uno o dos argumentos."
            )
        value = args[0]
        base = args[1] if len(args) == 2 else 10.0
        if value <= 0:
            raise ValueError(
                "El argumento del logaritmo debe ser positivo."
            )
        if base <= 0:
            raise ValueError(
                "La base del logaritmo debe ser positiva."
            )
        if math.isclose(base, 1.0, abs_tol=1e-12):
            raise ValueError(
                "La base del logaritmo no puede ser uno."
            )
        return math.log(value, base)
    if name in {"floor", "ceil", "trunc", "round"}:
        _require_count(name, args, 1)
        value = args[0]
        if name == "floor":
            return float(math.floor(value))
        if name == "ceil":
            return float(math.ceil(value))
        if name == "trunc":
            return float(math.trunc(value))
        # Redondeo convencional: los medios se alejan de cero.
        return float(
            math.floor(value + 0.5)
            if value >= 0
            else math.ceil(value - 0.5)
        )
    if name in {"min", "max"}:
        _require_count(name, args, 2)
        return min(args) if name == "min" else max(args)
    raise ValueError(f"Función desconocida: {name}")
def _require_count(
    name: str,
    args: list[float],
    expected: int
) -> None:
    if len(args) != expected:
        raise ValueError(
            f"{name} requiere exactamente {expected} argumento(s)."
        )
def calcular(
    expresion: str,
    unidad_angular: str = "GRADOS"
) -> float:
    """Evalúa una expresión matemática y devuelve un float.
    Args:
        expresion: Expresión matemática, por ejemplo ``"2+3*4-5/2"``.
        unidad_angular: ``"GRADOS"`` (predeterminado) o ``"RADIANES"``.
    Returns:
        El resultado de la expresión como ``float``.
    Raises:
        TypeError: Si la expresión o la unidad angular tienen un tipo incorrecto.
        ValueError: Si la expresión no es válida o la operación no está definida.
    """
    if not isinstance(expresion, str):
        raise TypeError("La expresión debe ser un str.")
    if not isinstance(unidad_angular, str):
        raise TypeError("La unidad angular debe ser un str.")
    unidad_angular = unidad_angular.upper()
    if unidad_angular not in {"GRADOS", "RADIANES"}:
        raise ValueError(
            "La unidad angular debe ser 'GRADOS' o 'RADIANES'."
        )
    tokens = _tokenize(expresion)
    return _Parser(tokens, unidad_angular).parse()