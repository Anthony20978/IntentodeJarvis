import sqlite3
from contextlib import closing
from .config import DATA_DIR, DATABASE_PATH
from pathlib import Path
import shutil
# Ubicación anterior de la base de datos
LEGACY_DATABASE_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "jarvis.db"
)
def initialize_memory():
    """Inicializa la base de datos y migra datos antiguos si existen."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    # Migrar la base de datos anterior si todavía no existe la nueva.
    if not DATABASE_PATH.exists() and LEGACY_DATABASE_PATH.is_file():
        shutil.copy2(LEGACY_DATABASE_PATH, DATABASE_PATH)
    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        with connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL
                )
            """)
def save_memory(key: str, value: str):
    """Guarda un dato o actualiza uno existente."""
    if not key.strip() or not value.strip():
        raise ValueError("La clave y el valor no pueden estar vacíos.")
    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        with connection:
            connection.execute("""
                INSERT INTO memory (key, value)
                VALUES (?, ?)
                ON CONFLICT(key)
                DO UPDATE SET value = excluded.value
            """, (key.strip(), value.strip()))
def get_memory(key: str):
    """Recupera un dato mediante su clave."""
    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        result = connection.execute(
            "SELECT value FROM memory WHERE key = ?",
            (key.strip(),)
        ).fetchone()
    return result[0] if result else None
def delete_memory(key: str):
    """Elimina un dato mediante su clave."""
    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        with connection:
            connection.execute(
                "DELETE FROM memory WHERE key = ?",
                (key.strip(),)
            )