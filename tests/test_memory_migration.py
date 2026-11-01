import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch
from src.jarvis import memory
class MemoryMigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.data_dir = self.root / "new_data"
        self.database_path = self.data_dir / "jarvis.db"
        self.legacy_path = self.root / "old_data" / "jarvis.db"
        self.legacy_path.parent.mkdir(parents=True)
        with closing(sqlite3.connect(self.legacy_path)) as connection:
            with connection:
                connection.execute("""
                    CREATE TABLE memory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        key TEXT UNIQUE NOT NULL,
                        value TEXT NOT NULL
                    )
                """)
                connection.execute(
                    "INSERT INTO memory (key, value) VALUES (?, ?)",
                    ("nombre", "JARVIS")
                )
        self.data_patch = patch.object(
            memory, "DATA_DIR", self.data_dir
        )
        self.database_patch = patch.object(
            memory, "DATABASE_PATH", self.database_path
        )
        self.legacy_patch = patch.object(
            memory, "LEGACY_DATABASE_PATH", self.legacy_path
        )
        self.data_patch.start()
        self.database_patch.start()
        self.legacy_patch.start()
    def tearDown(self):
        self.legacy_patch.stop()
        self.database_patch.stop()
        self.data_patch.stop()
        self.temp_dir.cleanup()
    def test_migration_preserves_memory(self):
        memory.initialize_memory()
        self.assertEqual(
            memory.get_memory("nombre"),
            "JARVIS"
        )
    def test_legacy_database_is_preserved(self):
        memory.initialize_memory()
        self.assertTrue(self.legacy_path.exists())
    def test_existing_database_is_not_overwritten(self):
        memory.DATA_DIR.mkdir(parents=True)
        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                connection.execute("""
                    CREATE TABLE memory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        key TEXT UNIQUE NOT NULL,
                        value TEXT NOT NULL
                    )
                """)
                connection.execute(
                    "INSERT INTO memory (key, value) VALUES (?, ?)",
                    ("nombre", "JARVIS NUEVO")
                )
        memory.initialize_memory()
        self.assertEqual(
            memory.get_memory("nombre"),
            "JARVIS NUEVO"
        )
if __name__ == "__main__":
    unittest.main()