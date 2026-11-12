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
    def test_unknown_plan_preserves_context(self):
        context_text = (
            "Usuario: Me interesa Python\n"
            "JARVIS: Python es un lenguaje de programación"
        )
        analysis = AnalysisResult(
            intent="unknown",
            entities={"conversation_context": context_text},
            understood=False,
        )
        plan = create_action_plan(analysis)
        self.assertEqual(plan.actions, [])
        self.assertEqual(
            plan.parameters["conversation_context"],
            context_text,
        )
        self.assertFalse(plan.requires_confirmation)
    def test_low_confidence_does_not_propose_action(self):
        analysis = AnalysisResult(
            intent="help",
            confidence=0.3,
            understood=True,
        )
        plan = create_action_plan(analysis)
        self.assertEqual(plan.actions, [])
        self.assertFalse(plan.requires_confirmation)
        self.assertIn("confianza", plan.reason)
    def test_confidence_at_threshold_allows_action(self):
        analysis = AnalysisResult(
            intent="help",
            confidence=0.5,
            understood=True,
        )
        plan = create_action_plan(analysis)
        self.assertEqual(plan.actions, ["show_help"])
    def test_custom_minimum_confidence(self):
        analysis = AnalysisResult(
            intent="help",
            confidence=0.7,
            understood=True,
        )
        plan = create_action_plan(analysis, min_confidence=0.8)
        self.assertEqual(plan.actions, [])
    def test_invalid_minimum_confidence(self):
        analysis = AnalysisResult(
            intent="help",
            confidence=1.0,
            understood=True,
        )
        for value in (-0.1, 1.1, float("nan"), True, "0.5"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    create_action_plan(analysis, min_confidence=value)
    def test_invalid_analysis_confidence(self):
        for value in (-0.1, 1.1, float("inf"), True, "alta"):
            with self.subTest(value=value):
                analysis = AnalysisResult(
                    intent="help",
                    confidence=value,
                    understood=True,
                )
                with self.assertRaises(ValueError):
                    create_action_plan(analysis)
    def test_integration_plan_uses_requested_handler(self):
        analysis = AnalysisResult(
            intent="integration",
            entities={"integration": "show_status"},
            confidence=1.0,
            understood=True,
        )
        plan = create_action_plan(analysis)
        self.assertEqual(plan.actions, ["show_status"])
        self.assertEqual(plan.parameters["integration"], "show_status")
        self.assertTrue(plan.requires_confirmation)
    def test_integration_plan_rejects_missing_name(self):
        analysis = AnalysisResult(
            intent="integration",
            confidence=1.0,
            understood=True,
        )
        plan = create_action_plan(analysis)
        self.assertEqual(plan.actions, [])
        self.assertFalse(plan.requires_confirmation)
        self.assertIn("integración", plan.reason)
    def test_integration_plan_rejects_invalid_name(self):
        for value in (None, "", "   ", 123):
            with self.subTest(value=value):
                analysis = AnalysisResult(
                    intent="integration",
                    entities={"integration": value},
                    confidence=1.0,
                    understood=True,
                )
                plan = create_action_plan(analysis)
                self.assertEqual(plan.actions, [])
                self.assertFalse(plan.requires_confirmation)
if __name__ == "__main__":
    unittest.main()