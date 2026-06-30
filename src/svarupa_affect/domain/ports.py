"""Ports (Protocols) — the seam between the pure core and outer adapters (§3.2, §4.1).

Inner layers depend on these abstractions only; ``infrastructure/`` implements them.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .models import (
    AffectiveField,
    AttributeScore,
    CueBundle,
    EmotionEvidence,
    EmotionHypothesis,
    LayerContext,
    VAD,
    DimensionalSignal,
)


@runtime_checkable
class IAnalyticalLayer(Protocol):
    code: str
    version: str
    affinity: frozenset[int]

    async def analyze(self, ctx: LayerContext) -> list[DimensionalSignal]: ...


@runtime_checkable
class IVADModel(Protocol):
    async def score(self, text: str) -> tuple[VAD, float]: ...


@runtime_checkable
class ILexicalAffect(Protocol):
    async def signals(self, text: str) -> tuple[EmotionEvidence, float]: ...


@runtime_checkable
class ILinguisticCues(Protocol):
    async def cues(self, text: str, history: list[dict[str, str]]) -> CueBundle: ...


@runtime_checkable
class IEmotionEvidence(Protocol):
    async def classify(self, text: str) -> tuple[EmotionEvidence, float]: ...


@runtime_checkable
class IBridgeTable(Protocol):
    version: str

    def map(
        self, hypotheses: list[EmotionHypothesis], field: AffectiveField
    ) -> list[AttributeScore]: ...


@runtime_checkable
class IConceptRegistry(Protocol):
    def affinity(self, layer_code: str | None = None) -> frozenset[int]: ...

    def slugs(self, dimension_id: int, layer_code: str | None = None) -> frozenset[str]: ...

    def glosses(
        self,
        dimension_id: int,
        attributes: list[str],
        layer_code: str | None = None,
    ) -> dict[str, str]: ...


@runtime_checkable
class IScorerRegistry(Protocol):
    def scorers(self, layer_code: str | None = None) -> tuple[object, ...]: ...

    def emit_dimensions(self, layer_code: str | None = None) -> frozenset[int]: ...

    def scorer_for(self, dimension_id: int, layer_code: str | None = None) -> object | None: ...

    def output_slugs(self, dimension_id: int, layer_code: str | None = None) -> frozenset[str]: ...


@runtime_checkable
class IDimensionRegistry(Protocol):
    def name_for(self, dimension_id: int) -> str: ...


@runtime_checkable
class IKnowledgeSteward(Protocol):
    async def glosses(self, dimension_id: int, attributes: list[str]) -> dict[str, str]: ...


@runtime_checkable
class ILLMProvider(Protocol):
    async def complete_json(
        self,
        *,
        system: str,
        prompt: str,
        schema: dict,
        model_id: str,
        temperature: float,
        timeout_s: float,
        max_tokens: int = 4096,
        request_id: str | None = None,
        attempt: int = 1,
    ) -> dict: ...


@runtime_checkable
class IFeatureCache(Protocol):
    """Per-request cache for cross-layer shared features (PHE valence/arousal, NAR temporal_cues).

    Only *features* are shared across layers, never judgements — AFF stays epistemically
    independent for fusion's agreement math.
    """

    def get(self, key: str) -> object | None: ...

    def set(self, key: str, value: object) -> None: ...
