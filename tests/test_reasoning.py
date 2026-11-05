import unittest
from jarvis.ai.reasoning import create_action_plan
from jarvis.ai.structures import AnalysisResult, ActionPlan
class TestReasoning(unittest.TestCase):
    def test_help_plan(self):
        analysis = AnalysisResult(
            intent="help",
            confidence=1.0,
            understood=True,
        )
        plan = create_action_plan(analysis)
        self.assertEqual(plan.actions, ["show_help"])
    def test_remember_plan(self):
        analysis = AnalysisResult(
            intent="remember",
            entities={"key": "nombre", "value": "Jarvis"},
            confidence=1.0,
            understood=True,
        )
        plan = create_action_plan(analysis)
        self.assertEqual(plan.actions, ["store_memory"])
        self.assertEqual(plan.parameters["key"], "nombre")
        self.assertTrue(plan.requires_confirmation)
    def test_unknown_plan(self):
        analysis = AnalysisResult(
            intent="unknown",
            understood=False,
        )
        plan = create_action_plan(analysis)
        self.assertEqual(plan.actions, [])
    def test_default_confirmation(self):
        plan = ActionPlan()
        self.assertTrue(plan.requires_confirmation)
    def test_invalid_input(self):
        with self.assertRaises(TypeError):
            create_action_plan("ayuda")
if __name__ == "__main__":
    unittest.main()