"""Request context helpers for the public demo."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TenantContext:
    """Minimal tenant and operator context used by workflow records."""

    tenant_id: str = "demo-tenant"
    operator: str = "demo"
    roles: tuple[str, ...] = ("agent_operator",)


def demo_context() -> TenantContext:
    """Return the default local demo context."""

    return TenantContext()
