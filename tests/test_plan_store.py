import tempfile
import unittest
from pathlib import Path
from jarvis.ai.structures import Action, ActionPlan
from jarvis.plan_store import PlanStore
class TestPlanStore(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "jarvis.db"
        self.store = PlanStore(self.database_path)
        self.plan = ActionPlan(
            actions=[
                Action(
                    name="store_memory",
                    parameters={"key": "nombre", "value": "JARVIS"},
                ),
                Action(name="show_help"),
            ],
            parameters={"source": "test"},
            requires_confirmation=True,
            reason="Guardar información.",
        )
    def tearDown(self):
        self.store.close()
        self.temp_dir.cleanup()
    def test_save_and_get_plan(self):
        self.store.save_plan("Mi plan", self.plan)
        retrieved = self.store.get_plan("Mi plan")
        self.assertEqual(retrieved, self.plan)
    def test_plan_persists_after_reopening_database(self):
        self.store.save_plan("Mi plan", self.plan)
        self.store.close()
        self.store = PlanStore(self.database_path)
        retrieved = self.store.get_plan("Mi plan")
        self.assertEqual(retrieved, self.plan)
    def test_list_plans(self):
        self.store.save_plan("Segundo", self.plan)
        self.store.save_plan("Primero", self.plan)
        plans = self.store.list_plans()
        self.assertEqual(
            [plan["name"] for plan in plans],
            ["Primero", "Segundo"],
        )
        self.assertIn("id", plans[0])
        self.assertIn("reason", plans[0])
        self.assertIn("created_at", plans[0])
        self.assertIn("updated_at", plans[0])
    def test_get_missing_plan(self):
        self.assertIsNone(self.store.get_plan("Inexistente"))
    def test_save_duplicate_plan(self):
        self.store.save_plan("Mi plan", self.plan)
        with self.assertRaises(ValueError):
            self.store.save_plan("Mi plan", self.plan)
    def test_update_existing_plan(self):
        self.store.save_plan("Mi plan", self.plan)
        updated_plan = ActionPlan(
            actions=[Action(name="show_help")],
            parameters={"updated": True},
            requires_confirmation=False,
            reason="Plan actualizado.",
        )
        self.assertTrue(
            self.store.update_plan("Mi plan", updated_plan)
        )
        self.assertEqual(
            self.store.get_plan("Mi plan"),
            updated_plan,
        )
    def test_update_missing_plan(self):
        self.assertFalse(
            self.store.update_plan("Inexistente", self.plan)
        )
    def test_delete_existing_plan(self):
        self.store.save_plan("Mi plan", self.plan)
        self.assertTrue(self.store.delete_plan("Mi plan"))
        self.assertIsNone(self.store.get_plan("Mi plan"))
    def test_delete_missing_plan(self):
        self.assertFalse(self.store.delete_plan("Inexistente"))
    def test_reject_empty_plan_name(self):
        with self.assertRaises(ValueError):
            self.store.save_plan("   ", self.plan)
    def test_reject_non_string_plan_name(self):
        with self.assertRaises(TypeError):
            self.store.save_plan(123, self.plan)
    def test_reject_invalid_plan_type(self):
        with self.assertRaises(TypeError):
            self.store.save_plan("Mi plan", "invalid")
    def test_reject_invalid_actions(self):
        invalid_plan = ActionPlan(actions=["invalid"])
        with self.assertRaises(TypeError):
            self.store.save_plan("Mi plan", invalid_plan)
    def test_reject_non_serializable_parameters(self):
        invalid_plan = ActionPlan(
            actions=[Action(name="show_help")],
            parameters={"invalid": object()},
        )
        with self.assertRaises(ValueError):
            self.store.save_plan("Mi plan", invalid_plan)
    def test_operations_after_closing_connection(self):
        self.store.close()
        with self.assertRaises(RuntimeError):
            self.store.get_plan("Mi plan")
if __name__ == "__main__":
    unittest.main()