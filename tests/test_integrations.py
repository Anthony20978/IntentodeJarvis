import unittest
from jarvis.ai.integrations import IntegrationRegistry
class TestIntegrationRegistry(unittest.TestCase):
    def setUp(self):
        self.registry = IntegrationRegistry({
            "help": lambda parameters: "Ayuda disponible.",
        })
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
if __name__ == "__main__":
    unittest.main()