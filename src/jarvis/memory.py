import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from .config import DATA_DIR,DATABASE_PATH
# Base de datos utilizada por versiones anteriores.
LEGACY_DATABASE_PATH = (
    Path(__file__).resolve().parents[2] / "data" / "jarvis.db"
)
class MemoryStore:
    """Gestiona la memoria persistente de JARVIS."""
    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path or DATABASE_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self.db_path)
        self._connection.row_factory = sqlite3.Row
        try:
            self._initialize_database()
        except Exception:
            self.close()
            raise
    def _initialize_database(self) -> None:
        """Crea la estructura y recupera datos antiguos."""
        with self._connection:
            self._connection.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL UNIQUE,
                    value TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            self._connection.execute("""
                CREATE TABLE IF NOT EXISTS memory_migrations (
                    source TEXT PRIMARY KEY,
                    migrated_at TEXT NOT NULL
                )
            """)
            self._migrate_legacy_table(self._connection)
        if self.db_path.resolve() == Path(DATABASE_PATH).resolve():
            self._migrate_legacy_database()
    def _migrate_legacy_table(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        """Importa registros de la antigua tabla 'memory'."""
        migration_key = "legacy_table:memory"
        if connection.execute(
            "SELECT 1 FROM memory_migrations WHERE source = ?",
            (migration_key,),
        ).fetchone():
            return
        table = connection.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table' AND name = 'memory'
        """).fetchone()
        if table is None:
            return
        columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(memory)"
            ).fetchall()
        }
        if not {"key", "value"}.issubset(columns):
            return
        rows = connection.execute(
            "SELECT key, value FROM memory"
        ).fetchall()
        now = datetime.now(timezone.utc).isoformat()
        connection.executemany("""
            INSERT OR IGNORE INTO memories
                (key, value, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        """, [
            (row["key"], row["value"], now, now)
            for row in rows
        ])
        connection.execute(
            """
            INSERT INTO memory_migrations (source, migrated_at)
            VALUES (?, ?)
            """,
            (migration_key, now),
        )
    def _migrate_legacy_database(self) -> None:
        """Importa recuerdos de la base de datos antigua."""
        legacy_path = Path(LEGACY_DATABASE_PATH)
        if not legacy_path.is_file():
            return
        if legacy_path.resolve() == self.db_path.resolve():
            return
        migration_key = f"legacy_database:{legacy_path.resolve()}"
        if self._connection.execute(
            "SELECT 1 FROM memory_migrations WHERE source = ?",
            (migration_key,),
        ).fetchone():
            return
        with closing(sqlite3.connect(legacy_path)) as legacy:
            legacy.row_factory = sqlite3.Row
            table = legacy.execute("""
                SELECT name
                FROM sqlite_master
                WHERE type = 'table' AND name = 'memory'
            """).fetchone()
            if table is None:
                return
            columns = {
                row["name"]
                for row in legacy.execute(
                    "PRAGMA table_info(memory)"
                ).fetchall()
            }
            if not {"key", "value"}.issubset(columns):
                return
            rows = legacy.execute(
                "SELECT key, value FROM memory"
            ).fetchall()
        now = datetime.now(timezone.utc).isoformat()
        with self._connection:
            self._connection.executemany("""
                INSERT OR IGNORE INTO memories
                    (key, value, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            """, [
                (row["key"], row["value"], now, now)
                for row in rows
            ])
            self._connection.execute(
                """
                INSERT INTO memory_migrations (source, migrated_at)
                VALUES (?, ?)
                """,
                (migration_key, now),
            )
    def _ensure_open(self) -> sqlite3.Connection:
        """Comprueba que la conexión siga abierta."""
        if self._connection is None:
            raise RuntimeError("La conexión de memoria está cerrada.")
        return self._connection
    def remember(self, key: str, value: str) -> None:
        """Guarda un recuerdo o actualiza uno existente."""
        self._validate(key, value)
        now = datetime.now(timezone.utc).isoformat()
        with self._ensure_open():
            self._connection.execute("""
                INSERT INTO memories
                    (key, value, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = excluded.updated_at
            """, (key.strip(), value.strip(), now, now))
    def recall(self, key: str) -> str | None:
        """Recupera un recuerdo mediante su clave."""
        self._validate(key)
        row = self._ensure_open().execute(
            "SELECT value FROM memories WHERE key = ?",
            (key.strip(),),
        ).fetchone()
        return row["value"] if row else None
    def forget(self, key: str) -> bool:
        """Elimina un recuerdo mediante su clave."""
        self._validate(key)
        with self._ensure_open():
            cursor = self._connection.execute(
                "DELETE FROM memories WHERE key = ?",
                (key.strip(),),
            )
        return cursor.rowcount > 0
    def search(self, query: str) -> list[dict]:
        """Busca recuerdos por coincidencia de texto."""
        self._validate(query)
        pattern = (
            "%"
            + query.strip()
            .replace("\\", "\\\\")
            .replace("%", "\\%")
            .replace("_", "\\_")
            + "%"
        )
        rows = self._ensure_open().execute("""
            SELECT id, key, value, created_at, updated_at
            FROM memories
            WHERE key LIKE ? ESCAPE '\\'
               OR value LIKE ? ESCAPE '\\'
            ORDER BY updated_at DESC
        """, (pattern, pattern)).fetchall()
        return [dict(row) for row in rows]
    def get_all(self) -> list[dict]:
        """Devuelve todos los recuerdos."""
        rows = self._ensure_open().execute("""
            SELECT id, key, value, created_at, updated_at
            FROM memories
            ORDER BY updated_at DESC
        """).fetchall()
        return [dict(row) for row in rows]
    def clear(self) -> None:
        """Elimina todos los recuerdos."""
        with self._ensure_open():
            self._connection.execute("DELETE FROM memories")
    @staticmethod
    def _validate(*values: str) -> None:
        """Valida los datos de entrada."""
        for value in values:
            if not isinstance(value, str):
                raise TypeError("Los datos deben ser cadenas de texto.")
            if not value.strip():
                raise ValueError("Los datos no pueden estar vacíos.")
    def close(self) -> None:
        """Cierra la conexión con la base de datos."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
# Compatibilidad temporal con el código anterior.
# Cada operación abre y cierra su propia conexión.
def initialize_memory() -> None:
    with MemoryStore(DATABASE_PATH):
        pass
def save_memory(key: str, value: str) -> None:
    with MemoryStore(DATABASE_PATH) as store:
        store.remember(key, value)
def get_memory(key: str) -> str | None:
    with MemoryStore(DATABASE_PATH) as store:
        return store.recall(key)
def delete_memory(key: str) -> bool:
    with MemoryStore(DATABASE_PATH) as store:
        return store.forget(key)