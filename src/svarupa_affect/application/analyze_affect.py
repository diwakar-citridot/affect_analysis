"""AffectLayer (use case): orchestrates the field-first pipeline (§2.3).

Implements IAnalyticalLayer. ``analyze`` returns the shared DimensionalSignal[] fusion
envelope; ``analyze_full`` additionally returns the curated PhenomenologyInput (the single
public object) for downstream consumers such as the Phenomenology layer.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from .. import LAYER_CODE, __version__
from ..domain.enums import Durability, EvidenceKind, StatePole, UncertaintyType
from ..domain.exceptions import ModelUnavailable
from ..domain.models import (
    AttributeScore,
    DimensionalSignal,
    Evidence,
    ForegroundEpisode,
    LayerContext,
    PhenomenologyInput,
    Provenance,
    StateHint,
    UncertaintyProfile,
)
from ..domain.ports import IBridgeTable, IConceptRegistry, IScorerRegistry
from ..domain.scoring import build_uncertainty_profile, clip, dimension_relevance
from ..infrastructure.affect.lexicons import sentences, tokenize
from .appraisal import AppraisalReconstructor
from .drivers import AffectDriverReconstructor
from .dynamics import AffectDynamicsAnalyzer
from .field_assist import FieldAssist
from .field_builder import AffectiveFieldBuilder, FieldSignals
from .guna_scorer import GunaFamilyModulator, GunaScoreResult, GunaScorer
from .hypotheses import EmotionHypothesisGenerator
from .patterns import ExperientialPatternRecognizer
from .phenomenology_input import PhenomenologyInputAssembler

logger = logging.getLogger("svarupa_affect.llm_assist")

_RELEVANCE_FLOOR = 0.12


@dataclass(frozen=True)
class AnalyzeResult:
    signals: list[DimensionalSignal]
    phenomenology_input: PhenomenologyInput


class AffectLayer:
    code: str = LAYER_CODE
    version: str = __version__

    def __init__(
        self,
        builder: AffectiveFieldBuilder,
        appraisal: AppraisalReconstructor,
        drivers: AffectDriverReconstructor,
        patterns: ExperientialPatternRecognizer,
        hypotheses: EmotionHypothesisGenerator,
        dynamics: AffectDynamicsAnalyzer,
        assembler: PhenomenologyInputAssembler,
        guna_scorer: GunaScorer | None,
        bridges: dict[int, IBridgeTable],
        guna_modulator: GunaFamilyModulator,
        field_assist: FieldAssist | None = None,
        *,
        concept_registry: IConceptRegistry | None = None,
        scorer_registry: IScorerRegistry | None = None,
        affinity: frozenset[int] | None = None,
        emit_dimensions: frozenset[int] | None = None,
    ) -> None:
        from ..infrastructure.kg.concept_registry import build_concept_registry
        from ..infrastructure.kg.scorer_registry import build_scorer_registry

        self._registry = concept_registry or build_concept_registry()
        self._scorer_registry = scorer_registry or build_scorer_registry()
        self.affinity = affinity if affinity is not None else self._registry.affinity()
        db_emit = self._scorer_registry.emit_dimensions()
        self._emit_dimensions = (
            emit_dimensions
            if emit_dimensions is not None
            else self.affinity & db_emit
        )
        unimplemented = self.affinity - db_emit
        if unimplemented:
            logger.info(
                "AFF DB affinity includes dimensions without registered scorers: %s",
                sorted(unimplemented),
            )
        not_emitting = db_emit - self._emit_dimensions
        if not_emitting:
            logger.info(
                "AFF scorers registered but not in emit set (affinity gate): %s",
                sorted(not_emitting),
            )
        self._builder = builder
        self._appraisal = appraisal
        self._drivers = drivers
        self._patterns = patterns
        self._hypotheses = hypotheses
        self._dynamics = dynamics
        self._assembler = assembler
        self._guna_scorer = guna_scorer
        self._bridges = bridges
        self._guna_modulator = guna_modulator
        self._field_assist = field_assist
        self._bridge_d8 = bridges.get(8)
        self._bridge_d9 = bridges.get(9)

    async def analyze(self, ctx: LayerContext) -> list[DimensionalSignal]:
        return (await self.analyze_full(ctx)).signals

    async def analyze_full(self, ctx: LayerContext) -> AnalyzeResult:
        text = ctx.analysis_text
        shared = ctx.shared_features

        # 1-4. affective features + hierarchical background field
        bg_sig = await self._builder.signals_for(text, ctx.conversation_history)
        background = self._builder.field_from_signals(bg_sig, shared)

        # 7. ambiguity gate + 7b. LLM field-assist (reconstruct the field; degrade silently)
        lexical_valence = self._lexical_valence(bg_sig)
        assist = await self._run_assist(ctx, background, bg_sig, lexical_valence)
        background = assist.field

        # 5-6. appraisal + drivers (why the affect is present), on the reconciled field
        appraisal = self._appraisal.reconstruct(background, bg_sig.cues)
        drivers = self._drivers.reconstruct(text, background, appraisal, bg_sig.cues)

        # 7-8. dynamics: build foreground episodes, then trajectory/interactions
        episodes = await self._foreground_episodes(text, ctx)

        # 9. experiential patterns (background-level)
        patterns = self._patterns.recognize(background)

        # 10. emotion hypotheses (derived) — gated on affect presence (abstain on affect-free text)
        if self._affect_salient(bg_sig, background):
            hypotheses = self._hypotheses.generate(
                background, patterns, bg_sig.lexical, semantic=bg_sig.semantic
            )
        else:
            hypotheses = []

        dynamics, trajectory, interactions = self._dynamics.analyze(
            background, episodes, hypotheses
        )

        # 11. score registered dimensions (field guṇa + hypothesis bridges), modulate Rasa
        scores_by_dimension: dict[int, list[AttributeScore]] = {}
        evidence_by_dimension: dict[int, list[Evidence]] = {}
        guna_result = GunaScoreResult(
            attributes=[], modulation_weights={}, evidence=[], raw_scores={}
        )
        if self._affect_salient(bg_sig, background):
            if self._guna_scorer is not None and 2 in self._emit_dimensions:
                guna_result = self._guna_scorer.score(background, patterns, trajectory)
                scores_by_dimension[2] = guna_result.attributes
                evidence_by_dimension[2] = guna_result.evidence
            for dimension_id in sorted(self._emit_dimensions & self._bridges.keys()):
                attrs = self._bridges[dimension_id].map(hypotheses, background)
                if guna_result.modulation_weights:
                    attrs = self._guna_modulator.apply(
                        attrs, guna_result.modulation_weights
                    )
                scores_by_dimension[dimension_id] = attrs

        # 12. uncertainty profile + signals + assemble public contract
        uncertainty = self._uncertainty(background, bg_sig, len(sentences(text)), text, assist)
        provenance = self._provenance(assist)

        signals = self._build_signals(
            ctx,
            scores_by_dimension,
            evidence_by_dimension,
            uncertainty,
            hypotheses,
            provenance,
        )

        phenomenology = self._assembler.assemble(
            request_id=ctx.request_id,
            layer_version=self.version,
            background_field=background,
            appraisal=appraisal,
            episodes=episodes,
            trajectory=trajectory,
            interactions=interactions,
            drivers=drivers,
            patterns=patterns,
            hypotheses=hypotheses,
            uncertainty=uncertainty,
            provenance=provenance,
        )
        return AnalyzeResult(signals=signals, phenomenology_input=phenomenology)

    # -- helpers ----------------------------------------------------------------------

    @staticmethod
    def _affect_salient(bg_sig: FieldSignals, field) -> bool:
        """Affect-presence gate: abstain on affect-free / purely factual text (§7.1)."""
        sem = bg_sig.semantic
        if sem.hypothesis_probs:
            top = max(sem.hypothesis_probs.values())
            if sem.margin >= 0.28 or top >= 0.48:
                return True
        if bg_sig.lexical.probs:
            return True
        intensity = field.core.intensity.value
        regulation = field.regulation.regulation.value
        if intensity >= 0.62 and regulation >= 0.32:
            return True
        if regulation >= 0.45 and intensity >= 0.25 and abs(field.core.valence.value) <= 0.22:
            return True
        if abs(field.core.valence.value) >= 0.28 and intensity >= 0.58:
            if bg_sig.lexical.probs or (sem.hypothesis_probs and sem.margin >= 0.30):
                return True
        if field.core.arousal.value >= 0.55:
            return True
        if field.motivation.avoidance.value >= 0.5 or field.motivation.approach.value >= 0.5:
            return True
        return False

    @staticmethod
    def _lexical_valence(bg_sig: FieldSignals) -> float:
        lex = bg_sig.lexical
        if not lex.probs:
            return 0.0
        pos = sum(lex.probs.get(e, 0.0) for e in ("joy", "love", "trust", "anticipation"))
        neg = sum(lex.probs.get(e, 0.0) for e in ("sadness", "fear", "anger", "disgust"))
        return pos - neg

    async def _run_assist(self, ctx, background, bg_sig, lexical_valence):
        from .field_assist import AssistResult

        if self._field_assist is None:
            return AssistResult(field=background, used=False, reasons=["no_assist"])
        return await self._field_assist.maybe_assist(
            ctx,
            background,
            vad_valence=bg_sig.vad.valence,
            lexical_valence=lexical_valence,
            margin=bg_sig.lexical.margin if bg_sig.lexical.probs else 0.4,
            irony=bg_sig.cues.scores.get("irony", 0.0),
            targets=bg_sig.cues.targets,
        )

    async def _foreground_episodes(self, text: str, ctx: LayerContext) -> list[ForegroundEpisode]:
        spans = sentences(text)
        episodes: list[ForegroundEpisode] = []
        for start, end, seg in spans:
            sig = await self._builder.signals_for(seg, ctx.conversation_history)
            efield = self._builder.field_from_signals(sig, ctx.shared_features)
            ep_patterns = self._patterns.recognize(efield)
            episodes.append(
                ForegroundEpisode(
                    field=efield, span=(start, end), text=seg, drivers=[], patterns=ep_patterns
                )
            )
        return episodes

    def _uncertainty(
        self, field, bg_sig: FieldSignals, n_segments: int, text: str, assist=None
    ) -> UncertaintyProfile:
        lex = bg_sig.lexical
        lex_valence = self._lexical_valence(bg_sig)
        agreement = (
            1.0 - min(1.0, abs(bg_sig.vad.valence - lex_valence) / 2.0) if lex.probs else 0.7
        )
        if assist is not None and assist.used:
            agreement = clip(0.5 * agreement + 0.5 * assist.agreement)
        coverage = (
            sum(field.axis_coverage.values()) / len(field.axis_coverage)
            if field.axis_coverage
            else 0.0
        )
        mixed = min(max(0.0, bg_sig.vad.valence), max(0.0, -lex_valence)) + min(
            max(0.0, -bg_sig.vad.valence), max(0.0, lex_valence)
        )
        length_factor = clip(len(tokenize(text)) / 25.0)
        return build_uncertainty_profile(
            field=field,
            evidence_strength=field.uncertainty.evidence_quality.value,
            source_agreement=agreement,
            coverage=coverage,
            mixed_valence=clip(mixed),
            irony=bg_sig.cues.scores.get("irony", 0.0),
            length_factor=length_factor,
            model_margin=lex.margin if lex.probs else 0.4,
            single_clause=n_segments <= 1,
        )

    def _build_signals(
        self,
        ctx: LayerContext,
        scores_by_dimension: dict[int, list[AttributeScore]],
        evidence_by_dimension: dict[int, list[Evidence]],
        uncertainty: UncertaintyProfile,
        hypotheses,
        provenance: Provenance,
    ) -> list[DimensionalSignal]:
        """Emit one signal per dimension in ``affinity ∩ scorer_registry.emit_dimensions``."""
        signals: list[DimensionalSignal] = []
        emit_dimensions = sorted(self._emit_dimensions)
        for dimension_id in emit_dimensions:
            attrs = scores_by_dimension.get(dimension_id, [])
            relevance = dimension_relevance([a.relevance for a in attrs])
            abstained = relevance < _RELEVANCE_FLOOR or not attrs
            kept = [] if abstained else attrs[:5]
            state_hint = (
                StateHint(state=kept[0].state, confidence=uncertainty.overall)
                if kept
                else StateHint(state=StatePole.UNCLEAR, confidence=uncertainty.overall)
            )
            if dimension_id == 2:
                evidence = list(evidence_by_dimension.get(2, []))[:3]
            else:
                evidence = [
                    Evidence(
                        kind=EvidenceKind.MAPPING_PATH,
                        detail=f"{h.label} -> " + ", ".join(a.attribute for a in kept[:3]),
                        source="bridge",
                        weight=round(h.probability, 4),
                    )
                    for h in hypotheses[:2]
                ]
            signals.append(
                DimensionalSignal(
                    request_id=ctx.request_id,
                    layer=self.code,
                    layer_version=self.version,
                    dimension_id=dimension_id,
                    relevance=round(0.0 if abstained else relevance, 4),
                    confidence=uncertainty.overall,
                    uncertainty=uncertainty,
                    attribute_scores=kept,
                    state_hint=state_hint,
                    evidence=evidence,
                    abstained=abstained,
                    provenance=provenance,
                )
            )
        return signals

    def _provenance(self, assist=None) -> Provenance:
        used = bool(assist and assist.used)
        attempted = bool(assist and assist.attempted)
        fa = self._field_assist
        return Provenance(
            layer_version=self.version,
            model_id=fa.model_id if (fa and (used or attempted)) else None,
            prompt_version=fa.prompt_version if (fa and (used or attempted)) else None,
            bridge_table_version=(
                getattr(self._bridge_d8, "version", None) if self._bridge_d8 else None
            ),
            field_synthesis_version=self._builder.version,
            appraisal_rules_version=self._appraisal.version,
            patterns_version=self._patterns.version,
            guna_synthesis_version=(
                getattr(self._guna_scorer, "version", None) if self._guna_scorer else None
            ),
            llm_assist_used=used,
            llm_assist_attempted=attempted,
            llm_assist_failure=assist.failure if (assist and attempted and not used) else None,
            llm_assist_gate_reasons=list(assist.reasons) if assist else [],
            samples=assist.samples if used else 0,
        )


def _allowed_slugs(
    concept_registry: IConceptRegistry,
    scorer_registry: IScorerRegistry,
    dimension_id: int,
) -> frozenset[str]:
    slugs = scorer_registry.output_slugs(dimension_id)
    if slugs:
        return slugs
    return concept_registry.slugs(dimension_id)


def build_default_layer() -> AffectLayer:
    """Wire the lean deterministic adapters into the use case (the DI composition root)."""
    from ..infrastructure.affect.linguistic_cues import LinguisticCues
    from ..infrastructure.affect.nrclex_lexical import NRCLexLexicalAffect
    from ..infrastructure.affect.semantic_encoder import build_semantic_encoder
    from ..infrastructure.affect.vader_textblob_vad import VaderTextBlobVAD
    from ..infrastructure.bridge.tables import JsonBridgeTable
    from ..infrastructure.config import Settings
    from ..infrastructure.kg.concept_registry import build_concept_registry
    from ..infrastructure.kg.scorer_registry import build_scorer_registry
    from ..infrastructure.llm.bedrock_provider import BedrockLLMProvider, NullLLMProvider
    from .guna_scorer import GunaFamilyModulator, GunaScorer

    settings = Settings.load()
    concept_registry = build_concept_registry()
    scorer_registry = build_scorer_registry()
    builder = AffectiveFieldBuilder(
        vad=VaderTextBlobVAD(),
        lexical=NRCLexLexicalAffect(),
        cues=LinguisticCues(),
        semantic=build_semantic_encoder(settings=settings, concept_registry=concept_registry),
        synthesis_path=settings.field_synthesis,
    )

    provider: object = NullLLMProvider()
    if settings.enable_llm_assist:
        try:
            provider = BedrockLLMProvider(
                region_name=settings.aws_region,
                read_timeout_s=settings.llm_assist_timeout_s + 10.0,
            )
            logger.info(
                "LLM field-assist enabled (Bedrock model_id=%s, timeout=%.0fs)",
                settings.bedrock_model_id,
                settings.llm_assist_timeout_s,
            )
        except Exception as exc:  # noqa: BLE001
            # Do NOT fall back silently: surface the real cause loudly, then degrade
            # (unless strict mode is requested, in which case fail fast).
            if settings.llm_strict:
                raise ModelUnavailable(
                    f"LLM field-assist is enabled but the Bedrock provider could not be "
                    f"initialized: {exc}"
                ) from exc
            logger.error(
                "LLM field-assist is ENABLED but the Bedrock provider failed to initialize "
                "(%s: %s); falling back to deterministic-only (NullLLMProvider). "
                "Install boto3 and configure AWS credentials/region, or set "
                "SVARUPA_ENABLE_LLM_ASSIST=0 to silence this.",
                type(exc).__name__,
                exc,
            )
            provider = NullLLMProvider()
    field_assist = FieldAssist(
        provider=provider,  # type: ignore[arg-type]
        model_id=settings.bedrock_model_id,
        timeout_s=settings.llm_assist_timeout_s,
        max_tokens=settings.llm_assist_max_tokens,
    )

    guna_scorer: GunaScorer | None = None
    bridges: dict[int, JsonBridgeTable] = {}
    modulator_path = settings.guna_families
    for spec in scorer_registry.scorers():
        if not spec.emits_signals:
            continue
        allowed = _allowed_slugs(concept_registry, scorer_registry, spec.dimension_id)
        if spec.scorer_kind == "field_native":
            if spec.pole_map_path is None:
                raise ValueError(f"field_native scorer D{spec.dimension_id} needs pole_map_ref")
            guna_scorer = GunaScorer(
                spec.data_path,
                spec.pole_map_path,
                allowed_slugs=allowed,
            )
        elif spec.scorer_kind == "hypothesis_bridge":
            bridges[spec.dimension_id] = JsonBridgeTable(
                spec.data_path,
                allowed_slugs=allowed,
            )
            if spec.modulator_path is not None:
                modulator_path = spec.modulator_path

    return AffectLayer(
        builder=builder,
        appraisal=AppraisalReconstructor(settings.appraisal_rules),
        drivers=AffectDriverReconstructor(),
        patterns=ExperientialPatternRecognizer(settings.patterns),
        hypotheses=EmotionHypothesisGenerator(),
        dynamics=AffectDynamicsAnalyzer(settings.interactions),
        assembler=PhenomenologyInputAssembler(),
        guna_scorer=guna_scorer,
        bridges=bridges,
        guna_modulator=GunaFamilyModulator(modulator_path),
        field_assist=field_assist,
        concept_registry=concept_registry,
        scorer_registry=scorer_registry,
        affinity=concept_registry.affinity(),
    )
