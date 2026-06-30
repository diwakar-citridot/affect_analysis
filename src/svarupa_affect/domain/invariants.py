"""Shared domain-invariant bases (§3.3.0).

Every value object is immutable. Every *core* object additionally carries a
``schema_version`` and a UTC ``created_at`` timestamp. These bases enforce the
"immutable + versioned + timestamped" invariants in one place.
"""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = "2.1.0"


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Frozen(BaseModel):
    """Immutable value object base (no I/O, no mutation)."""

    model_config = ConfigDict(frozen=True)


class Core(Frozen):
    """Core domain object base: immutable + versioned + timestamped.

    Uncertainty- and evidence-bearing invariants are added by the concrete models
    (each carries either a ``confidence`` / ``UncertaintyProfile`` and an ``evidence`` list).
    """

    schema_version: str = SCHEMA_VERSION
    created_at: datetime = Field(default_factory=_utcnow)
