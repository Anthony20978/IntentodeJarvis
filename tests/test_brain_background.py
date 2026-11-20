import unittest
from threading import Event
from src.jarvis import brain
from src.jarvis.ai.background_tasks import (
    BackgroundTaskManager,
    TaskStatus,
)
class TestBrainBackground(unittest.TestCase):
    def setUp(self):
        self.original_manager = brain._BACKGROUND_TASKS
        self.manager = BackgroundTaskManager()
        brain._BACKGROUND_TASKS = self.manager
    def tearDown(self):
        self.manager.shutdown()
        brain._BACKGROUND_TASKS = self.original_manager
    def test_create_group(self):
        group_id = brain.create_task_group("Trabajo", 2)
        group = self.manager.get_group(group_id)
        self.assertEqual(group.name, "Trabajo")
        self.assertEqual(group.max_workers, 2)
    def test_list_groups(self):
        brain.create_task_group("Trabajo")
        response = brain.list_task_groups()
        self.assertIn("Trabajo", response)
        self.assertIn("General", response)
    def test_configure_group(self):
        group_id = brain.create_task_group("Trabajo", 1)
        result = brain.configure_task_group(group_id, 3)
        self.assertTrue(result)
        self.assertEqual(
            self.manager.get_group(group_id).max_workers,
            3,
        )
    def test_delete_group(self):
        group_id = brain.create_task_group("Temporal")
        result = brain.delete_task_group(group_id)
        self.assertTrue(result)
    def test_submit_task_to_selected_group(self):
        group_id = brain.create_task_group("Trabajo")
        task_id = brain.submit_background_task(
            lambda: 20 + 5,
            name="Suma",
            group=group_id,
        )
        self.manager.shutdown()
        task = self.manager.get_task(task_id)
        self.assertEqual(task.group_id, group_id)
        self.assertEqual(task.result, 25)
        self.assertEqual(task.status, TaskStatus.COMPLETED)
    def test_list_group_tasks(self):
        group_id = brain.create_task_group("Trabajo")
        brain.submit_background_task(
            lambda: "Terminado",
            name="Proceso",
            group=group_id,
        )
        self.manager.shutdown()
        response = brain.list_group_tasks(group_id)
        self.assertIn("Proceso", response)
        self.assertIn("completed", response)
    def test_cannot_delete_group_with_active_task(self):
        group_id = brain.create_task_group("Ocupado", 1)
        started = Event()
        release = Event()
        def blocking_task():
            started.set()
            release.wait()
        try:
            brain.submit_background_task(
                blocking_task,
                group=group_id,
            )
            self.assertTrue(started.wait(timeout=2))
            result = brain.delete_task_group(group_id)
            self.assertFalse(result)
        finally:
            release.set()
    def test_create_group_command(self):
        response = brain.process_command(
            "crear grupo Temporizadores con 2 trabajadores"
        )
        self.assertIn("Grupo 'Temporizadores' creado", response)
        self.assertEqual(len(self.manager.get_groups()), 2)
    def test_list_groups_command(self):
        brain.create_task_group("Personal")
        response = brain.process_command("ver grupos")
        self.assertIn("Personal", response)
    def test_rejects_unknown_group(self):
        with self.assertRaises(KeyError):
            brain.submit_background_task(
                lambda: None,
                group="inexistente",
            )
if __name__ == "__main__":
    unittest.main()