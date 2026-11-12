import unittest
from src.jarvis.brain import (
    _AI_CORE,
    get_integrations,
    register_integration,
    unregister_integration,
)
from src.jarvis.ai.structures import ActionPlan,Action
class TestBrainIntegrations(unittest.TestCase):
    def setUp(self):
        self.name = "test_custom_integration"
        unregister_integration(self.name)
    def tearDown(self):
        unregister_integration(self.name)
    def test_register_integration(self):
        handler = lambda parameters: "Integración ejecutada."
        register_integration(self.name, handler)
        self.assertIs(get_integrations()[self.name], handler)
    def test_registered_integration_can_be_executed(self):
        register_integration(
            self.name,
            lambda parameters: f"Hola, {parameters['name']}.",
        )
        plan = ActionPlan(
            actions=[
                Action(
                    name=self.name,
                    parameters={"name": "JARVIS"},
                )
            ],
            requires_confirmation=False,
        )
        result = _AI_CORE.execute_plan(plan)
        self.assertTrue(result.success)
        self.assertEqual(result.output, "Hola, JARVIS.")
    def test_duplicate_integration_is_rejected(self):
        register_integration(self.name, lambda parameters: "Primera.")
        with self.assertRaises(ValueError):
            register_integration(
                self.name,
                lambda parameters: "Segunda.",
            )
    def test_integration_can_be_replaced(self):
        register_integration(self.name, lambda parameters: "Primera.")
        replacement = lambda parameters: "Segunda."
        register_integration(
            self.name,
            replacement,
            replace=True,
        )
        self.assertIs(get_integrations()[self.name], replacement)
    def test_unregister_integration(self):
        register_integration(self.name, lambda parameters: "Listo.")
        self.assertTrue(unregister_integration(self.name))
        self.assertNotIn(self.name, get_integrations())
    def test_unregister_missing_integration(self):
        self.assertFalse(unregister_integration(self.name))
    def test_invalid_integration_name(self):
        with self.assertRaises(ValueError):
            register_integration("  ", lambda parameters: "")
    def test_invalid_integration_handler(self):
        with self.assertRaises(TypeError):
            register_integration(self.name, "not callable")
    def test_get_integrations_returns_copy(self):
        register_integration(self.name, lambda parameters: "Listo.")
        integrations = get_integrations()
        integrations.clear()
        self.assertIn(self.name, get_integrations())
if __name__ == "__main__":
    unittest.main()