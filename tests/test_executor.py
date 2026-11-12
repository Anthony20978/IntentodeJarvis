import unittest
from jarvis.ai.executor import execute_action_plan
from jarvis.ai.structures import Action, ActionPlan
class TestExecutor(unittest.TestCase):
    def setUp(self):
        self.handlers = {
            "show_help": lambda parameters: "Ayuda disponible.",
            "store_memory": lambda parameters: (
                f"Guardado: {parameters['key']}"
            ),
        }
    def test_execute_confirmed_action(self):
        plan = ActionPlan(actions=[Action(name="show_help")])
        result = execute_action_plan(
            plan, self.handlers, confirmed=True
        )
        self.assertTrue(result.success)
        self.assertEqual(result.output, "Ayuda disponible.")
    def test_confirmation_required(self):
        plan = ActionPlan(actions=[Action(name="show_help")])
        result = execute_action_plan(plan, self.handlers)
        self.assertFalse(result.success)
        self.assertEqual(
            result.error,
            "La acción requiere confirmación.",
        )
    def test_execute_with_parameters(self):
        plan = ActionPlan(
            actions=[
                Action(
                    name="store_memory",
                    parameters={"key": "nombre"},
                )
            ]
        )
        result = execute_action_plan(
            plan, self.handlers, confirmed=True
        )
        self.assertTrue(result.success)
        self.assertEqual(result.output, "Guardado: nombre")
    def test_actions_use_independent_parameters(self):
        received = []
        handlers = {
            "first": lambda parameters: (
                received.append(parameters) or "Primera"
            ),
            "second": lambda parameters: (
                received.append(parameters) or "Segunda"
            ),
        }
        plan = ActionPlan(
            actions=[
                Action(name="first", parameters={"value": 1}),
                Action(name="second", parameters={"value": 2}),
            ]
        )
        result = execute_action_plan(
            plan, handlers, confirmed=True
        )
        self.assertTrue(result.success)
        self.assertEqual(
            received,
            [{"value": 1}, {"value": 2}],
        )
    def test_unknown_action(self):
        plan = ActionPlan(
            actions=[Action(name="unknown_action")]
        )
        result = execute_action_plan(
            plan, self.handlers, confirmed=True
        )
        self.assertFalse(result.success)
        self.assertIn("Acción no disponible", result.error)
    def test_empty_plan(self):
        result = execute_action_plan(
            ActionPlan(), self.handlers
        )
        self.assertFalse(result.success)
        self.assertEqual(
            result.error,
            "El plan no contiene acciones.",
        )
    def test_execution_error(self):
        def failing_action(parameters):
            raise ValueError("Error de prueba")
        plan = ActionPlan(
            actions=[Action(name="failing_action")]
        )
        result = execute_action_plan(
            plan,
            {"failing_action": failing_action},
            confirmed=True,
        )
        self.assertFalse(result.success)
        self.assertIn("Error de prueba", result.error)
    def test_invalid_plan(self):
        with self.assertRaises(TypeError):
            execute_action_plan("invalid", self.handlers)
    def test_invalid_confirmation(self):
        plan = ActionPlan(
            actions=[Action(name="show_help")]
        )
        with self.assertRaises(TypeError):
            execute_action_plan(
                plan, self.handlers, confirmed="yes"
            )
if __name__ == "__main__":
    unittest.main()