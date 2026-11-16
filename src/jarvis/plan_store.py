import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from .config import DATABASE_PATH
from .ai.structures import Action, ActionPlan
class PlanStore:
    """Gestiona los planes de ejecución persistentes de JARVIS."""
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
        """Crea la tabla de planes si todavía no existe."""
        with self._ensure_open():
            self._connection.execute("""
                CREATE TABLE IF NOT EXISTS plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    actions TEXT NOT NULL,
                    parameters TEXT NOT NULL,
                    requires_confirmation INTEGER NOT NULL,
                    reason TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
    def _ensure_open(self) -> sqlite3.Connection:
        """Comprueba que la conexión siga abierta."""
        if self._connection is None:
            raise RuntimeError("La conexión de planes está cerrada.")
        return self._connection
    @staticmethod
    def _validate_name(name: str) -> str:
        """Valida y normaliza el nombre de un plan."""
        if not isinstance(name, str):
            raise TypeError("El nombre del plan debe ser texto.")
        if not name.strip():
            raise ValueError("El nombre del plan no puede estar vacío.")
        return name.strip()
    @staticmethod
    def _serialize_plan(plan: ActionPlan) -> tuple[str, str, int, str]:
        """Convierte un ActionPlan en datos compatibles con SQLite."""
        if not isinstance(plan, ActionPlan):
            raise TypeError("plan debe ser una instancia de ActionPlan.")
        if not isinstance(plan.actions, list):
            raise TypeError("actions debe ser una lista.")
        if not all(isinstance(action, Action) for action in plan.actions):
            raise TypeError("Todas las acciones deben ser instancias de Action.")
        if not isinstance(plan.parameters, dict):
            raise TypeError("parameters debe ser un diccionario.")
        if not isinstance(plan.requires_confirmation, bool):
            raise TypeError("requires_confirmation debe ser booleano.")
        if not isinstance(plan.reason, str):
            raise TypeError("reason debe ser texto.")
        actions_data = [
            {
                "name": action.name,
                "parameters": action.parameters,
            }
            for action in plan.actions
        ]
        try:
            actions_json = json.dumps(
                actions_data,
                ensure_ascii=False,
            )
            parameters_json = json.dumps(
                plan.parameters,
                ensure_ascii=False,
            )
        except (TypeError, ValueError) as error:
            raise ValueError(
                "Los datos del plan deben ser compatibles con JSON."
            ) from error
        return (
            actions_json,
            parameters_json,
            int(plan.requires_confirmation),
            plan.reason,
        )
    @staticmethod
    def _deserialize_plan(row: sqlite3.Row) -> ActionPlan:
        """Reconstruye un ActionPlan desde un registro SQLite."""
        actions_data = json.loads(row["actions"])
        actions = [
            Action(
                name=item["name"],
                parameters=item["parameters"],
            )
            for item in actions_data
        ]
        return ActionPlan(
            actions=actions,
            parameters=json.loads(row["parameters"]),
            requires_confirmation=bool(row["requires_confirmation"]),
            reason=row["reason"],
        )
    def save_plan(self, name: str, plan: ActionPlan) -> int:
        """Guarda un plan y devuelve su identificador."""
        name = self._validate_name(name)
        actions, parameters, confirmation, reason = (
            self._serialize_plan(plan)
        )
        now = datetime.now(timezone.utc).isoformat()
        try:
            with self._ensure_open():
                cursor = self._connection.execute("""
                    INSERT INTO plans (
                        name,
                        actions,
                        parameters,
                        requires_confirmation,
                        reason,
                        created_at,
                        updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    name,
                    actions,
                    parameters,
                    confirmation,
                    reason,
                    now,
                    now,
                ))
        except sqlite3.IntegrityError as error:
            raise ValueError(
                f"Ya existe un plan llamado '{name}'."
            ) from error
        return cursor.lastrowid
    def get_plan(self, name: str) -> ActionPlan | None:
        """Recupera un plan mediante su nombre."""
        name = self._validate_name(name)
        row = self._ensure_open().execute(
            "SELECT * FROM plans WHERE name = ?",
            (name,),
        ).fetchone()
        if row is None:
            return None
        return self._deserialize_plan(row)
    def list_plans(self) -> list[dict]:
        """Devuelve los datos descriptivos de los planes guardados."""
        rows = self._ensure_open().execute("""
            SELECT id, name, reason, created_at, updated_at
            FROM plans
            ORDER BY name COLLATE NOCASE
        """).fetchall()
        return [dict(row) for row in rows]
    def update_plan(self, name: str, plan: ActionPlan) -> bool:
        """Actualiza las acciones y parámetros de un plan existente."""
        name = self._validate_name(name)
        actions, parameters, confirmation, reason = (
            self._serialize_plan(plan)
        )
        now = datetime.now(timezone.utc).isoformat()
        with self._ensure_open():
            cursor = self._connection.execute("""
                UPDATE plans
                SET actions = ?,
                    parameters = ?,
                    requires_confirmation = ?,
                    reason = ?,
                    updated_at = ?
                WHERE name = ?
            """, (
                actions,
                parameters,
                confirmation,
                reason,
                now,
                name,
            ))
        return cursor.rowcount > 0
    def delete_plan(self, name: str) -> bool:
        """Elimina un plan mediante su nombre."""
        name = self._validate_name(name)
        with self._ensure_open():
            cursor = self._connection.execute(
                "DELETE FROM plans WHERE name = ?",
                (name,),
            )
        return cursor.rowcount > 0
    def close(self) -> None:
        """Cierra la conexión con la base de datos."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()