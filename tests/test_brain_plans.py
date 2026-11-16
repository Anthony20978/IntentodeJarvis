import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
from src.jarvis import brain
from src.jarvis.ai.structures import Action, ActionPlan
from src.jarvis.plan_store import PlanStore as RealPlanStore
class TestBrainPlans(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "jarvis.db"
        # Todas las operaciones utilizarán una base de datos temporal.
        self.plan_store_patch = patch.object(
            brain,
            "PlanStore",
            side_effect=lambda: RealPlanStore(self.database_path),
        )
        self.plan_store_patch.start()
        self.original_ai_core = brain._AI_CORE
        self.mock_ai_core = Mock()
        self.mock_ai_core.execute_plan.return_value = SimpleNamespace(
            success=True,
            output="Acción ejecutada.",
            error="",
        )
        brain._AI_CORE = self.mock_ai_core
        brain._PENDING_PLAN = None
        brain._PENDING_ACTION_INDEX = 0
        brain._PENDING_OPERATION = None
        self.plan = ActionPlan(
            actions=[
                Action(
                    name="weather",
                    parameters={"city": "San José"},
                ),
                Action(
                    name="show_help",
                    parameters={},
                ),
            ],
            parameters={},
            requires_confirmation=True,
            reason="Consultar información.",
        )
    def tearDown(self):
        brain._PENDING_PLAN = None
        brain._PENDING_ACTION_INDEX = 0
        brain._PENDING_OPERATION = None
        brain._AI_CORE = self.original_ai_core
        self.plan_store_patch.stop()
        self.temp_dir.cleanup()
    def _save_plan(self, name="Mi plan"):
        with RealPlanStore(self.database_path) as store:
            store.save_plan(name, self.plan)
    def test_list_empty_plans(self):
        result = brain.process_command("ver planes")
        self.assertEqual(result, "No hay planes guardados.")
    def test_list_saved_plans(self):
        self._save_plan("Mi plan")
        result = brain.process_command("ver planes")
        self.assertIn("Mi plan", result)
        self.assertIn("Consultar información.", result)
    def test_save_pending_plan(self):
        brain._PENDING_PLAN = self.plan
        result = brain.process_command("G")
        self.assertIn("nombre", result.lower())
        result = brain.process_command("Plan nuevo")
        self.assertIn("Plan guardado", result)
        with RealPlanStore(self.database_path) as store:
            saved_plan = store.get_plan("Plan nuevo")
        self.assertEqual(saved_plan, self.plan)
    def test_edit_plan_parameter(self):
        self._save_plan()
        result = brain.process_command("editar_plan Mi plan")
        self.assertIn("Acciones", result)
        result = brain.process_command("1.city")
        self.assertIn("Nuevo valor", result)
        result = brain.process_command("Heredia")
        self.assertIn("actualizado", result)
        with RealPlanStore(self.database_path) as store:
            updated_plan = store.get_plan("Mi plan")
        self.assertEqual(
            updated_plan.actions[0].parameters["city"],
            "Heredia",
        )
    def test_edit_invalid_parameter(self):
        self._save_plan()
        brain.process_command("editar_plan Mi plan")
        result = brain.process_command("1.invalid")
        self.assertIn("no existe", result)
    def test_edit_missing_plan(self):
        result = brain.process_command("editar_plan Inexistente")
        self.assertIn("No existe", result)
    def test_delete_existing_plan(self):
        self._save_plan()
        result = brain.process_command("eliminar_plan Mi plan")
        self.assertIn("eliminado", result)
        with RealPlanStore(self.database_path) as store:
            self.assertIsNone(store.get_plan("Mi plan"))
    def test_delete_missing_plan(self):
        result = brain.process_command("eliminar_plan Inexistente")
        self.assertIn("No existe", result)
    def test_execute_plan_requires_confirmation(self):
        self._save_plan()
        result = brain.process_command("ejecutar_plan Mi plan")
        self.assertIn("PLAN DE EJECUCIÓN", result)
        self.assertIsNotNone(brain._PENDING_PLAN)
        self.mock_ai_core.execute_plan.assert_not_called()
    def test_execute_plan_one_action_at_a_time(self):
        self._save_plan()
        brain.process_command("ejecutar_plan Mi plan")
        result = brain.process_command("S")
        self.assertIn("Acción ejecutada", result)
        self.assertIsNotNone(brain._PENDING_PLAN)
        self.assertEqual(
            self.mock_ai_core.execute_plan.call_count,
            1,
        )
        result = brain.process_command("S")
        self.assertIn("Todas las acciones", result)
        self.assertIsNone(brain._PENDING_PLAN)
        self.assertEqual(
            self.mock_ai_core.execute_plan.call_count,
            2,
        )
    def test_cancel_pending_plan_execution(self):
        self._save_plan()
        brain.process_command("ejecutar_plan Mi plan")
        result = brain.process_command("N")
        self.assertIn("Plan cancelado", result)
        self.assertIsNone(brain._PENDING_PLAN)
        self.mock_ai_core.execute_plan.assert_not_called()
    def test_invalid_confirmation_does_not_execute_plan(self):
        self._save_plan()
        brain.process_command("ejecutar_plan Mi plan")
        result = brain.process_command("tal vez")
        self.assertIn("Respuesta no válida", result)
        self.assertIsNotNone(brain._PENDING_PLAN)
        self.mock_ai_core.execute_plan.assert_not_called()
if __name__ == "__main__":
    unittest.main()
