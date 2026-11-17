import unittest
from . import INTEGRATIONS
from .dev import calcular
from .integration import calculate
class TestCalculadora(unittest.TestCase):
    """Pruebas de la lógica matemática."""
    def test_arithmetic_expression(self):
        self.assertEqual(calcular("2 + 3 * 4"), 14.0)
    def test_square_root(self):
        self.assertEqual(calcular("sqrt(25)"), 5.0)
    def test_trigonometry_degrees(self):
        self.assertAlmostEqual(calcular("sen(30)"), 0.5)
    def test_trigonometry_radians(self):
        self.assertAlmostEqual(
            calcular("sen(pi/2)", "RADIANES"),
            1.0,
        )
class TestCalculadoraIntegration(unittest.TestCase):
    """Pruebas del handler que utiliza JARVIS."""
    def test_calculate_returns_string(self):
        result = calculate({"expresion": "2 + 3"})
        self.assertIsInstance(result, str)
        self.assertEqual(float(result), 5.0)
    def test_default_angular_unit(self):
        result = calculate({"expresion": "sen(30)"})
        self.assertAlmostEqual(float(result), 0.5)
    def test_explicit_angular_unit(self):
        result = calculate({
            "expresion": "sen(pi/2)",
            "unidad_angular": "RADIANES",
        })
        self.assertAlmostEqual(float(result), 1.0)
class TestCalculadoraDefinition(unittest.TestCase):
    """Pruebas de los metadatos de la integración."""
    def test_integration_is_registered(self):
        self.assertEqual(len(INTEGRATIONS), 2)
        self.assertEqual(INTEGRATIONS[0].name, "calculadora")
    def test_handler_is_calculate(self):
        self.assertIs(INTEGRATIONS[0].handler, calculate)
    def test_parameters_are_correct(self):
        definition = INTEGRATIONS[0]
        parameters = {
            parameter.name: parameter
            for parameter in definition.parameters
        }
        self.assertIn("expresion", parameters)
        self.assertIn("unidad_angular", parameters)
        self.assertIs(parameters["expresion"].type, str)
        self.assertTrue(parameters["expresion"].required)
        self.assertIs(parameters["unidad_angular"].type, str)
        self.assertFalse(parameters["unidad_angular"].required)
if __name__ == "__main__":
    unittest.main()