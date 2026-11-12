import unittest
from jarvis.ai.reasoning import create_action_plan
from jarvis.ai.structures import AnalysisResult, ActionPlan, Action, AnalysisBatch, AnalysisResult
class TestReasoning(unittest.TestCase):
    def test_help_plan(self):
        analysis = AnalysisResult(
            intent="help",
            confidence=1.0,
            understood=True,
        )
        plan = create_action_plan(analysis)
        self.assertEqual(plan.actions[0].name, "show_help")
        self.assertEqual(plan.actions[0].parameters, {})
        self.assertTrue(plan.requires_confirmation)
        self.assertEqual(len(plan.actions), 1)
    def test_remember_plan(self):
        analysis = AnalysisResult(
            intent="remember",
            entities={"key": "nombre", "value": "Jarvis"},
            confidence=1.0,
            understood=True,
        )
        plan = create_action_plan(analysis)
        self.assertEqual(len(plan.actions), 1)
        self.assertEqual(plan.actions[0].name, "store_memory")
        self.assertEqual(
            plan.actions[0].parameters["key"],
            "nombre",
        )
        self.assertEqual(
            plan.actions[0].parameters["value"],
            "Jarvis",
        )
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
        self.assertEqual(plan.actions[0].name, "show_help")
        self.assertEqual(plan.actions[0].parameters, {})
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
        self.assertEqual(plan.actions[0].name, "show_status")
        self.assertEqual(plan.actions[0].parameters, {})
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
    def test_create_action_plan_from_multiple_analyses(self):
        batch = AnalysisBatch(
            results=[
                AnalysisResult(
                    intent="remember",
                    entities={"key": "proyecto", "value": "JARVIS"},
                    confidence=1.0,
                    understood=True,
                ),
                AnalysisResult(
                    intent="remember",
                    entities={"key": "lenguaje", "value": "Python"},
                    confidence=1.0,
                    understood=True,
                ),
            ]
        )
        plan = create_action_plan(batch)
        self.assertEqual(len(plan.actions), 2)
        self.assertEqual(plan.actions[0].name, "store_memory")
        self.assertEqual(plan.actions[1].name, "store_memory")
        self.assertEqual(
            plan.actions[0].parameters["value"],
            "JARVIS",
        )
        self.assertEqual(
            plan.actions[1].parameters["value"],
            "Python",
        )
    def test_create_action_plan_skips_unrecognized_analyses(self):
        batch = AnalysisBatch(
            results=[
                AnalysisResult(
                    intent="unknown",
                    confidence=0.0,
                    understood=False,
                ),
                AnalysisResult(
                    intent="remember",
                    entities={"key": "proyecto", "value": "JARVIS"},
                    confidence=1.0,
                    understood=True,
                ),
            ]
        )
        plan = create_action_plan(batch)
        self.assertEqual(len(plan.actions), 1)
        self.assertEqual(plan.actions[0].name, "store_memory")
if __name__ == "__main__":
    unittest.main()