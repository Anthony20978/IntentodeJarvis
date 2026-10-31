import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from src.jarvis import memory
from src.jarvis.brain import process_command
from src.jarvis.platform import get_system_info
from src.jarvis.capabilities import get_capabilities
class JarvisCoreTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        temp_path = Path(self.temp_dir.name)
        self.data_patch = patch.object(
            memory, "DATA_DIR", temp_path
        )
        self.database_patch = patch.object(
            memory, "DATABASE_PATH", temp_path / "test.db"
        )
        self.data_patch.start()
        self.database_patch.start()
        memory.initialize_memory()
    def tearDown(self):
        self.data_patch.stop()
        self.database_patch.stop()
        self.temp_dir.cleanup()
    def test_save_and_get_memory(self):
        memory.save_memory("nombre", "JARVIS")
        self.assertEqual(
            memory.get_memory("nombre"),
            "JARVIS"
        )
    def test_update_memory(self):
        memory.save_memory("nombre", "JARVIS")
        memory.save_memory("nombre", "JARVIS 2")
        self.assertEqual(
            memory.get_memory("nombre"),
            "JARVIS 2"
        )
    def test_missing_memory(self):
        self.assertIsNone(
            memory.get_memory("inexistente")
        )
    def test_delete_memory(self):
        memory.save_memory("nombre", "JARVIS")
        memory.delete_memory("nombre")
        self.assertIsNone(
            memory.get_memory("nombre")
        )
    def test_empty_memory_values(self):
        with self.assertRaises(ValueError):
            memory.save_memory("nombre", " ")
    def test_remember_command(self):
        response = process_command(
            "recuerda nombre: JARVIS"
        )
        self.assertEqual(response, "He guardado: nombre.")
        self.assertEqual(
            memory.get_memory("nombre"),
            "JARVIS"
        )
    def test_retrieve_command(self):
        memory.save_memory("nombre", "JARVIS")
        self.assertEqual(
            process_command("recupera nombre"),
            "JARVIS"
        )
    def test_empty_command(self):
        self.assertEqual(
            process_command(""),
            "No he recibido ninguna instrucción."
        )
    def test_help_command(self):
        self.assertIn(
            "Comandos disponibles",
            process_command("ayuda")
        )
    def test_system_detection(self):
        info = get_system_info()
        self.assertIn("system", info)
        self.assertIn("architecture", info)
        self.assertGreaterEqual(info["cpu_cores"], 1)
    def test_capabilities(self):
        capabilities = get_capabilities()
        self.assertTrue(capabilities["system_detection"])
        self.assertTrue(capabilities["persistent_memory"])
        self.assertTrue(capabilities["command_processing"])
if __name__ == "__main__":
    unittest.main()