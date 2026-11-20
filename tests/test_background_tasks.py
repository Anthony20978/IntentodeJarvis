import unittest
from threading import Event
from jarvis.ai.background_tasks import (
    BackgroundTaskManager,
    TaskStatus,
)
class TestBackgroundTaskManager(unittest.TestCase):
    def test_executes_task_and_stores_result(self):
        manager = BackgroundTaskManager()
        try:
            task_id = manager.submit_task(lambda: 10 + 5, name="Suma")
            manager.shutdown()
            task = manager.get_task(task_id)
            self.assertEqual(task.status, TaskStatus.COMPLETED)
            self.assertEqual(task.result, 15)
            self.assertEqual(task.name, "Suma")
        finally:
            manager.shutdown()
    def test_captures_task_errors(self):
        manager = BackgroundTaskManager()
        def failing_task():
            raise ValueError("Error de prueba")
        try:
            task_id = manager.submit_task(failing_task)
            manager.shutdown()
            task = manager.get_task(task_id)
            self.assertEqual(task.status, TaskStatus.FAILED)
            self.assertEqual(task.error, "Error de prueba")
        finally:
            manager.shutdown()
    def test_executes_tasks_concurrently(self):
        manager = BackgroundTaskManager(max_workers=2)
        first_started = Event()
        second_started = Event()
        release_first = Event()
        def first_task():
            first_started.set()
            release_first.wait()
        def second_task():
            second_started.set()
        try:
            manager.submit_task(first_task)
            self.assertTrue(first_started.wait(timeout=2))
            manager.submit_task(second_task)
            self.assertTrue(second_started.wait(timeout=2))
        finally:
            release_first.set()
            manager.shutdown()
    def test_cancels_task_that_has_not_started(self):
        manager = BackgroundTaskManager(max_workers=1)
        started = Event()
        release = Event()
        def blocking_task():
            started.set()
            release.wait()
        try:
            manager.submit_task(blocking_task)
            self.assertTrue(started.wait(timeout=2))
            task_id = manager.submit_task(
                lambda: "No debería ejecutarse"
            )
            self.assertTrue(manager.cancel_task(task_id))
            release.set()
            manager.shutdown()
            task = manager.get_task(task_id)
            self.assertEqual(task.status, TaskStatus.CANCELLED)
        finally:
            release.set()
            manager.shutdown()
    def test_collects_completion_notifications(self):
        manager = BackgroundTaskManager()
        try:
            task_id = manager.submit_task(lambda: "Terminado")
            manager.shutdown()
            notifications = manager.get_notifications()
            self.assertEqual(len(notifications), 1)
            self.assertEqual(notifications[0].id, task_id)
            self.assertEqual(
                notifications[0].status,
                TaskStatus.COMPLETED,
            )
        finally:
            manager.shutdown()
    def test_rejects_invalid_worker_count(self):
        for value in (0, -1, True, 1.5):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    BackgroundTaskManager(max_workers=value)
    def test_rejects_non_callable_task(self):
        manager = BackgroundTaskManager()
        try:
            with self.assertRaises(TypeError):
                manager.submit_task("no soy una función")
        finally:
            manager.shutdown()
    def test_rejects_tasks_after_shutdown(self):
        manager = BackgroundTaskManager()
        manager.shutdown()
        with self.assertRaises(RuntimeError):
            manager.submit_task(lambda: None)
    def test_creates_independent_groups(self):
        manager = BackgroundTaskManager()
        try:
            first_id = manager.create_group("Trabajo", max_workers=2)
            second_id = manager.create_group("Personal", max_workers=1)
            self.assertNotEqual(first_id, second_id)
            self.assertEqual(manager.get_group(first_id).name, "Trabajo")
            self.assertEqual(manager.get_group(second_id).name, "Personal")
            self.assertEqual(manager.get_group(first_id).max_workers, 2)
            self.assertEqual(manager.get_group(second_id).max_workers, 1)
        finally:
            manager.shutdown()
    def test_assigns_task_to_selected_group(self):
        manager = BackgroundTaskManager()
        try:
            group_id = manager.create_group("Trabajo")
            task_id = manager.submit_task(
                lambda: 25,
                name="Cálculo",
                group_id=group_id,
            )
            manager.shutdown()
            task = manager.get_task(task_id)
            self.assertEqual(task.group_id, group_id)
            self.assertEqual(task.result, 25)
            self.assertEqual(task.status, TaskStatus.COMPLETED)
        finally:
            manager.shutdown()
    def test_groups_execute_independently(self):
        manager = BackgroundTaskManager()
        group_a = manager.create_group("Grupo A", max_workers=1)
        group_b = manager.create_group("Grupo B", max_workers=1)
        first_started = Event()
        release_first = Event()
        second_started = Event()
        def blocking_task():
            first_started.set()
            release_first.wait()
        def second_task():
            second_started.set()
        try:
            manager.submit_task(blocking_task, group_id=group_a)
            self.assertTrue(first_started.wait(timeout=2))
            manager.submit_task(second_task, group_id=group_b)
            self.assertTrue(second_started.wait(timeout=2))
        finally:
            release_first.set()
            manager.shutdown()
    def test_configures_idle_group_worker_count(self):
        manager = BackgroundTaskManager()
        try:
            group_id = manager.create_group("Trabajo", max_workers=1)
            result = manager.configure_group(group_id, max_workers=3)
            self.assertTrue(result)
            self.assertEqual(manager.get_group(group_id).max_workers, 3)
        finally:
            manager.shutdown()
    def test_does_not_configure_group_with_active_tasks(self):
        manager = BackgroundTaskManager()
        group_id = manager.create_group("Trabajo", max_workers=1)
        started = Event()
        release = Event()
        def blocking_task():
            started.set()
            release.wait()
        try:
            manager.submit_task(blocking_task, group_id=group_id)
            self.assertTrue(started.wait(timeout=2))
            result = manager.configure_group(group_id, max_workers=3)
            self.assertFalse(result)
            self.assertEqual(manager.get_group(group_id).max_workers, 1)
        finally:
            release.set()
            manager.shutdown()
    def test_deletes_empty_group(self):
        manager = BackgroundTaskManager()
        try:
            group_id = manager.create_group("Temporal")
            self.assertTrue(manager.delete_group(group_id))
            with self.assertRaises(KeyError):
                manager.get_group(group_id)
        finally:
            manager.shutdown()
    def test_does_not_delete_group_with_active_tasks(self):
        manager = BackgroundTaskManager()
        group_id = manager.create_group("Ocupado")
        started = Event()
        release = Event()
        def blocking_task():
            started.set()
            release.wait()
        try:
            manager.submit_task(blocking_task, group_id=group_id)
            self.assertTrue(started.wait(timeout=2))
            self.assertFalse(manager.delete_group(group_id))
            self.assertEqual(manager.get_group(group_id).name, "Ocupado")
        finally:
            release.set()
            manager.shutdown()
    def test_rejects_deleting_default_group(self):
        manager = BackgroundTaskManager()
        try:
            with self.assertRaises(ValueError):
                manager.delete_group("default")
        finally:
            manager.shutdown()
    def test_rejects_unknown_group_when_submitting(self):
        manager = BackgroundTaskManager()
        try:
            with self.assertRaises(KeyError):
                manager.submit_task(
                    lambda: None,
                    group_id="grupo-inexistente",
                )
        finally:
            manager.shutdown()
if __name__ == "__main__":
    unittest.main()