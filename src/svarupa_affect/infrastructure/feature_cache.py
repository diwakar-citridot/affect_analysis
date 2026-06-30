"""In-process per-request feature cache (IFeatureCache adapter).

The default transport for the cross-layer shared-feature cache (§7.3). A Redis-backed
implementation can replace this behind the same port without changing call sites.
"""

from __future__ import annotations


class InMemoryFeatureCache:
    """Adapter implementing :class:`IFeatureCache` with a plain dict."""

    def __init__(self) -> None:
        self._store: dict[str, object] = {}

    def get(self, key: str) -> object | None:
        return self._store.get(key)

    def set(self, key: str, value: object) -> None:
        self._store[key] = value
