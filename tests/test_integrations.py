import unittest
from jarvis.ai.integrations_registry import IntegrationRegistry
class TestIntegrationRegistry(unittest.TestCase):
    def setUp(self):
        self.registry = IntegrationRegistry({
            "help": lambda parameters: "Ayuda disponible.",
            
        },auto_discover=False)
    def test_register_and_get_handler(self):
        handler = lambda parameters: "Listo."
        self.registry.register("status", handler)
        self.assertIs(self.registry.get_handler("status"), handler)
    def test_register_rejects_empty_name(self):
        with self.assertRaises(ValueError):
            self.registry.register("  ", lambda parameters: "")
    def test_register_rejects_non_callable(self):
        with self.assertRaises(TypeError):
            self.registry.register("status", "not callable")
    def test_register_rejects_duplicate_without_replace(self):
        with self.assertRaises(ValueError):
            self.registry.register("help", lambda parameters: "Otra ayuda.")
    def test_register_can_replace_handler(self):
        handler = lambda parameters: "Nueva ayuda."
        self.registry.register("help", handler, replace=True)
        self.assertIs(self.registry.get_handler("help"), handler)
    def test_unregister_existing_handler(self):
        self.assertTrue(self.registry.unregister("help"))
        self.assertFalse(self.registry.has_handler("help"))
    def test_unregister_missing_handler(self):
        self.assertFalse(self.registry.unregister("missing"))
    def test_get_handlers_returns_copy(self):
        handlers = self.registry.get_handlers()
        handlers.clear()
        self.assertTrue(self.registry.has_handler("help"))
    def test_invalid_initial_handlers(self):
        with self.assertRaises(TypeError):
            IntegrationRegistry("invalid")
    def test_invalid_replace_flag(self):
        with self.assertRaises(TypeError):
            self.registry.register(
                "status",
                lambda parameters: "",
                replace=1,
            )
    def test_length(self):

        self.assertEqual(len(self.registry), 1)
    def test_register_definition(self):
        from jarvis.ai.structures import (
            IntegrationDefinition,
            IntegrationParameter,
        )
        definition = IntegrationDefinition(
            name="calculate",
            description="Calculadora.",
            version="1.0.0",
            parameters=[
                IntegrationParameter(
                    name="expression",
                    description="Expresión matemática.",
                    type=str,
                    flag="-x"
                )
            ],
            handler=lambda parameters: "2",
        )
        self.registry.register_definition(definition)
        self.assertIs(
            self.registry.get_handler("calculate"),
            definition.handler,
        )
        self.assertIs(
            self.registry.get_definition("calculate"),
            definition,
        )
    def test_register_definition_rejects_invalid_type(self):
        with self.assertRaises(TypeError):
            self.registry.register_definition("invalid")
    def test_get_definition(self):
        from jarvis.ai.structures import IntegrationDefinition
        definition = IntegrationDefinition(
            name="calculate",
            description="Calculadora.",
            version="1.0.0",
            handler=lambda parameters: "2",
        )
        self.registry.register_definition(definition)
        self.assertIs(
            self.registry.get_definition("calculate"),
            definition,
        )
    def test_get_definitions_returns_copy(self):
        definitions = self.registry.get_definitions()
        definitions.clear()
        self.assertEqual(self.registry.get_definitions(), {})
    def test_unregister_removes_definition(self):
        from jarvis.ai.structures import IntegrationDefinition
        definition = IntegrationDefinition(
            name="calculate",
            description="Calculadora.",
            version="1.0.0",
            handler=lambda parameters: "2",
        )
        self.registry.register_definition(definition)
        self.assertTrue(self.registry.unregister("calculate"))
        self.assertIsNone(self.registry.get_definition("calculate"))
    def test_get_discovery_errors_returns_copy(self):
        errors = self.registry.get_discovery_errors()
        errors["fake"] = "Error"
        self.assertNotIn("fake", self.registry.get_discovery_errors())
if __name__ == "__main__":
    unittest.main()