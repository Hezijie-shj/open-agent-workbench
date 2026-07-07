"""Local task queue simulation."""

from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime


@dataclass
class QueueJob:
    """Queued workflow job."""

    job_id: str
    module: str
    action: str
    status: str = "queued"
    attempts: int = 0
    max_attempts: int = 3
    payload: dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class DemoTaskQueue:
    """Deterministic queue used by the demos."""

    def __init__(self) -> None:
        self._queue: deque[QueueJob] = deque()
        self._jobs: dict[str, QueueJob] = {}

    def enqueue(self, module: str, action: str, **payload: object) -> dict:
        """Enqueue one job."""

        job_id = f"{module}-{len(self._jobs) + 1:04d}"
        job = QueueJob(job_id=job_id, module=module, action=action, payload=dict(payload))
        self._queue.append(job)
        self._jobs[job_id] = job
        return asdict(job)

    def run_next(self) -> dict | None:
        """Mark the next job as completed."""

        if not self._queue:
            return None
        job = self._queue.popleft()
        job.attempts += 1
        job.status = "completed"
        job.updated_at = datetime.now(UTC).isoformat()
        return asdict(job)

    def get(self, job_id: str) -> dict | None:
        """Return a queued job."""

        job = self._jobs.get(job_id)
        return asdict(job) if job else None

    def list_jobs(self, module: str | None = None) -> list[dict]:
        """List jobs."""

        jobs = self._jobs.values()
        if module:
            jobs = [job for job in jobs if job.module == module]
        return [asdict(job) for job in jobs]


task_queue = DemoTaskQueue()
