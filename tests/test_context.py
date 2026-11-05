import unittest
from datetime import datetime
from jarvis.ai.context import ConversationContext
from jarvis.ai.structures import InputData
class TestConversationContext(unittest.TestCase):
    def create_input(self, text):
        return InputData(
            text=text,
            timestamp=datetime.now(),
            source="test",
        )
    def test_add_input(self):
        context = ConversationContext()
        context.add_input(self.create_input("Hola"))
        self.assertEqual(len(context.get_recent()), 1)
    def test_get_recent(self):
        context = ConversationContext()
        context.add_input(self.create_input("Hola"))
        context.add_input(self.create_input("¿Cómo estás?"))
        result = context.get_recent(1)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "¿Cómo estás?")
    def test_max_history(self):
        context = ConversationContext(max_history=2)
        context.add_input(self.create_input("Uno"))
        context.add_input(self.create_input("Dos"))
        context.add_input(self.create_input("Tres"))
        result = context.get_recent()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].text, "Dos")
    def test_clear(self):
        context = ConversationContext()
        context.add_input(self.create_input("Hola"))
        context.clear()
        self.assertEqual(len(context.get_recent()), 0)
    def test_invalid_input(self):
        context = ConversationContext()
        with self.assertRaises(TypeError):
            context.add_input("Hola")
    def test_invalid_history_limit(self):
        with self.assertRaises(ValueError):
            ConversationContext(max_history=0)
if __name__ == "__main__":
    unittest.main()