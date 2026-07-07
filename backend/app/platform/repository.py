"""In-memory repository helpers that mimic database behavior."""

from collections.abc import Callable
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime


@dataclass
class WorkflowTask:
    """Persisted workflow task record."""

    task_id: str
    module: str
    status: str
    title: str
    tenant_id: str
    operator: str
    current_step: str = "created"
    progress: int = 0
    payload: dict = field(default_factory=dict)
    errors: list[dict] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class InMemoryRepository:
    """Simple repository with transaction-style rollback for demos."""

    def __init__(self) -> None:
        self._tasks: dict[str, WorkflowTask] = {}
        self._review_records: list[dict] = []

    @contextmanager
    def transaction(self) -> object:
        """Rollback records if a demo operation raises."""

        snapshot = deepcopy((self._tasks, self._review_records))
        try:
            yield self
        except Exception:
            self._tasks, self._review_records = snapshot
            raise

    def save_task(self, task: WorkflowTask) -> dict:
        """Insert or replace a workflow task."""

        task.updated_at = datetime.now(UTC).isoformat()
        self._tasks[task.task_id] = task
        return asdict(task)

    def update_task(self, task_id: str, **changes: object) -> dict | None:
        """Update task fields."""

        task = self._tasks.get(task_id)
        if not task:
            return None
        for key, value in changes.items():
            setattr(task, key, value)
        task.updated_at = datetime.now(UTC).isoformat()
        return asdict(task)

    def get_task(self, task_id: str) -> dict | None:
        """Get one task."""

        task = self._tasks.get(task_id)
        return asdict(task) if task else None

    def list_tasks(
        self,
        module: str | None = None,
        status: str | None = None,
        page: int = 1,
        size: int = 10,
        predicate: Callable[[WorkflowTask], bool] | None = None,
    ) -> dict:
        """List tasks with simple filtering and pagination."""

        items = list(self._tasks.values())
        if module:
            items = [item for item in items if item.module == module]
        if status:
            items = [item for item in items if item.status == status]
        if predicate:
            items = [item for item in items if predicate(item)]
        total = len(items)
        start = max(page - 1, 0) * size
        return {
            "items": [asdict(item) for item in items[start : start + size]],
            "page": page,
            "size": size,
            "total": total,
        }

    def add_review_record(self, module: str, subject_id: str, operator: str, result: str, issues: list[dict]) -> dict:
        """Store one review record."""

        record = {
            "id": len(self._review_records) + 1,
            "module": module,
            "subject_id": subject_id,
            "operator": operator,
            "result": result,
            "issues": issues,
            "created_at": datetime.now(UTC).isoformat(),
        }
        self._review_records.append(record)
        return record

    def list_review_records(self, module: str | None = None, subject_id: str | None = None) -> list[dict]:
        """List review records."""

        records = self._review_records
        if module:
            records = [record for record in records if record["module"] == module]
        if subject_id:
            records = [record for record in records if record["subject_id"] == subject_id]
        return records


repository = InMemoryRepository()
