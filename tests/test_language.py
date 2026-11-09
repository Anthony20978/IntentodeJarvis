import unittest
from jarvis.ai.language import normalize_for_matching 
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
    def test_normalize_for_matching(self):
        self.assertEqual(
            normalize_for_matching("Música"),
            "musica",
        )
    def test_normalize_for_matching_preserves_enye(self):
        self.assertEqual(
            normalize_for_matching("Niño"),
            "niño",
        )
    def test_normalize_for_matching_preserves_umlaut(self):
        self.assertEqual(
            normalize_for_matching("Pingüino"),
            "pinguino",
        )
    def test_normalize_for_matching_multiple_accents(self):
        self.assertEqual(
            normalize_for_matching("Árboles y Canciones"),
            "arboles y canciones",
        )
    def test_tokenize_unicode(self):
        self.assertEqual(
            tokenize("¡Hola, niño!"),
            ["¡", "hola", ",", "niño", "!"],
        )
    def test_tokenize_empty_text(self):
        self.assertEqual(tokenize(""), [])
if __name__ == "__main__":
    unittest.main()