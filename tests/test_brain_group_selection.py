import unittest
from unittest.mock import patch
from src.jarvis import brain
from src.jarvis.ai.background_tasks import GroupInfo
from src.jarvis.ai.structures import (
    Action,
    ActionPlan,
    AnalysisResult,
    ExecutionResult,
)
class TestBrainGroupSelection(unittest.TestCase):
    def setUp(self):
        brain._PENDING_PLAN = None
        brain._PENDING_ACTION_INDEX = 0
        brain._PENDING_GROUP_SELECTION = None
        self.groups = [
            GroupInfo("default", "General", 1, 0, 0, 0),
            GroupInfo("research", "Investigación", 2, 0, 0, 0),
            GroupInfo("timers", "Temporizadores", 3, 0, 0, 0),
        ]
        self.plan = ActionPlan(
            actions=[
                Action("first", {"value": "one"}),
                Action("second", {"value": "two"}),
            ],
            requires_confirmation=True,
            reason="Prueba de selección de grupo.",
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
            return_value=ExecutionResult(
                success=True,
                output="Acción ejecutada.",
            ),
        )
        self.groups_patch = patch.object(
            brain._BACKGROUND_TASKS,
            "get_groups",
            return_value=self.groups,
        )
        self.submit_patch = patch.object(
            brain._BACKGROUND_TASKS,
            "submit_task",
        )
        self.process_patch.start()
        self.execute_plan = self.execute_patch.start()
        self.groups_patch.start()
        self.submit_task = self.submit_patch.start()
    def tearDown(self):
        self.process_patch.stop()
        self.execute_patch.stop()
        self.groups_patch.stop()
        self.submit_patch.stop()
        brain._PENDING_PLAN = None
        brain._PENDING_ACTION_INDEX = 0
        brain._PENDING_GROUP_SELECTION = None
    def _request_group_selection(self, answer="S"):
        brain.process_command("instrucción")
        return brain.process_command(answer)
    def test_s_requests_group_selection(self):
        response = self._request_group_selection()
        self.assertIn("General", response)
        self.assertIn("Investigación", response)
        self.assertIn("Temporizadores", response)
        self.assertIsNotNone(brain._PENDING_GROUP_SELECTION)
        self.submit_task.assert_not_called()
    def test_o_requests_group_selection_for_remaining_actions(self):
        response = self._request_group_selection("O")
        self.assertIn("Investigación", response)
        self.assertIsNotNone(brain._PENDING_GROUP_SELECTION)
        self.submit_task.assert_not_called()
    def test_select_group_by_number(self):
        self._request_group_selection()
        response = brain.process_command("2")
        self.assertIn("Investigación", response)
        self.submit_task.assert_called_once()
        self.assertEqual(
            self.submit_task.call_args.kwargs["group_id"],
            "research",
        )
    def test_select_group_by_name(self):
        self._request_group_selection()
        response = brain.process_command("Temporizadores")
        self.assertIn("Temporizadores", response)
        self.submit_task.assert_called_once()
        self.assertEqual(
            self.submit_task.call_args.kwargs["group_id"],
            "timers",
        )
    def test_invalid_group_keeps_selection_pending(self):
        self._request_group_selection()
        response = brain.process_command("Grupo inexistente")
        self.assertIn("no válido", response.casefold())
        self.assertIsNotNone(brain._PENDING_GROUP_SELECTION)
        self.submit_task.assert_not_called()
    def test_cancel_group_selection(self):
        self._request_group_selection()
        response = brain.process_command("cancelar")
        self.assertIn("cancelado", response.casefold())
        self.assertIsNone(brain._PENDING_GROUP_SELECTION)
        self.submit_task.assert_not_called()
    def test_actions_are_submitted_to_selected_group(self):
        self._request_group_selection()
        brain.process_command("2")
        self.submit_task.assert_called_once()
        task_function = self.submit_task.call_args.args[0]
        self.assertTrue(callable(task_function))
        self.assertEqual(
            self.submit_task.call_args.kwargs["group_id"],
            "research",
        )
    def test_o_submits_all_remaining_actions(self):
        self._request_group_selection("O")
        brain.process_command("1")
        self.assertEqual(self.submit_task.call_count, 2)
        for call in self.submit_task.call_args_list:
            self.assertEqual(
                call.kwargs["group_id"],
                "default",
            )
if __name__ == "__main__":
    unittest.main()