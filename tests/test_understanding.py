import unittest
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
if __name__ == "__main__":
    unittest.main()