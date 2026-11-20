from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass, replace
from enum import Enum
from threading import Lock
from typing import Any, Callable
from uuid import uuid4
class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
@dataclass
class TaskInfo:
    id: str
    name: str
    group_id: str
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: str | None = None
@dataclass(frozen=True)
class TaskNotification:
    id: str
    name: str
    group_id: str
    status: TaskStatus
    result: Any = None
    error: str | None = None
@dataclass(frozen=True)
class GroupInfo:
    id: str
    name: str
    max_workers: int
    task_count: int
    pending_count: int
    running_count: int
@dataclass
class _TaskRecord:
    info: TaskInfo
    future: Future | None = None
@dataclass
class _Group:
    id: str
    name: str
    max_workers: int
    executor: ThreadPoolExecutor
class BackgroundTaskManager:
    def __init__(self, max_workers: int = 2):
        self._validate_worker_count(max_workers)
        self._lock = Lock()
        self._shutdown = False
        self._groups: dict[str, _Group] = {}
        self._tasks: dict[str, _TaskRecord] = {}
        self._notifications: list[TaskNotification] = []
        self._groups["default"] = _Group(
            id="default",
            name="General",
            max_workers=max_workers,
            executor=ThreadPoolExecutor(
                max_workers=max_workers,
                thread_name_prefix="jarvis-default",
            ),
        )
    @staticmethod
    def _validate_worker_count(max_workers: int) -> None:
        if (
            isinstance(max_workers, bool)
            or not isinstance(max_workers, int)
            or max_workers < 1
        ):
            raise ValueError("max_workers debe ser un entero positivo")
    def _ensure_running(self) -> None:
        if self._shutdown:
            raise RuntimeError("El administrador ya está cerrado")
    def create_group(self, name: str, max_workers: int = 1) -> str:
        self._validate_worker_count(max_workers)
        if not isinstance(name, str) or not name.strip():
            raise ValueError("El nombre del grupo no puede estar vacío")
        with self._lock:
            self._ensure_running()
            group_id = uuid4().hex
            self._groups[group_id] = _Group(
                id=group_id,
                name=name.strip(),
                max_workers=max_workers,
                executor=ThreadPoolExecutor(
                    max_workers=max_workers,
                    thread_name_prefix=f"jarvis-{group_id[:8]}",
                ),
            )
            return group_id
    def configure_group(self, group_id: str, max_workers: int) -> bool:
        self._validate_worker_count(max_workers)
        with self._lock:
            self._ensure_running()
            group = self._groups.get(group_id)
            if group is None:
                raise KeyError(f"Grupo desconocido: {group_id}")
            if self._group_has_active_tasks(group_id):
                return False
            if group.max_workers == max_workers:
                return True
            old_executor = group.executor
            group.executor = ThreadPoolExecutor(
                max_workers=max_workers,
                thread_name_prefix=f"jarvis-{group_id[:8]}",
            )
            group.max_workers = max_workers
        old_executor.shutdown(wait=True)
        return True
    def delete_group(self, group_id: str) -> bool:
        if group_id == "default":
            raise ValueError("El grupo predeterminado no se puede eliminar")
        with self._lock:
            self._ensure_running()
            group = self._groups.get(group_id)
            if group is None:
                return False
            if self._group_has_active_tasks(group_id):
                return False
            del self._groups[group_id]
        group.executor.shutdown(wait=True)
        return True
    def get_group(self, group_id: str) -> GroupInfo:
        with self._lock:
            group = self._groups.get(group_id)
            if group is None:
                raise KeyError(f"Grupo desconocido: {group_id}")
            tasks = [
                record.info
                for record in self._tasks.values()
                if record.info.group_id == group_id
            ]
            return GroupInfo(
                id=group.id,
                name=group.name,
                max_workers=group.max_workers,
                task_count=len(tasks),
                pending_count=sum(
                    task.status == TaskStatus.PENDING for task in tasks
                ),
                running_count=sum(
                    task.status == TaskStatus.RUNNING for task in tasks
                ),
            )
    def get_groups(self) -> list[GroupInfo]:
        with self._lock:
            group_ids = list(self._groups)
        return [self.get_group(group_id) for group_id in group_ids]
    def submit_task(
        self,
        task: Callable,
        name: str | None = None,
        group_id: str = "default",
        *args: Any,
        **kwargs: Any,
    ) -> str:
        if not callable(task):
            raise TypeError("La tarea debe ser ejecutable")
        task_name = name or getattr(task, "__name__", "Tarea")
        with self._lock:
            self._ensure_running()
            group = self._groups.get(group_id)
            if group is None:
                raise KeyError(f"Grupo desconocido: {group_id}")
            task_id = uuid4().hex
            info = TaskInfo(
                id=task_id,
                name=task_name,
                group_id=group_id,
            )
            record = _TaskRecord(info=info)
            self._tasks[task_id] = record
            try:
                record.future = group.executor.submit(
                    self._run_task,
                    task_id,
                    task,
                    args,
                    kwargs,
                )
            except Exception:
                del self._tasks[task_id]
                raise
            return task_id
    def _run_task(
        self,
        task_id: str,
        task: Callable,
        args: tuple,
        kwargs: dict,
    ) -> None:
        with self._lock:
            record = self._tasks[task_id]
            if record.info.status == TaskStatus.CANCELLED:
                return
            record.info.status = TaskStatus.RUNNING
        try:
            result = task(*args, **kwargs)
            status = TaskStatus.COMPLETED
            error = None
        except Exception as exc:
            result = None
            status = TaskStatus.FAILED
            error = str(exc)
        with self._lock:
            info = self._tasks[task_id].info
            info.status = status
            info.result = result
            info.error = error
            self._notifications.append(
                TaskNotification(
                    id=info.id,
                    name=info.name,
                    group_id=info.group_id,
                    status=info.status,
                    result=info.result,
                    error=info.error,
                )
            )
    def get_task(self, task_id: str) -> TaskInfo:
        with self._lock:
            record = self._tasks.get(task_id)
            if record is None:
                raise KeyError(f"Tarea desconocida: {task_id}")
            return replace(record.info)
    def get_group_tasks(self, group_id: str) -> list[TaskInfo]:
        with self._lock:
            if group_id not in self._groups:
                raise KeyError(f"Grupo desconocido: {group_id}")
            return [
                replace(record.info)
                for record in self._tasks.values()
                if record.info.group_id == group_id
            ]
    def get_pending_tasks(self) -> list[TaskInfo]:
        with self._lock:
            return [
                replace(record.info)
                for record in self._tasks.values()
                if record.info.status in (
                    TaskStatus.PENDING,
                    TaskStatus.RUNNING,
                )
            ]
    def cancel_task(self, task_id: str) -> bool:
        with self._lock:
            record = self._tasks.get(task_id)
            if record is None or record.future is None:
                return False
            if not record.future.cancel():
                return False
            info = record.info
            info.status = TaskStatus.CANCELLED
            self._notifications.append(
                TaskNotification(
                    id=info.id,
                    name=info.name,
                    group_id=info.group_id,
                    status=info.status,
                )
            )
            return True
    def get_notifications(self) -> list[TaskNotification]:
        with self._lock:
            notifications = self._notifications
            self._notifications = []
            return notifications
    def _group_has_active_tasks(self, group_id: str) -> bool:
        return any(
            record.info.group_id == group_id
            and record.info.status in (
                TaskStatus.PENDING,
                TaskStatus.RUNNING,
            )
            for record in self._tasks.values()
        )
    def shutdown(self) -> None:
        with self._lock:
            if self._shutdown:
                return
            self._shutdown = True
            executors = [
                group.executor for group in self._groups.values()
            ]
        for executor in executors:
            executor.shutdown(wait=True)