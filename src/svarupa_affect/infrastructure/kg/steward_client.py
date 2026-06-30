"""IKnowledgeSteward adapter (§4.5).

AFF is **read-only** against the KG. Glosses are fetched per ``(dimension_id, attr)`` and
cached. The default steward reads from :class:`StaticConceptRegistry` / MySQL-backed
``MySQLConceptRegistry`` so the closed vocabulary matches ``svarupa_concept_layer``.
"""

from __future__ import annotations

from .concept_registry import StaticConceptRegistry, build_concept_registry


class StaticKnowledgeSteward:
    """Adapter implementing :class:`IKnowledgeSteward` from a concept registry (cached)."""

    def __init__(self, registry: StaticConceptRegistry | None = None) -> None:
        self._registry = registry or build_concept_registry()
        self._cache: dict[tuple[int, str], str] = {}

    async def glosses(self, dimension_id: int, attributes: list[str]) -> dict[str, str]:
        return self._registry.glosses(dimension_id, attributes)


class Neo4jKnowledgeSteward:  # pragma: no cover - requires a live Neo4j + driver
    """Read-only Neo4j-backed steward (optional ``neo4j`` driver)."""

    def __init__(self, uri: str, user: str, password: str) -> None:
        from neo4j import GraphDatabase  # type: ignore

        self._driver = GraphDatabase.driver(uri, auth=(user, password))
        self._cache: dict[tuple[int, str], str] = {}

    async def glosses(self, dimension_id: int, attributes: list[str]) -> dict[str, str]:
        out: dict[str, str] = {}
        with self._driver.session() as session:
            for attr in attributes:
                key = (dimension_id, attr)
                if key not in self._cache:
                    rec = session.run(
                        "MATCH (c:Concept {dimension_id:$d, slug:$a}) RETURN c.gloss AS gloss",
                        d=dimension_id,
                        a=attr,
                    ).single()
                    self._cache[key] = (rec["gloss"] if rec else "") or ""
                if self._cache[key]:
                    out[attr] = self._cache[key]
        return out


def build_knowledge_steward(
    registry: StaticConceptRegistry | None = None,
) -> StaticKnowledgeSteward:
    return StaticKnowledgeSteward(registry=registry or build_concept_registry())
