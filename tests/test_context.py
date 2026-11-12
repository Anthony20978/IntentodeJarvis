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
    def test_find_relevant_matches_case_insensitively(self):
        context = ConversationContext()
        expected = self.create_input("Python local memory")
        context.add_input(expected)
        context.add_input(self.create_input("JavaScript web browser"))
        result = context.find_relevant("PYTHON MEMORY")
        self.assertEqual(result, [expected])
    def test_find_relevant_respects_min_score(self):
        context = ConversationContext()
        strong = self.create_input("Python local memory")
        weak = self.create_input("Python")
        context.add_input(strong)
        context.add_input(weak)
        result = context.find_relevant(
            "Python local memory",
            min_score=0.6,
        )
        self.assertEqual(result, [strong])
    def test_find_relevant_respects_limit(self):
        context = ConversationContext()
        context.add_input(self.create_input("Python memory"))
        second = self.create_input("Python memory storage")
        context.add_input(second)
        result = context.find_relevant("Python memory", limit=1)
        self.assertEqual(1, len(result))
        self.assertEqual(result, [second])
    def test_find_relevant_empty_or_unmatched_query(self):
        context = ConversationContext()
        context.add_input(self.create_input("Python memory"))
        self.assertEqual(context.find_relevant("   "), [])
        self.assertEqual(
            context.find_relevant("unrelated words"),
            [],
        )
    def test_find_relevant_invalid_query(self):
        context = ConversationContext()
        with self.assertRaises(TypeError):
            context.find_relevant(None)
    def test_find_relevant_invalid_min_score_type(self):
        context = ConversationContext()
        with self.assertRaises(TypeError):
            context.find_relevant("Python", min_score=True)
    def test_find_relevant_invalid_min_score_range(self):
        context = ConversationContext()
        for score in (-0.1, 1.1):
            with self.subTest(score=score):
                with self.assertRaises(ValueError):
                    context.find_relevant("Python", min_score=score)
    def test_get_relevant_context_formats_results(self):
        context = ConversationContext()
        context.add_input(
            InputData(
                text="Python local memory",
                timestamp=datetime.now(),
                source="user",
            )
        )
        result = context.get_relevant_context("Python memory")
        self.assertEqual(
            result,
            "Usuario: Python local memory",
        )
    def test_get_relevant_context_respects_min_score(self):
        context = ConversationContext()
        context.add_input(self.create_input("Python local memory"))
        context.add_input(self.create_input("Python"))
        result = context.get_relevant_context(
            "Python local memory",
            min_score=0.6,
        )
        self.assertEqual(result, "Test: Python local memory")
if __name__ == "__main__":
    unittest.main()