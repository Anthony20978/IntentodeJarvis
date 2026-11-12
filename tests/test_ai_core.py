import unittest
from datetime import datetime
from jarvis.ai.core import AICore
from jarvis.ai.structures import (
    ActionPlan,
    AnalysisResult,
    InputData,
    AnalysisBatch
)
class TestAICore(unittest.TestCase):
    def setUp(self):
        self.handlers = {
            "show_help": lambda parameters: "Ayuda disponible.",
        }
        self.ai = AICore(handlers=self.handlers)
    def create_input(self, text):
        return InputData(
            text=text,
            timestamp=datetime(2026, 1, 1),
            source="test",
        )
    def test_process_input(self):
        analysis, plan = self.ai.process_input(
            self.create_input("ayuda")
        )
        self.assertEqual(analysis.intent, "help")
        self.assertEqual(plan.actions[0].name, "show_help")
        self.assertEqual(len(plan.actions), 1)
        self.assertEqual(plan.actions[0].name, "show_help")
    def test_unknown_intent(self):
        analysis, plan = self.ai.process_input(
            self.create_input("algo desconocido")
        )
        self.assertFalse(analysis.understood)
        self.assertEqual(plan.actions, [])
    def test_add_input_history(self):
        self.ai.process_input(self.create_input("ayuda"))
        self.assertEqual(len(self.ai.get_history()), 1)
    def test_history_limit(self):
        ai = AICore(max_history=2)
        for text in ["ayuda", "salir", "ayuda"]:
            ai.process_input(self.create_input(text))
        self.assertEqual(len(ai.get_history()), 2)
    def test_clear_history(self):
        self.ai.process_input(self.create_input("ayuda"))
        self.ai.clear_history()
        self.assertEqual(self.ai.get_history(), [])
    def test_execute_confirmed_action(self):
        _, plan = self.ai.process_input(
            self.create_input("ayuda")
        )
        result = self.ai.execute_plan(plan, confirmed=True)
        self.assertTrue(result.success)
        self.assertEqual(result.output, "Ayuda disponible.")
    def test_confirmation_required(self):
        _, plan = self.ai.process_input(
            self.create_input("ayuda")
        )
        result = self.ai.execute_plan(plan)
        self.assertFalse(result.success)
        self.assertEqual(
            result.error,
            "La acción requiere confirmación.",
        )
    def test_invalid_input(self):
        with self.assertRaises(TypeError):
            self.ai.process_input("ayuda")
    def test_invalid_handlers(self):
        with self.assertRaises(TypeError):
            AICore(handlers="invalid")
    def test_invalid_plan(self):
        with self.assertRaises(TypeError):
            self.ai.execute_plan("invalid")
    def test_find_relevant_context(self):
        expected = self.create_input("Python local memory")
        self.ai._context.add_input(expected)
        result = self.ai.find_relevant_context("Python memory")
        self.assertEqual(result, [expected])
    def test_find_relevant_context_forwards_min_score(self):
        strong = self.create_input("Python local memory")
        weak = self.create_input("Python")
        self.ai._context.add_input(strong)
        self.ai._context.add_input(weak)
        result = self.ai.find_relevant_context(
            "Python local memory",
            min_score=0.6,
        )
        self.assertEqual(result, [strong])
    def test_get_relevant_context_returns_text(self):
        self.ai._context.add_input(
            InputData(
                text="Python local memory",
                timestamp=datetime(2026, 1, 1),
                source="user",
            )
        )
        result = self.ai.get_relevant_context("Python memory")
        self.assertEqual(result, "Usuario: Python local memory")
        self.assertIsInstance(result, str)
    def test_get_relevant_context_forwards_min_score(self):
        self.ai._context.add_input(
            self.create_input("Python local memory")
        )
        self.ai._context.add_input(self.create_input("Python"))
        result = self.ai.get_relevant_context(
            "Python local memory",
            min_score=0.6,
        )
        self.assertEqual(result, "Test: Python local memory")
    def test_process_input_uses_conversation_context(self):
        self.ai.process_input(
            InputData(
                text="Me interesa Python",
                timestamp=datetime(2026, 1, 1),
                source="user",
            )
        )
        analysis, _ = self.ai.process_input(
            InputData(
                text="Háblame de Python",
                timestamp=datetime(2026, 1, 1),
                source="user",
            )
        )
        self.assertIn(
            "conversation_context",
            analysis.entities,
        )
        self.assertIn(
            "Me interesa Python",
            analysis.entities["conversation_context"],
        )
    def test_get_relevant_context_returns_formatted_text(self):
        self.ai.process_input(
            InputData(
                text="Me interesa Python",
                timestamp=datetime(2026, 1, 1),
                source="user",
            )
        )
        result = self.ai.get_relevant_context("Python")
        self.assertIsInstance(result, str)
        self.assertEqual(result, "Usuario: Me interesa Python")
    def test_get_relevant_context_respects_min_score(self):
        self.ai.process_input(
            InputData(
                text="Python memoria local",
                timestamp=datetime(2026, 1, 1),
                source="user",
            )
        )
        result = self.ai.get_relevant_context(
            "Python memoria local",
            min_score=0.8,
        )
        self.assertEqual(result, "Usuario: Python memoria local")
    def test_process_input_returns_analysis_batch(self):
        data = InputData(
            text=(
                "Recuerda proyecto: JARVIS "
                "y recuerda lenguaje: Python"
            ),
            timestamp=datetime.now(),
            source="user",
        )
        analysis, plan = self.ai.process_input(data)
        self.assertIsInstance(analysis, AnalysisBatch)
        self.assertEqual(len(analysis.results), 2)
        self.assertEqual(len(plan.actions), 2)
    def test_process_input_preserves_single_analysis(self):
        data = InputData(
            text="Recuerda proyecto: JARVIS",
            timestamp=datetime.now(),
            source="user",
        )
        analysis, plan = self.ai.process_input(data)
        self.assertIsInstance(analysis, AnalysisResult)
        self.assertEqual(len(plan.actions), 1)
if __name__ == "__main__":
    unittest.main()