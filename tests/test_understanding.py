import unittest
from unittest.mock import Mock
from datetime import datetime
from jarvis.ai.understanding import analyze_input
from jarvis.ai.structures import InputData
class TestUnderstanding(unittest.TestCase):
    def create_input(self, text):
        return InputData(
            text=text,
            timestamp=datetime.now(),
            source="test",
        )
    def test_help_intent(self):
        result = analyze_input(self.create_input("ayuda"))
        self.assertEqual(result.intent, "help")
        self.assertTrue(result.understood)
    def test_exit_intent(self):
        result = analyze_input(self.create_input("salir"))
        self.assertEqual(result.intent, "exit")
        self.assertTrue(result.understood)
    def test_remember_intent(self):
        result = analyze_input(
            self.create_input("recuerda nombre: Jarvis")
        )
        self.assertEqual(result.intent, "remember")
        self.assertEqual(result.entities["key"], "nombre")
        self.assertEqual(result.entities["value"], "Jarvis")
    def test_recall_intent(self):
        result = analyze_input(
            self.create_input("recupera nombre")
        )
        self.assertEqual(result.intent, "recall")
        self.assertEqual(result.entities["key"], "nombre")
    def test_unknown_intent(self):
        result = analyze_input(
            self.create_input("Hola Jarvis")
        )
        self.assertEqual(result.intent, "unknown")
        self.assertFalse(result.understood)
    def test_empty_input(self):
        result = analyze_input(self.create_input("   "))
        self.assertEqual(result.intent, "unknown")
        self.assertFalse(result.understood)
    def test_invalid_input(self):
        with self.assertRaises(TypeError):
            analyze_input("ayuda")
    def test_help_variations(self):
        phrases = [
            "necesito ayuda",
            "puedes ayudarme",
            "que puedes hacer",
            "qué puedes hacer",
        ]
        for phrase in phrases:
            with self.subTest(phrase=phrase):
                result = analyze_input(self.create_input(phrase))
                self.assertEqual(result.intent, "help")
                self.assertTrue(result.understood)
    def test_exit_variations(self):
        phrases = {
            "salir",
            "exit",
            "quit",
            "cerrar jarvis",
            "apagar jarvis",
            "adios",
            "adiós",
        }
        for phrase in phrases:
            with self.subTest(phrase=phrase):
                result = analyze_input(self.create_input(phrase))
                self.assertEqual(result.intent, "exit")
                self.assertTrue(result.understood)
    def test_remember_empty_key(self):
        result = analyze_input(self.create_input("recuerda : valor"))
        self.assertEqual(result.intent, "unknown")
    def test_remember_empty_value(self):
        result = analyze_input(self.create_input("recuerda nombre:"))
        self.assertEqual(result.intent, "unknown")
    def test_recall_empty_key(self):
        result = analyze_input(self.create_input("recupera"))
        self.assertEqual(result.intent, "unknown")
    def test_context_parameter_is_optional(self):
        result = analyze_input(self.create_input("Hola Jarvis"))
        self.assertEqual(result.intent, "unknown")
        self.assertNotIn("conversation_context", result.entities)
    def test_context_is_used_for_unknown_intent(self):
        context = Mock()
        context.find_relevant.return_value = []
        result = analyze_input(
            self.create_input("Háblame de Python"),
            context=context,
        )
        context.find_relevant.assert_called_once_with(
            "Háblame de Python",
            limit=5,
            min_score=0.3,
        )
        self.assertEqual(result.intent, "unknown")
    def test_relevant_context_is_added_to_entities(self):
        context = Mock()
        context.find_relevant.return_value = [
            InputData(
                text="Me interesa Python",
                timestamp=datetime.now(),
                source="user",
            ),
            InputData(
                text="Python es un lenguaje de programación",
                timestamp=datetime.now(),
                source="assistant",
            ),
        ]
        result = analyze_input(
            self.create_input("Háblame de Python"),
            context=context,
        )
        self.assertIn("conversation_context", result.entities)
        self.assertEqual(
            result.entities["conversation_context"],
            "Usuario: Me interesa Python\n"
            "JARVIS: Python es un lenguaje de programación",
        )
    def test_empty_context_does_not_add_entity(self):
        context = Mock()
        context.find_relevant.return_value = []
        result = analyze_input(
            self.create_input("Hola Jarvis"),
            context=context,
        )
        self.assertNotIn("conversation_context", result.entities)
    def test_context_is_not_used_for_known_intents(self):
        context = Mock()
        result = analyze_input(
            self.create_input("ayuda"),
            context=context,
        )
        self.assertEqual(result.intent, "help")
        context.find_relevant.assert_not_called()
    def test_context_is_not_used_for_empty_input(self):
        context = Mock()
        result = analyze_input(
            self.create_input("   "),
            context=context,
        )
        self.assertEqual(result.intent, "unknown")
        context.find_relevant.assert_not_called()
    def test_invalid_context(self):
        with self.assertRaises(TypeError):
            analyze_input(
                self.create_input("Hola Jarvis"),
                context=object(),
            )
    def test_context_preserves_original_command_behavior(self):
        context = Mock()
        result = analyze_input(
            self.create_input("recuerda nombre: Jarvis"),
            context=context,
        )
        self.assertEqual(result.intent, "remember")
        self.assertEqual(result.entities["key"], "nombre")
        self.assertEqual(result.entities["value"], "Jarvis")
        context.find_relevant.assert_not_called()
    def test_registered_integration_intent(self):
        integrations = {"show_status": lambda parameters: "Listo."}
        result = analyze_input(
            self.create_input("ejecuta show_status"),
            available_integrations=integrations,
        )
        self.assertEqual(result.intent, "integration")
        self.assertEqual(result.entities["integration"], "show_status")
        self.assertTrue(result.understood)
        self.assertEqual(result.confidence, 1.0)
    def test_registered_integration_is_case_insensitive(self):
        integrations = {"show_status": lambda parameters: "Listo."}
        result = analyze_input(
            self.create_input("EJECUTA SHOW_STATUS"),
            available_integrations=integrations,
        )
        self.assertEqual(result.intent, "integration")
        self.assertEqual(result.entities["integration"], "show_status")
    def test_unknown_integration_is_not_recognized(self):
        result = analyze_input(
            self.create_input("ejecuta delete_everything"),
            available_integrations={"show_status": lambda parameters: "Listo."},
        )
        self.assertEqual(result.intent, "unknown")
        self.assertFalse(result.understood)
    def test_integration_command_requires_registry(self):
        result = analyze_input(self.create_input("ejecuta show_status"))
        self.assertEqual(result.intent, "unknown")
        self.assertFalse(result.understood)
    def test_invalid_available_integrations(self):
        with self.assertRaises(TypeError):
            analyze_input(
                self.create_input("ejecuta show_status"),
                available_integrations=["show_status"],
            )
if __name__ == "__main__":
    unittest.main()