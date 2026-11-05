import unittest
from jarvis.ai.language import (
    normalize_text,
    tokenize,
    prepare_text,
)
class TestLanguage(unittest.TestCase):
    def test_normalize_text(self):
        self.assertEqual(
            normalize_text("  HOLA   Jarvis  "),
            "hola jarvis",
        )
    def test_tokenize(self):
        self.assertEqual(
            tokenize("Hola, Jarvis!"),
            ["hola", ",", "jarvis", "!"],
        )
    def test_prepare_text(self):
        self.assertEqual(
            prepare_text("  Hola   Jarvis  "),
            "hola jarvis",
        )
    def test_invalid_input(self):
        with self.assertRaises(TypeError):
            normalize_text(123)
if __name__ == "__main__":
    unittest.main()