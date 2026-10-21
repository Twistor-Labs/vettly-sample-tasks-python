import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone


class ValidationError(ValueError):
    pass


@dataclass
class Task:
    title: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    done: bool = False
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class TaskStore:
    """In-memory store; a database can replace it behind the same methods."""

    def __init__(self):
        self._tasks: dict[str, Task] = {}

    def list(self, done: bool | None = None) -> list[dict]:
        return [asdict(t) for t in self._tasks.values() if done is None or t.done == done]

    def create(self, payload: object) -> dict:
        title = payload.get("title") if isinstance(payload, dict) else None
        if not isinstance(title, str) or not title.strip():
            raise ValidationError("title is required")
        if len(title) > 200:
            raise ValidationError("title must be 200 characters or fewer")
        task = Task(title=title.strip())
        self._tasks[task.id] = task
        return asdict(task)

    def complete(self, task_id: str) -> dict | None:
        task = self._tasks.get(task_id)
        if task is None:
            return None
        task.done = True
        return asdict(task)

    def remove(self, task_id: str) -> bool:
        return self._tasks.pop(task_id, None) is not None
