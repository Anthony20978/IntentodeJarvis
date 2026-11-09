import unittest
from datetime import datetime
from jarvis.ai.core import AICore
from jarvis.ai.structures import (
    ActionPlan,
    InputData,
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
        self.assertEqual(plan.actions, ["show_help"])
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
if __name__ == "__main__":
    unittest.main()