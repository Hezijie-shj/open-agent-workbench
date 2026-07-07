"""Local object storage abstraction for public demos."""

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from hashlib import sha256


@dataclass
class StoredObject:
    """Stored object metadata."""

    object_key: str
    file_name: str
    content_type: str
    size: int
    checksum: str
    tags: dict[str, str] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class LocalObjectStore:
    """Small in-memory object store with metadata records."""

    def __init__(self) -> None:
        self._objects: dict[str, StoredObject] = {}
        self._payloads: dict[str, bytes] = {}

    def put(self, file_name: str, payload: bytes, content_type: str, **tags: str) -> dict:
        """Store bytes and return public-safe metadata."""

        checksum = sha256(payload).hexdigest()[:16]
        object_key = f"demo/{checksum}/{file_name}"
        stored = StoredObject(
            object_key=object_key,
            file_name=file_name,
            content_type=content_type,
            size=len(payload),
            checksum=checksum,
            tags=tags,
        )
        self._objects[object_key] = stored
        self._payloads[object_key] = payload
        return asdict(stored)

    def get(self, object_key: str) -> dict | None:
        """Return stored metadata."""

        stored = self._objects.get(object_key)
        return asdict(stored) if stored else None

    def list_objects(self, prefix: str = "demo/") -> list[dict]:
        """List objects by prefix."""

        return [asdict(item) for key, item in self._objects.items() if key.startswith(prefix)]


object_store = LocalObjectStore()
