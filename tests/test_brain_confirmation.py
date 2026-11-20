import unittest
from unittest.mock import patch
from src.jarvis import brain
from src.jarvis.ai.structures import (
    Action,
    ActionPlan,
    AnalysisResult,
    AnalysisBatch,
    ExecutionResult,
)
class TestBrainConfirmation(unittest.TestCase):
    def _capture_task(self, task, *args, **kwargs):
        self.submitted_tasks.append({
            "task": task,
            "args": args,
            "kwargs": kwargs,
        })
        return f"task-{len(self.submitted_tasks)}"
    def setUp(self):
        brain._PENDING_GROUP_SELECTION = None
        brain._PENDING_PLAN = None
        brain._PENDING_ACTION_INDEX = 0
        self.submit_patch = patch.object(
            brain._BACKGROUND_TASKS,
            "submit_task",
            side_effect=self._capture_task,
        )
        self.submit_task = self.submit_patch.start()
        self.submitted_tasks = []
        self.plan = ActionPlan(
            actions=[
                Action("first", {"value": "one"}),
                Action("second", {"value": "two"}),
                Action("third", {"value": "three"}),
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
            side_effect=self._execute_plan,
        )
        self.process_input = self.process_patch.start()
        self.execute_plan = self.execute_patch.start()
    @staticmethod
    def _execute_plan(plan, confirmed=False):
        names = [action.name for action in plan.actions]
        return ExecutionResult(
            success=True,
            output=f"Ejecutadas: {', '.join(names)}",
        )
    def tearDown(self):
        self.process_patch.stop()
        self.execute_patch.stop()
        self.submit_patch.stop()
        brain._PENDING_PLAN = None
        brain._PENDING_ACTION_INDEX = 0
        brain._PENDING_GROUP_SELECTION = None
    def test_plan_is_shown_before_execution(self):
        response = brain.process_command("instrucción")
        self.assertIn("PLAN DE EJECUCIÓN", response)
        self.assertIn("O = Autorizar todas", response)
        self.assertIs(brain._PENDING_PLAN, self.plan)
        self.execute_plan.assert_not_called()
    def test_s_authorizes_only_one_action(self):
        brain.process_command("instrucción")
        response = brain.process_command("S")
        self.assertIn("¿A qué grupo", response)
        self.execute_plan.assert_not_called()
        response = brain.process_command("1")
        self.assertIn("1 acción(es) enviada(s)", response)
        self.assertEqual(len(self.submitted_tasks), 1)
        task = self.submitted_tasks[0]
        self.assertEqual(task["kwargs"]["name"], "first")
        self.assertEqual(task["kwargs"]["group_id"], "default")
        task["task"]()
        self.execute_plan.assert_called_once()
        executed_plan = self.execute_plan.call_args.args[0]
        self.assertEqual(
            [action.name for action in executed_plan.actions],
            ["first"],
        )
        self.assertTrue(
            self.execute_plan.call_args.kwargs["confirmed"]
        )
    def test_o_authorizes_all_remaining_actions(self):
        brain.process_command("instrucción")
        brain.process_command("S")
        brain.process_command("1")
        self.assertEqual(len(self.submitted_tasks), 1)
        # Simular que la primera acción ya fue enviada.
        brain._PENDING_PLAN = self.plan
        brain._PENDING_ACTION_INDEX = 1
        self.execute_plan.reset_mock()
        self.submitted_tasks.clear()
        response = brain.process_command("O")
        self.assertIn("¿A qué grupo", response)
        response = brain.process_command("1")
        self.assertIn("2 acción(es) enviada(s)", response)
        self.assertEqual(len(self.submitted_tasks), 2)
        for task in self.submitted_tasks:
            task["task"]()
        self.assertEqual(self.execute_plan.call_count, 2)
        executed_names = [
            call.args[0].actions[0].name
            for call in self.execute_plan.call_args_list
        ]
        self.assertEqual(executed_names, ["second", "third"])
    def test_o_authorizes_all_actions_from_the_beginning(self):
        brain.process_command("instrucción")
        brain.process_command("O")
        response = brain.process_command("1")
        self.assertIn("3 acción(es) enviada(s)", response)
        self.assertEqual(len(self.submitted_tasks), 3)
        for task in self.submitted_tasks:
            task["task"]()
        self.assertEqual(self.execute_plan.call_count, 3)
        executed_names = [
            call.args[0].actions[0].name
            for call in self.execute_plan.call_args_list
        ]
        self.assertEqual(executed_names, ["first", "second", "third"])
        self.assertIsNone(brain._PENDING_PLAN)
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
        brain.process_command("S")
        brain.process_command("1")
        self.assertEqual(len(self.submitted_tasks), 1)
        with self.assertRaisesRegex(RuntimeError, "Acción rechazada"):
            self.submitted_tasks[0]["task"]()
        self.assertIsNone(brain._PENDING_PLAN)
        self.assertEqual(brain._PENDING_ACTION_INDEX, 0)
    def test_analysis_batch_supports_multiple_actions(self):
        self.analysis = AnalysisBatch(results=[
            AnalysisResult("integration", confidence=1.0, understood=True),
            AnalysisResult("integration", confidence=1.0, understood=True),
            AnalysisResult("integration", confidence=1.0, understood=True),
        ])
        self.process_input.return_value = (self.analysis, self.plan)
        response = brain.process_command("tres instrucciones")
        self.assertIn("PLAN DE EJECUCIÓN", response)
        self.assertIs(brain._PENDING_PLAN, self.plan)
        self.execute_plan.assert_not_called()
    def test_batch_with_unknown_and_recognized_instructions(self):
        self.analysis = AnalysisBatch(results=[
            AnalysisResult("unknown", understood=False),
            AnalysisResult("integration", confidence=1.0, understood=True),
        ])
        self.process_input.return_value = (self.analysis, self.plan)
        response = brain.process_command("instrucciones combinadas")
        self.assertIn("PLAN DE EJECUCIÓN", response)
        self.assertIs(brain._PENDING_PLAN, self.plan)
        self.execute_plan.assert_not_called()
    def test_batch_without_understood_instructions(self):
        self.analysis = AnalysisBatch(results=[
            AnalysisResult("unknown", understood=False),
            AnalysisResult("unknown", understood=False),
        ])
        self.process_input.return_value = (self.analysis, self.plan)
        self.plan = ActionPlan(
            actions=[],
            requires_confirmation=False,
            reason="No hay acciones válidas.",
        )
        self.process_input.return_value = (self.analysis, self.plan)
        response = brain.process_command("instrucciones desconocidas")
        self.assertIn("no tengo una función", response)
        self.assertIsNone(brain._PENDING_PLAN)
        self.execute_plan.assert_not_called()
    def test_batch_of_safe_intents_does_not_require_confirmation(self):
        self.analysis = AnalysisBatch(results=[
            AnalysisResult("help", confidence=1.0, understood=True),
            AnalysisResult("recall", confidence=1.0, understood=True),
        ])
        self.process_input.return_value = (self.analysis, self.plan)
        response = brain.process_command("ayuda y recupera información")
        self.execute_plan.assert_called_once()
        self.assertFalse(
            self.execute_plan.call_args.kwargs["confirmed"]
        )
        self.assertIsNone(brain._PENDING_PLAN)
    def test_batch_with_remember_and_recall_requires_confirmation(self):
        self.analysis = AnalysisBatch(results=[
            AnalysisResult("recall", confidence=1.0, understood=True),
            AnalysisResult("remember", confidence=1.0, understood=True),
        ])
        self.process_input.return_value = (self.analysis, self.plan)
        response = brain.process_command("recupera y recuerda")
        self.assertIn("PLAN DE EJECUCIÓN", response)
        self.assertIs(brain._PENDING_PLAN, self.plan)
        self.execute_plan.assert_not_called()
if __name__ == "__main__":
    unittest.main()