import unittest
from jarvis.ai.structures import Action, ActionPlan, AnalysisResult, AnalysisBatch
class TestActionStructures(unittest.TestCase):
    def test_action_stores_name_and_parameters(self):
        action = Action(
            name="store_memory",
            parameters={"key": "nombre", "value": "JARVIS"},
        )
        self.assertEqual(action.name, "store_memory")
        self.assertEqual(
            action.parameters,
            {"key": "nombre", "value": "JARVIS"},
        )
    def test_action_has_empty_parameters_by_default(self):
        action = Action(name="show_help")
        self.assertEqual(action.parameters, {})
    def test_actions_have_independent_parameters(self):
        first = Action(name="first")
        second = Action(name="second")
        first.parameters["value"] = 1
        self.assertEqual(first.parameters, {"value": 1})
        self.assertEqual(second.parameters, {})
    def test_action_plan_stores_multiple_actions(self):
        actions = [
            Action(name="first", parameters={"value": 1}),
            Action(name="second", parameters={"value": 2}),
        ]
        plan = ActionPlan(actions=actions)
        self.assertEqual(plan.actions, actions)
        self.assertEqual(plan.actions[0].parameters, {"value": 1})
        self.assertEqual(plan.actions[1].parameters, {"value": 2})
class TestAnalysisBatch(unittest.TestCase):
    def test_analysis_batch_accepts_multiple_results(self):
        results = [
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
        batch = AnalysisBatch(results=results)
        self.assertEqual(len(batch.results), 2)
        self.assertEqual(batch.results, results)
    def test_analysis_batch_accepts_empty_results(self):
        batch = AnalysisBatch()
        self.assertEqual(batch.results, [])
    def test_analysis_batch_rejects_non_list(self):
        with self.assertRaises(TypeError):
            AnalysisBatch(results="invalid")
    def test_analysis_batch_rejects_invalid_results(self):
        with self.assertRaises(TypeError):
            AnalysisBatch(results=[
                AnalysisResult(intent="remember"),
                "invalid",
            ])
if __name__ == "__main__":
    unittest.main()