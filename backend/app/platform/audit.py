"""Audit and usage ledger for local workflow demos."""

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime


@dataclass
class AuditEvent:
    """One immutable workflow event."""

    event_id: int
    module: str
    action: str
    tenant_id: str
    operator: str
    status: str
    detail: dict
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class AuditLedger:
    """In-memory audit, usage, and billing counter ledger."""

    def __init__(self) -> None:
        self._events: list[AuditEvent] = []
        self._usage: dict[str, dict[str, int]] = {}

    def record(
        self,
        module: str,
        action: str,
        tenant_id: str,
        operator: str,
        status: str = "completed",
        **detail: object,
    ) -> dict:
        """Record an audit event and update usage counters."""

        event = AuditEvent(
            event_id=len(self._events) + 1,
            module=module,
            action=action,
            tenant_id=tenant_id,
            operator=operator,
            status=status,
            detail=dict(detail),
        )
        self._events.append(event)
        tenant_usage = self._usage.setdefault(tenant_id, {})
        tenant_usage[module] = tenant_usage.get(module, 0) + 1
        return asdict(event)

    def list_events(self, module: str | None = None, limit: int = 20) -> list[dict]:
        """List recent audit events."""

        events = self._events
        if module:
            events = [event for event in events if event.module == module]
        return [asdict(event) for event in events[-limit:]]

    def usage_summary(self, tenant_id: str = "demo-tenant") -> dict:
        """Return a lightweight usage and billing summary."""

        usage = self._usage.get(tenant_id, {})
        total_calls = sum(usage.values())
        return {
            "tenant_id": tenant_id,
            "usage": usage,
            "total_calls": total_calls,
            "billing_mode": "demo_counter_only",
            "estimated_amount": "0.00",
        }


audit_ledger = AuditLedger()
