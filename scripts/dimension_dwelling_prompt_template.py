"""Prompt template and concept-specific example builders for dimension-dwelling statements."""

from __future__ import annotations

import json
import logging
import os
import random
import re
import time
from dataclasses import dataclass
from typing import Any, Protocol

logger = logging.getLogger(__name__)

DEFAULT_BEDROCK_MODEL_ID = "us.anthropic.claude-opus-4-7"
DEFAULT_AWS_REGION = "us-west-2"
STEP2_MAX_TOKENS = 2048
STEP2_MAX_RETRIES = 3
STEP2_RETRY_DELAY_SEC = 5
STEP2_THROTTLE_MAX_RETRIES = 8
STEP2_THROTTLE_BASE_DELAY = 5
STEP2_THROTTLE_MAX_DELAY = 120

LIVED_EXPERIENCE_MAX_TOKENS = 8192
LIVED_EXPERIENCE_MAX_RETRIES = 3
LIVED_EXPERIENCE_RETRY_DELAY_SEC = 5
LIVED_EXPERIENCE_THROTTLE_MAX_RETRIES = 8
LIVED_EXPERIENCE_THROTTLE_BASE_DELAY = 5
LIVED_EXPERIENCE_THROTTLE_MAX_DELAY = 120

try:
    import boto3
    from botocore.config import Config as BotoConfig
    from botocore.exceptions import ClientError
except ImportError:  # pragma: no cover - exercised when boto3 missing in env
    boto3 = None  # type: ignore[assignment]
    BotoConfig = None  # type: ignore[misc, assignment]
    ClientError = Exception  # type: ignore[misc, assignment]

BEDROCK_TIMEOUT = (
    BotoConfig(read_timeout=300, connect_timeout=15, retries={"max_attempts": 0})
    if BotoConfig is not None
    else None
)


@dataclass(frozen=True)
class ConceptRecord:
    dimension: str  # svarupa_dimensions.slug
    concept: str  # svarupa_concepts.slug
    source_meaning: str
    keywords: tuple[str, ...] = ()
    # svarupa_dimensions
    db_dimension_name: str = ""
    db_dimension_sanskrit_term: str = ""
    # svarupa_concepts
    db_display_name: str = ""  # svarupa_concepts.name
    db_sanskrit_term: str = ""
    db_category: str = ""


@dataclass(frozen=True)
class ConceptProfile:
    display_name: str
    gloss: str
    organizing_subject: str
    organizing_phrase: str
    mention_term: str
    adjacent_concept_hint: str
    spoken_anchor: str = ""


PROMPT_TEMPLATE = """## Input

You will receive a passage describing a concept or dimension from Indian wisdom traditions (e.g., one of the five koshas, a guna, a chakra, a state of consciousness).

## Step 1: Internal Analysis (do not output)

Before writing any statements, silently identify:

- **The distinctive signature** of this dimension — what makes it recognizable as *this* and not something adjacent. What distinguishes someone *dwelling* at this layer from someone who merely passes through it occasionally?
- **The load-bearing test** — for a person whose center of gravity is this dimension, what does this dimension *carry* in their life? What does it organize? What decisions are made through it? What suffering is routed through it? What does wellbeing depend on?
- **The spectrum** of expression: deficient form, balanced form, excessive form
- **The contexts where it surfaces** in ordinary modern life — including interpersonal moments (with family, relatives, friends, colleagues, neighbours, strangers) where the dimension shows up in how the person responds, reacts, withdraws, leans in, judges, or feels touched
- **The somatic/experiential signature** — how this dimension actually feels in lived experience, not how it sounds in books

## Step 2: The Load-Bearing Test (critical)

The single most important test for each statement:

**Does this statement reveal that the dimension is doing load-bearing work in this person's life — that their identity, meaning, suffering, wellbeing, or daily organization is routed through this layer?**

Mere mention of body, energy, mind, intellect, or bliss is not enough. Anyone might mention these. A statement reflects *dwelling at* this dimension only when it discloses that this layer is the **center of gravity** — what the person's life is organized around, what they fall back on, what sets the terms.

{step2_examples}

Apply the equivalent test to whichever dimension is being explored.

## Step 3: Generate Two Sets of 8 Statements

Generate one set from a **Western perspective** and one set from an **Asian perspective**. The cultural difference should show up in the *substance and context* of the lived experience, not in surface details (don't just swap one word for another). The contextual grain — the structure of family, the role of food and care, the rhythms of work and worship, the role of elders, the felt presence of community — should do real work.

A great deal of human experience surfaces *in the presence of, or in interaction with, other people*. Statements should reflect this. Many of the strongest disclosures come from how a person responds physically and emotionally to family members, relatives, friends, colleagues, neighbours, household help, strangers in public, and what they notice in themselves while watching others interact.

### Distribution within each set of 8:

| Life Context | Minimum statements |
|---|---|
| Personal/inner life (self alone, mornings, sleep, habits) | 6 |
| Family and intimate relationships (spouse, parents, children, in-laws, siblings) | 6 |
| Extended relationships (relatives, close friends, neighbours) | 4 |
| Work/professional life (colleagues, manager, team, customers) | 5 |
| Wider social/community interactions (strangers, public spaces, gatherings, observing others) | 5 |
| Transitions between contexts | 4 |

### Across each set of 8, ensure each body-mind layer appears at least 6 times:

- **Physical body** — sensation, energy, sleep, appetite, posture, breath
- **Mental body** — attention quality, thought patterns, decision-making
- **Emotional/vital body** — mood texture, reactivity, energy waves
- **Psychic/soul body** — felt sense of meaning, rightness, intuition, inner knowing. Phrase this so a thoughtful non-spiritual reader would not roll their eyes.

### Within each set of 8, include exactly:

- 2 statements with status **balanced** — healthy, integrated expression of dwelling at this layer (includes subtle background experiences most people miss)
- 2 statements with status **excessive** — stressed, over-activated, or dominated expression of this dimension
- 2 statements with status **deficient** — absence, under-activation, or suppressed expression of this dimension

## Format & Voice

- **First person, present tense**. The voice is a person describing themselves to a therapist, counsellor, doctor, or close friend they trust — someone they are talking to because they would like to understand their experience.
- **2–3 sentences per statement**.
- **Plain spoken language** — the way someone would actually describe themselves out loud, not the way they would write about themselves. No literary flourishes, no insight-laden conclusions, no neat lessons. Real people rarely understand their own patterns clearly.
- **Vary openers naturally**: "I get...", "When I...", "If I...", "I cannot...", "I notice...", "I find myself...", "After...", or simply describing the experience directly. Avoid starting more than 4 consecutive statements with the same opener.
- **The statement must reveal the speaker's own lived experience.** Other people can appear in the statement — that is encouraged — but what is being disclosed is what is happening *in the speaker* in response to or in interaction with them.
- **No commentary about other people's behaviour as an end in itself, no analytical asides, no neat life-lessons.** The speaker is reporting their own experience, not interpreting others.

## Specificity Requirements

- **One small anchor per statement** — a moment, an object, a recurring situation, a person. Just enough to ground the experience. Not a full scene or storyline.
- **Sensory or behavioural detail lightly** — a sensation, a time of day, a small action — but don't build a story around it.
- **Reference everyday modern life** — mornings, meals, sleep, work, family, social occasions, transit, public spaces.
- **No tradition-specific imagery** (no lotuses, sages, ancient rivers).
- **No translated jargon** ("luminous clarity," "groundedness of being," "expansive consciousness"). Use kitchen-table language.
- **Ordinariness is the discipline.** Real people describe themselves in small, partial, sometimes confused ways. They rarely sum themselves up neatly. If a statement sounds wise, insightful, or like a finished thought, it's probably too written.

## Cultural Grain (for the two sets)

**Western perspective — likely textures:** individual or nuclear-family living, the gym, primary care doctors and annual physicals, school drop-off, the commute by car, open-plan offices and video calls, takeout and meal-prep culture, dating apps, weekend brunch, marathon training, weather as seasons (winter coats, first warm day), retirement planning, mortgage, ER visits, the dentist, holiday weekends, neighbours one barely knows, networking events.

**Asian perspective — likely textures (drawn broadly from East, Southeast, and South Asia):** multi-generational and extended-family households or close family involvement even when living apart, food as a primary love and care language, elders' active presence and authority in daily decisions, marriage and reproduction as shared family concerns, the role of household help or live-in caregivers where applicable, the felt weight of being observed and assessed by community, festival and ritual rhythms (lunar new year, harvest festivals, religious holidays, ancestor remembrances), hot food vs. cold food and other folk health beliefs, traditional medicine alongside modern doctors, removing footwear at the threshold, dense urban living and public transport, hierarchy at work, the importance of face and reputation, neighbours and community members who know one's business, food gifts and reciprocity, body and appearance as family-level concerns.

The cultural difference should appear in **what is happening to and around the person — including in the presence of other people** — not just in surface details of consumption.

## Self-check Before Outputting

For each statement, ask:

- **Does this pass the load-bearing test?** Does it reveal that this dimension is doing the organizing work in this person's life — or is it just mentioning the dimension?
- **Could this describe the opposite concept too?** If yes, it's too generic.
- **Is this disclosing something about the speaker's own lived experience** — including when others are present — or is it just describing what someone else did?
- **Is there a small anchor, or just abstract feeling-words?**
- **Does it sound like spoken description, or like a written reflection?**
- **Is it insight-laden in a way ordinary people are not?** If the speaker has too clear a read on their own pattern, it's probably too writerly.
- **Does this overlap too closely with another statement in the set?**

### Signal clarity review (required — revise before output)

After generating the lived-experience statements, review **every** statement against the **expected signals** for this concept context. The statement itself must make these three signals clear, crisp, and unambiguous — without using tradition jargon or naming the dimension/attribute in Sanskrit or technical labels:

1. **Dimension signal** — Would a careful reader reliably infer that this person is organized around *this dimension* (not an adjacent one)? If the experiential cues could equally fit a neighbouring dimension, the signal is muddy — revise.
2. **Attribute / concept signal** — Does the statement disclose the distinctive signature of *this attribute* (the concept named in the Concept context below), not a generic flavour of the parent dimension? If the attribute-specific texture is vague, soft, or interchangeable with a sibling attribute, revise until the cue is precise.
3. **State signal** — Does the experiential pattern clearly and unambiguously match the assigned `"status"` (`balanced` / `excessive` / `deficient`)? A balanced statement must not read as stress or absence; an excessive statement must show over-activation or domination; a deficient statement must show under-activation, absence, or suppression. If status could be misread, revise until the state is unmistakable from the lived detail alone.

**Revision rule:** If any of the three signals is missing, blurred, implied only by wishful reading, or not crisp and precise, **rewrite that lived-experience statement** before including it in the output. Prefer a sharper anchor, a more distinctive behavioural/somatic cue, and clearer status texture — still in plain spoken language. Do not "fix" clarity by adding analytical labels or tradition vocabulary.

After assembling all statements, review them once per perspective set. Identify the 5 weakest (most generic, most likely to apply to any dimension, most writerly, most repetitive, or weakest on dimension / attribute / state signal clarity) and rewrite them with a clearer anchor, plainer language, a stronger disclosure of dwelling-at-this-layer, and unambiguous expected signals. Ensure the final counts still satisfy the 2/2/2 status distribution for each perspective.

{target_quality_examples}

## Output

Return a JSON array of exactly 60 statement objects. Each object must have exactly these three fields:

- `"statement"`: the lived-experience statement (2–3 sentences, first-person, present tense)
- `"status"`: one of `"balanced"`, `"excessive"`, or `"deficient"`
- `"regional_perspective"`: one of `"western"` or `"asian"`

The array must contain exactly 8 objects with `"regional_perspective": "western"` (2 balanced, 2 excessive, 2 deficient) and 8 objects with `"regional_perspective": "asian"` (2 balanced, 2 excessive, 2 deficient).

Output only the raw JSON array — no markdown fences, no preamble, no commentary, no concept name.

---

## Concept context (for generation)

- **Dimension**: {dimension}
- **Concept**: {concept}
- **Display name**: {display_name}
- **Source meaning** (primary semantic authority):

{source_meaning}
"""


STEP2_GENERATION_PROMPT = """You are an expert at calibrating example pairs for a lived experience extraction task. Your job is to produce a small set of ✗/✓ contrast pairs that teach another model the right level of specificity for first-person experience statements about a concept from Indian wisdom traditions.

Input

Dimension: {dimension_name}
Attribute/Sub-concept (if applicable): {attribute_name}
Source passage: {source_passage}

What You Are Generating

Four ✗/✓ pairs of first-person statements about this concept. Each pair shows a failure mode on the ✗ side and the correct calibration on the ✓ side. The four pairs must cover these four failure modes, in this order:

1. Too vague — captures the feeling but has no anchor in everyday life
2. Too narrative — reads like a journal entry, builds a full scene with a story arc
3. Too generic — could describe many adjacent or opposite concepts equally well
4. Too generic (a second instance) — same failure mode, but on a different facet of the concept, to reinforce the pattern

Calibration Rules for the ✓ Statements

- 2–3 sentences, first-person, present tense
- Sound like spoken language, not written language — the way someone describes themselves to a friend or therapist
- One small anchor: a moment, an object, a time of day, a recurring situation. Not a full scene.
- Kitchen-table vocabulary. No Sanskrit. No translated jargon ("luminous clarity," "groundedness of being," etc.). No tradition-specific imagery (lotuses, sages, deities, chakras).
- Reference modern everyday life — mornings, messages, meetings, meals, sleep, conversations.
- The ✓ statement should be the same feeling as the ✗ statement, just calibrated correctly. They are a matched pair, not unrelated examples.

Coverage Rules Across the Four Pairs

- Cover the edges of the concept, not its center. The most obvious expressions of the concept should be left for the downstream model to generate. Your examples should sit on subtler, less-obvious facets — unusual contexts, background experiences, partial expressions — so they teach calibration without giving away common answers.
- Vary the life context across the four pairs: at least one in personal/inner life, one in relational life (family or social), one in work, and the fourth in any context not yet covered.
- Vary the body-mind layer across the four pairs: cover at least three of {{physical, mental, emotional, psychic/soul}}.
- Vary the spectrum across the four pairs: include at least one balanced expression, at least one excessive/stress expression, and at least one deficient/absence expression.

Distinctive Signature Check

Before writing, briefly identify (do not output) what makes {dimension_name}{attribute_suffix} distinctive — what separates it from adjacent concepts a reader might confuse it with. Each ✓ statement should reflect this distinctive signature, so that the statement could not be swapped onto a neighbouring concept without feeling wrong.

Output Format

Produce exactly this structure, nothing else:

✗ Too vague (no anchor at all):
*"[statement]"*

✓ Right level (feeling + small anchor):
*"[statement]"*

✗ Too narrative (reads like a journal entry):
*"[statement]"*

✓ Right level:
*"[statement]"*

✗ Too generic:
*"[statement]"*

✓ Right level:
*"[statement]"*

✗ Too generic:
*"[statement]"*

✓ Right level:
*"[statement]"*

No preamble, no headings, no commentary, no explanation of which life context or layer each pair covers."""


class BedrockStep2Client(Protocol):
    def generate_step2_examples(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model_id: str,
        max_tokens: int,
    ) -> str: ...

    def generate_lived_experience(
        self,
        *,
        user_prompt: str,
        model_id: str,
        max_tokens: int,
    ) -> str: ...


def _resolve_bedrock_model_id(explicit: str | None = None) -> str:
    if explicit and explicit.strip():
        return explicit.strip()
    for key in (
        "SVARUPA_DIMENSION_DWELLING_BEDROCK_MODEL_ID",
        "BEDROCK_MODEL_ID",
        "SVARUPA_EVALUATION_BEDROCK_MODEL_ID_GENERATION",
        "evaluation_bedrock_model_id_generation",
    ):
        value = os.getenv(key, "").strip().strip('"')
        if value:
            return value
    return DEFAULT_BEDROCK_MODEL_ID


def _resolve_aws_region(explicit: str | None = None) -> str:
    if explicit and explicit.strip():
        return explicit.strip()
    for key in ("AWS_REGION", "AWS_DEFAULT_REGION", "SVARUPA_AWS_REGION", "PIPELINE_AWS_REGION"):
        value = os.getenv(key, "").strip()
        if value:
            return value
    return DEFAULT_AWS_REGION


def _strip_fence(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = "\n".join(
            line for line in cleaned.splitlines() if not line.strip().startswith("```")
        )
    return cleaned.strip()



def _log_bedrock_prompt(
    *,
    purpose: str,
    model_id: str,
    system_prompt: str,
    user_prompt: str,
    extra: dict[str, Any] | None = None,
) -> None:
    payload: dict[str, Any] = {
        "purpose": purpose,
        "model_id": model_id,
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
    }
    if extra:
        payload["context"] = extra
    logger.info("Bedrock request\n%s", json.dumps(payload, indent=2, ensure_ascii=False))


def _is_throttle(exc: Exception) -> bool:
    if isinstance(exc, ClientError):
        code = exc.response.get("Error", {}).get("Code", "")
        if code in ("ThrottlingException", "TooManyRequestsException", "ServiceUnavailableException"):
            return True
    name = type(exc).__name__
    return "Throttl" in name or "TooManyRequests" in name


def _validate_step2_examples(text: str, *, display_name: str) -> str:
    cleaned = _strip_fence(text)
    fail_count = cleaned.count("✗")
    pass_count = cleaned.count("✓")
    if fail_count < 4 or pass_count < 4:
        raise ValueError(
            f"Step 2 examples need 4 ✗ and 4 ✓ pairs for {display_name!r} "
            f"(got {fail_count} ✗ / {pass_count} ✓)"
        )
    return cleaned


def _bedrock_converse_with_retry(
    client: Any,
    *,
    system_prompt: str,
    user_prompt: str,
    model_id: str,
    max_tokens: int,
    purpose: str,
    max_retries: int,
    retry_delay_sec: int,
    throttle_max_retries: int,
    throttle_base_delay: int,
    throttle_max_delay: int,
) -> str:
    throttle_attempts = 0
    attempt = 0
    while True:
        try:
            converse_kwargs: dict[str, Any] = {
                "modelId": model_id,
                "messages": [{"role": "user", "content": [{"text": user_prompt}]}],
                "inferenceConfig": {"maxTokens": max_tokens},
            }
            if system_prompt:
                converse_kwargs["system"] = [{"text": system_prompt}]
            response = client.converse(**converse_kwargs)
            content = ""
            for block in response.get("output", {}).get("message", {}).get("content", []):
                if "text" in block:
                    content += block["text"]
            content = _strip_fence(content)
            if not content:
                raise ValueError(f"Empty Bedrock response for {purpose}")
            return content
        except Exception as exc:
            if _is_throttle(exc):
                throttle_attempts += 1
                if throttle_attempts > throttle_max_retries:
                    raise RuntimeError(
                        f"Bedrock throttled after {throttle_max_retries} retries: {exc}"
                    ) from exc
                delay = min(
                    throttle_base_delay * (2 ** (throttle_attempts - 1)) + random.uniform(0, 2),
                    throttle_max_delay,
                )
                logger.warning("Bedrock throttled for %s; backing off %.1fs", purpose, delay)
                time.sleep(delay)
                continue

            attempt += 1
            if attempt < max_retries:
                logger.warning(
                    "Bedrock %s attempt %d/%d failed: %s — retrying in %ds",
                    purpose,
                    attempt,
                    max_retries,
                    exc,
                    retry_delay_sec,
                )
                time.sleep(retry_delay_sec)
                continue
            raise


class Boto3Step2Client:
    """Sync Bedrock client for Step 2 example generation and lived-experience generation."""

    def __init__(self, *, region: str | None = None) -> None:
        if boto3 is None:
            raise RuntimeError(
                "boto3 is required for Bedrock Step 2 generation. Install project dependencies."
            )
        self._region = _resolve_aws_region(region)
        self._client = boto3.client(
            "bedrock-runtime",
            region_name=self._region,
            config=BEDROCK_TIMEOUT,
        )

    def generate_step2_examples(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model_id: str,
        max_tokens: int,
    ) -> str:
        return _bedrock_converse_with_retry(
            self._client,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model_id=model_id,
            max_tokens=max_tokens,
            purpose="Step 2 examples",
            max_retries=STEP2_MAX_RETRIES,
            retry_delay_sec=STEP2_RETRY_DELAY_SEC,
            throttle_max_retries=STEP2_THROTTLE_MAX_RETRIES,
            throttle_base_delay=STEP2_THROTTLE_BASE_DELAY,
            throttle_max_delay=STEP2_THROTTLE_MAX_DELAY,
        )

    def generate_lived_experience(
        self,
        *,
        user_prompt: str,
        model_id: str,
        max_tokens: int,
    ) -> str:
        return _bedrock_converse_with_retry(
            self._client,
            system_prompt="",
            user_prompt=user_prompt,
            model_id=model_id,
            max_tokens=max_tokens,
            purpose="lived-experience generation",
            max_retries=LIVED_EXPERIENCE_MAX_RETRIES,
            retry_delay_sec=LIVED_EXPERIENCE_RETRY_DELAY_SEC,
            throttle_max_retries=LIVED_EXPERIENCE_THROTTLE_MAX_RETRIES,
            throttle_base_delay=LIVED_EXPERIENCE_THROTTLE_BASE_DELAY,
            throttle_max_delay=LIVED_EXPERIENCE_THROTTLE_MAX_DELAY,
        )


_STEP2_CLIENT: BedrockStep2Client | None = None


def get_step2_bedrock_client(*, region: str | None = None) -> BedrockStep2Client:
    global _STEP2_CLIENT
    if _STEP2_CLIENT is None:
        _STEP2_CLIENT = Boto3Step2Client(region=region)
    return _STEP2_CLIENT


def reset_step2_bedrock_client() -> None:
    """Reset cached client (useful in tests)."""
    global _STEP2_CLIENT
    _STEP2_CLIENT = None


def display_name(concept: str) -> str:
    return concept.replace("_", " ").strip()


def parse_keywords(raw: str | None) -> tuple[str, ...]:
    if not raw:
        return ()
    text = raw.strip()
    if not text:
        return ()
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return tuple(str(x).strip() for x in parsed if str(x).strip())
    except json.JSONDecodeError:
        pass
    return tuple(part.strip() for part in text.split(",") if part.strip())


def first_sentence(text: str, *, max_len: int = 220) -> str:
    cleaned = re.sub(r"\s+", " ", text.strip())
    if not cleaned:
        return ""
    match = re.search(r"(?<=[.!?])\s+", cleaned)
    sentence = cleaned[: match.start()] if match else cleaned
    if len(sentence) > max_len:
        sentence = sentence[: max_len - 3].rstrip() + "..."
    return sentence


def infer_profile(record: ConceptRecord) -> ConceptProfile:
    name = record.db_display_name or display_name(record.concept)

    gloss_source = first_sentence(record.source_meaning)
    derived_gloss = (
        gloss_source[0].lower() + gloss_source[1:]
        if gloss_source
        else f"dwelling organized around {name}"
    )

    anchor = record.db_sanskrit_term or (record.keywords[0] if record.keywords else name)
    anchor_lower = anchor.lower()
    adjacent = record.db_category.strip() if record.db_category else "many adjacent human qualities"
    return ConceptProfile(
        display_name=name,
        gloss=derived_gloss,
        organizing_subject=name.title(),
        organizing_phrase=f"{name}-centered dwelling",
        mention_term=anchor_lower,
        adjacent_concept_hint=adjacent,
        spoken_anchor=anchor_lower,
    )


def _voice_anchor(profile: ConceptProfile) -> str:
    return profile.spoken_anchor or profile.display_name


def build_step2_examples(
    profile: ConceptProfile,
    record: ConceptRecord,
    *,
    bedrock_client: BedrockStep2Client | None = None,
    model_id: str | None = None,
    region: str | None = None,
) -> str:
    """Generate Step 2 calibration example pairs via Bedrock Claude."""
    resolved_model_id = _resolve_bedrock_model_id(model_id)
    attribute_suffix = (
        f" / {profile.display_name}"
        if profile.display_name.lower() != record.dimension.lower().replace("_", " ")
        else ""
    )
    dimension_label = record.db_dimension_name or display_name(record.dimension)
    prompt = STEP2_GENERATION_PROMPT.format(
        dimension_name=dimension_label,
        attribute_name=profile.display_name,
        source_passage=record.source_meaning.strip(),
        attribute_suffix=attribute_suffix,
    )
    _log_bedrock_prompt(
        purpose="step2_examples",
        model_id=resolved_model_id,
        system_prompt="",
        user_prompt=prompt,
        extra={
            "dimension": record.dimension,
            "concept": record.concept,
            "display_name": profile.display_name,
        },
    )

    client = bedrock_client or get_step2_bedrock_client(region=region)
    raw = client.generate_step2_examples(
        system_prompt="",
        user_prompt=prompt,
        model_id=resolved_model_id,
        max_tokens=STEP2_MAX_TOKENS,
    )
    validated = _validate_step2_examples(raw, display_name=profile.display_name)
    logger.info(
        "Bedrock Step 2 examples generated | dimension=%s concept=%s chars=%s",
        record.dimension,
        record.concept,
        len(validated),
    )
    return validated


def _example_block(
    *,
    ok: bool,
    heading: str,
    quote: str,
    explanation: str,
) -> str:
    marker = "✓" if ok else "✗"
    return (
        f"\n---\n\n**{marker} {heading}**\n\n"
        f'*"{quote}"*\n\n'
        f"{explanation.rstrip()}\n"
    )


def build_target_quality_examples(profile: ConceptProfile) -> str:
    subject_lower = profile.organizing_subject.lower()
    anchor = _voice_anchor(profile)
    adjacent = profile.adjacent_concept_hint

    blocks = [
        _example_block(
            ok=False,
            heading=f"Fails the load-bearing test — {profile.mention_term} is mentioned but not load-bearing",
            quote=(
                "I've been off lately and something in me keeps slipping. "
                "I wish I could get back to normal."
            ),
            explanation=(
                f"Almost anyone could say this during a difficult stretch. It does not show that "
                f"{subject_lower} organizes this person's week, relationships, or sense of who they are."
            ),
        ),
        _example_block(
            ok=False,
            heading=f"Fails the load-bearing test — a surface habit that doesn't disclose {profile.organizing_phrase}",
            quote=(
                f"I always do the same little routine my mother taught me around {anchor}. "
                "If I skip it I feel unsettled."
            ),
            explanation=(
                f"This is a familiar habit related to {anchor}. People dwelling at {adjacent} "
                f"could say the same. It does not show that {subject_lower} is the load-bearing center."
            ),
        ),
        _example_block(
            ok=False,
            heading="About someone else, not about the speaker's own lived experience",
            quote=(
                "My sister walks into the room and I can tell immediately whether the evening "
                "will be easy or tense."
            ),
            explanation=(
                "This observes someone else's mood or behaviour. The speaker has not disclosed "
                f"what is happening in them through {subject_lower}."
            ),
        ),
        _example_block(
            ok=False,
            heading="Too writerly, too self-aware for ordinary speech",
            quote=(
                f"I am starting to see that {anchor} has been running my life for years, "
                "and I think I am finally ready to understand why."
            ),
            explanation=(
                "Real people rarely deliver this much packaged insight in one breath. "
                "It sounds written, not spoken."
            ),
        ),
        _example_block(
            ok=False,
            heading="Too generic — could describe any dimension",
            quote="I just feel off most days. Nothing feels right and I can't explain it.",
            explanation=(
                f"This is feeling-language without an anchor. It could fit illness, grief, "
                f"burnout, or {adjacent}. It cannot disclose dwelling at {profile.display_name}."
            ),
        ),
        _example_block(
            ok=True,
            heading=f"Right level — {profile.organizing_phrase}, with another person in the frame",
            quote=(
                f"When my father-in-law starts talking about money at dinner, something in me locks up "
                f"before I even answer. By dessert I still am not myself if {anchor} feels threatened."
            ),
            explanation=(
                f"Another person is present, but the disclosure is the speaker's own experience — "
                f"and that experience is load-bearing because {subject_lower} sets the tone for the rest of the evening."
            ),
        ),
        _example_block(
            ok=True,
            heading=f"Right level — {profile.organizing_subject} sets the terms for the speaker's entire week",
            quote=(
                f"I protect one part of every week just to keep {anchor} steady. "
                "It is not a hobby — it is the only thing that keeps me functional with my team by Wednesday."
            ),
            explanation=(
                f"{profile.organizing_subject} is the foundation of the speaker's professional and relational life. "
                "The dimension is doing load-bearing work."
            ),
        ),
        _example_block(
            ok=True,
            heading=f"Right level — {profile.organizing_subject} as final authority over social life",
            quote=(
                "My friends make plans and I want to say yes, but I check first whether I can hold myself together. "
                "If I ignore that, the whole evening is ruined and they think I am being difficult."
            ),
            explanation=(
                f"{profile.organizing_subject} decides, not the speaker. Social plans negotiate around what "
                f"{anchor} will tolerate."
            ),
        ),
        _example_block(
            ok=True,
            heading=f"Right level — {anchor} as identity, ordinary language, no insight overlay",
            quote=(
                f"If I go a few days without tending to {anchor}, I do not feel like myself with my kids. "
                "My partner notices before I do. It is not something I do on the side — it is where I become myself."
            ),
            explanation=(
                f"{profile.organizing_subject} is the location of selfhood. Other people are in the frame, "
                "and the speaker reports the pattern without a neat lesson."
            ),
        ),
        _example_block(
            ok=True,
            heading=f"Right level — {anchor}-mediated reading of others, disclosing the speaker's own experience",
            quote=(
                "At a family gathering, if someone hugs me and feels closed off, I am flat the rest of the night. "
                f"Something in me has already decided the evening is heavy."
            ),
            explanation=(
                f"The speaker is with others, but the disclosure is their own experience — and that experience "
                f"is load-bearing because {subject_lower} shapes the rest of the evening."
            ),
        ),
    ]

    intro = (
        "## Examples of the Target Quality\n\n"
        f"The examples below use **{profile.display_name}** ({profile.gloss}) as the working illustration. "
        "The same logic applies to whichever dimension is being explored.\n"
    )
    return intro + "".join(blocks)


def build_prompt(
    record: ConceptRecord,
    *,
    bedrock_client: BedrockStep2Client | None = None,
    model_id: str | None = None,
    region: str | None = None,
) -> str:
    profile = infer_profile(record)
    dimension_label = record.db_dimension_name or display_name(record.dimension)
    concept_label = record.db_display_name or display_name(record.concept)
    return PROMPT_TEMPLATE.format(
        step2_examples=build_step2_examples(
            profile,
            record,
            bedrock_client=bedrock_client,
            model_id=model_id,
            region=region,
        ),
        target_quality_examples=build_target_quality_examples(profile),
        dimension=dimension_label,
        concept=concept_label,
        display_name=profile.display_name,
        source_meaning=record.source_meaning.strip(),
    )


_WESTERN_PERSPECTIVE_RE = re.compile(r"(?im)^.*western\s+perspective.*$")
_ASIAN_PERSPECTIVE_RE = re.compile(r"(?im)^.*asian\s+perspective.*$")


def split_lived_experience_perspectives(text: str) -> tuple[str, str]:
    """Split a lived-experience response into (western, asian) statement blocks."""
    western_match = _WESTERN_PERSPECTIVE_RE.search(text)
    asian_match = _ASIAN_PERSPECTIVE_RE.search(text)
    if not western_match or not asian_match:
        raise ValueError("Response is missing Western/Asian perspective section headers")
    if western_match.start() < asian_match.start():
        western_text = text[western_match.end() : asian_match.start()]
        asian_text = text[asian_match.end() :]
    else:
        asian_text = text[asian_match.end() : western_match.start()]
        western_text = text[western_match.end() :]
    return western_text.strip(), asian_text.strip()


_STATEMENT_NUMBER_RE = re.compile(r"^\s*(\d{1,3})[.\):]\s*(.*)$")


def split_statements(text: str) -> list[str]:
    """Split a numbered block of statements into a list of individual statement strings.

    Lines that continue a numbered statement (no leading ``N.``) are joined onto the
    previous statement, so this tolerates statements wrapped across multiple lines.
    """
    statements: list[str] = []
    current: list[str] = []
    for line in text.splitlines():
        match = _STATEMENT_NUMBER_RE.match(line)
        if match:
            if current:
                statements.append(" ".join(current).strip())
            current = [match.group(2).strip()]
        else:
            stripped = line.strip()
            if stripped:
                current.append(stripped)
    if current:
        statements.append(" ".join(current).strip())
    return [s for s in statements if s]


_VALID_STATUSES = frozenset({"balanced", "excessive", "deficient"})
_VALID_PERSPECTIVES = frozenset({"western", "asian"})


def parse_lived_experience_json(text: str) -> list[dict]:
    """Parse a JSON-format lived-experience response into a list of statement dicts.

    Each dict has keys: ``statement``, ``status``, ``regional_perspective``.
    Raises ``ValueError`` if the JSON is malformed or contains unexpected values.
    """
    cleaned = _strip_fence(text)
    start = cleaned.find("[")
    end = cleaned.rfind("]")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Lived-experience response does not contain a JSON array")
    try:
        data = json.loads(cleaned[start : end + 1])
    except json.JSONDecodeError as exc:
        raise ValueError(f"Lived-experience JSON parse error: {exc}") from exc
    if not isinstance(data, list):
        raise ValueError("Expected a JSON array of statement objects")
    validated: list[dict] = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"Item {i} is not a JSON object")
        missing = {"statement", "status", "regional_perspective"} - item.keys()
        if missing:
            raise ValueError(f"Item {i} missing required keys: {sorted(missing)}")
        status = item["status"]
        perspective = item["regional_perspective"]
        if status not in _VALID_STATUSES:
            raise ValueError(
                f"Item {i} has invalid status {status!r}; expected one of {sorted(_VALID_STATUSES)}"
            )
        if perspective not in _VALID_PERSPECTIVES:
            raise ValueError(
                f"Item {i} has invalid regional_perspective {perspective!r}; "
                f"expected one of {sorted(_VALID_PERSPECTIVES)}"
            )
        validated.append(
            {
                "statement": str(item["statement"]).strip(),
                "status": status,
                "regional_perspective": perspective,
            }
        )
    return validated


def generate_lived_experience_text(
    prompt_text: str,
    *,
    bedrock_client: BedrockStep2Client | None = None,
    model_id: str | None = None,
    region: str | None = None,
    max_tokens: int = LIVED_EXPERIENCE_MAX_TOKENS,
) -> str:
    """Run an assembled dimension-dwelling prompt through Bedrock Claude and return the raw response."""
    resolved_model_id = _resolve_bedrock_model_id(model_id)
    _log_bedrock_prompt(
        purpose="lived_experience",
        model_id=resolved_model_id,
        system_prompt="",
        user_prompt=prompt_text,
    )
    client = bedrock_client or get_step2_bedrock_client(region=region)
    raw = client.generate_lived_experience(
        user_prompt=prompt_text,
        model_id=resolved_model_id,
        max_tokens=max_tokens,
    )
    cleaned = _strip_fence(raw)
    logger.info("Bedrock lived-experience response generated | chars=%s", len(cleaned))
    return cleaned
