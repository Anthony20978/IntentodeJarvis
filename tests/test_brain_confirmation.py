import unittest
from unittest.mock import patch
from src.jarvis import brain
from src.jarvis.ai.structures import (
    Action,
    ActionPlan,
    AnalysisResult,
    ExecutionResult,
)
class TestBrainConfirmation(unittest.TestCase):
    def setUp(self):
        brain._PENDING_PLAN = None
        brain._PENDING_ACTION_INDEX = 0
        self.plan = ActionPlan(
            actions=[
                Action(name="first"),
                Action(name="second"),
                Action(name="third"),
            ],
            requires_confirmation=True,
            reason="Prueba de confirmación.",
        )
        self.analysis = AnalysisResult(
            intent="integration",
            confidence=1.0,
            understood=True,
        )
        self.process_patch = patch.object(
            brain._AI_CORE,
            "process_input",
            return_value=(self.analysis, self.plan),
        )
        self.execute_patch = patch.object(
            brain._AI_CORE,
            "execute_plan",
            side_effect=lambda plan, confirmed=False: ExecutionResult(
                success=True,
                output=f"Ejecutada: {plan.actions[0].name}",
            ),
        )
        self.process_input = self.process_patch.start()
        self.execute_plan = self.execute_patch.start()
    def tearDown(self):
        self.process_patch.stop()
        self.execute_patch.stop()
        brain._PENDING_PLAN = None
        brain._PENDING_ACTION_INDEX = 0
    def test_plan_is_shown_before_execution(self):
        response = brain.process_command("instrucción")
        self.assertIn("PLAN DE EJECUCIÓN", response)
        self.assertIn("O = Autorizar todas", response)
        self.assertIs(brain._PENDING_PLAN, self.plan)
        self.execute_plan.assert_not_called()
    def test_s_authorizes_only_one_action(self):
        brain.process_command("instrucción")
        response = brain.process_command("S")
        executed_plan = self.execute_plan.call_args.args[0]
        self.assertEqual(len(executed_plan.actions), 1)
        self.assertEqual(
            executed_plan.actions[0].name,
            "first",
        )
        self.assertTrue(
            self.execute_plan.call_args.kwargs["confirmed"]
        )
        self.assertIn("Siguiente acción (2/3)", response)
        self.assertIs(brain._PENDING_PLAN, self.plan)
    def test_o_authorizes_all_remaining_actions(self):
        brain.process_command("instrucción")
        brain.process_command("S")
        response = brain.process_command("O")
        executed_actions = [
            call.args[0].actions[0].name
            for call in self.execute_plan.call_args_list
        ]
        self.assertEqual(
            executed_actions,
            ["first", "second", "third"],
        )
        self.assertIn("Todas las acciones se ejecutaron", response)
        self.assertIsNone(brain._PENDING_PLAN)
        self.assertEqual(brain._PENDING_ACTION_INDEX, 0)
    def test_o_authorizes_all_actions_from_the_beginning(self):
        brain.process_command("instrucción")
        brain.process_command("O")
        executed_actions = [
            call.args[0].actions[0].name
            for call in self.execute_plan.call_args_list
        ]
        self.assertEqual(
            executed_actions,
            ["first", "second", "third"],
        )
    def test_n_cancels_remaining_actions(self):
        brain.process_command("instrucción")
        response = brain.process_command("N")
        self.assertIn("Plan cancelado", response)
        self.execute_plan.assert_not_called()
        self.assertIsNone(brain._PENDING_PLAN)
    def test_invalid_answer_keeps_plan_pending(self):
        brain.process_command("instrucción")
        response = brain.process_command("tal vez")
        self.assertIn("Respuesta no válida", response)
        self.assertIs(brain._PENDING_PLAN, self.plan)
        self.execute_plan.assert_not_called()
    def test_new_instruction_is_not_processed_while_plan_is_pending(self):
        brain.process_command("instrucción")
        response = brain.process_command(
            "recuerda color: azul"
        )
        self.assertIn("Respuesta no válida", response)
        self.process_input.assert_called_once()
        self.execute_plan.assert_not_called()
    def test_s_without_pending_plan_does_not_execute_actions(self):
        self.process_input.return_value = (
            AnalysisResult(
                intent="unknown",
                understood=False,
            ),
            ActionPlan(
                actions=[],
                requires_confirmation=False,
            ),
        )
        response = brain.process_command("S")
        self.assertIn("no tengo una función", response)
        self.execute_plan.assert_not_called()
    def test_execution_failure_clears_pending_plan(self):
        self.execute_plan.side_effect = None
        self.execute_plan.return_value = ExecutionResult(
            success=False,
            error="Acción rechazada.",
        )
        brain.process_command("instrucción")
        response = brain.process_command("S")
        self.assertIn("Acción rechazada", response)
        self.assertIsNone(brain._PENDING_PLAN)
        self.assertEqual(brain._PENDING_ACTION_INDEX, 0)
if __name__ == "__main__":
    unittest.main()