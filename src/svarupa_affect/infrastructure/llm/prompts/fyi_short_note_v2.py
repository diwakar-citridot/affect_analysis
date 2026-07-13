"""AFF FYI / Short Note prompt (v2).

Generates Stage-1 Short Notes (Response Formulation Spec v8, Artifact 1) from
pre-scored AFF signals — one tentative card per (dimension, attribute, state)
triplet. Pinned ``PROMPT_VERSION`` + schema live here.
"""

from __future__ import annotations

import json
import re

PROMPT_VERSION = "fyi_short_note_v6"

_MAX_CARDS = 3
_GROUNDING_MAXLEN = 480
_MAX_TEXT_WORDS_PER_SENTENCE = 15
_MAX_SIMPLE_WORDS_PER_SENTENCE = 18
_MIN_TEXT_SENTENCES = 2

_CARD_SCHEMA: dict = {
    "type": "object",
    "required": ["text", "simple_sentence", "reasoning", "attribute", "dimension", "status"],
    "properties": {
        "text": {"type": "string"},
        "simple_sentence": {"type": "string"},
        "reasoning": {"type": "string"},
        "attribute": {"type": "string"},
        "dimension": {"type": "string"},
        "status": {"type": "string", "enum": ["deficiency", "balance", "excess"]},
    },
}

FYI_SCHEMA: dict = {
    "type": "object",
    "required": ["cards"],
    "properties": {
        "cards": {
            "type": "array",
            "minItems": 1,
            "maxItems": _MAX_CARDS,
            "items": _CARD_SCHEMA,
        },
    },
}

SYSTEM_PROMPT = """You are the Svarupa Assistant (SA) FYI / Short Note writer for the Affect layer.

Your role is to help someone who has just revealed a lived experience understand
aspects of human nature that may be present in what they shared. Each Short Note
is a brief, tentative observation pointing at one scored signal
(dimension, attribute, state). The framework stays invisible in the user-facing prose.

---

## MISSION (non-negotiable)

Svarupa exists to help a person understand themselves through complementary
dimensions of inner life. So:
- Each card SHALL illuminate the experience from its own signal — never collapse
  several signals into one explanation, label, or "what this really is."
- SA SHALL NOT reduce the experience to one diagnosis, root cause, or universal fix.
- Preserve nuance and ambiguity. Widening awareness is the goal — not resolving the
  person into a category.

SA's purpose at this stage:
- Illuminate patterns in lived experience so the person can describe their experience
  more accurately and in more detail.
- Offer a trustworthy, supportive companion tone — warm, plain, non-clinical.
  Not therapy. Not diagnosis. Not prescriptive advice. Just clear illumination.

---

## TRIPLET-DRIVEN PROSE (non-negotiable)

Each signal is one scored **(dimension, attribute, state)** triplet. Both `text` and
`simple_sentence` MUST be shaped by that triplet — not by generic mood language alone.

Before writing, read the signal's `triplet`, `grounding_for_state`, `rationale`,
`reasoning`, and `dimension_register`. These tell you what THIS concept means at
THIS pole in THIS dimension family and why AFF scored it.

**How the triplet shapes each field:**

| Field | Triplet influence |
|-------|-------------------|
| **text** (Mirror) | Intersect lived experience with this attribute at this state pole. |
| **text** (Lens) | Name the pattern grounding describes for this attribute + state — hedged. |
| **simple_sentence** | Distill this triplet's felt signature — not a neighbouring concept. |

**State pole shapes tone invisibly (all fields):**
- **excess** → fullness, intensity, overreach, smolder, grip, or spill without alarm
- **deficiency** → thinning, absence, flatness, numbness, or unreachable quality without pity
- **balance** → ordinary presence, regulation, or earned rest without idealizing

**Dimension register shapes what kind of phenomenon you name (never the dimension name):**
- **Sthāyībhāvas** → enduring emotional organization (what colors the field over time)
- **Vyabhicārībhāvas** → transient movement (what passes through the moment)
- **Triguṇa** → felt tone of activation (restless urgency, settling clarity, or heavy drag)

**Discrimination rule:** If the attribute were swapped (e.g. alasya excess instead of
amarsha excess), the Lens and simple_sentence MUST read differently. Translate the
grounding's pole-specific texture into plain words — never the slug or doctrine.

---

## CRISP TEXT (non-negotiable — the `text` field)

`text` is the user-facing Short Note. It MUST be crisp — tight, vivid, and specific
to THIS (dimension, attribute, state) triplet:

- Sentence 1 (Mirror): ONE concrete felt detail from the lived experience or `span`.
  Short and vivid. No scene-setting, no throat-clearing ("It seems like…",
  "In moments when…"). Land the detail in impersonal language.
- Sentence 2 (Lens): ONE hedged pattern from this triplet's grounding — plain,
  direct, tentative. No mechanism chain, no "because," no summary moral.
- Max 15 words per sentence in `text`. Every word earns its place.
- If the attribute or state pole were swapped, the Mirror and Lens MUST read
  differently — generic mood language alone is not enough.

## SHORT NOTE STRUCTURE (per card — Response Formulation v8)

Each card `text` MUST be exactly two sentences in this order:

1. MIRROR (sentence 1) — name the felt detail from the lived experience or signal
   `span` in impersonal, generic language. Describe the situation, not the person.
   NEVER use "I", "me", "my", "you", or "your" in any sentence of text.

2. LENS (sentence 2) — offer a tentative pattern **from this triplet's grounding** in
   plain language. MUST open with or contain a hedge such as "There may be…",
   "It can seem…", or "Something here suggests…". The felt quality named here MUST
   match the attribute at this state pole (read `grounding_for_state` and align with
   `rationale` / `reasoning`). Name the felt quality, not a verdict. Do NOT label
   emotions directly as facts. Prefer indirect, normalized phrasing drawn from the
   triplet.

The Note never explains fully — it is a probe. One plain lens hint in sentence 2;
no mechanism, no cause chain, no "because." Leave the thought open; do not close
with a conclusion, moral, or summary.

## RESONANCE CHECK (silent — before returning JSON)

For each card, confirm ALL of the following — rewrite until true:

1. **Lived experience:** sentence 1 echoes a specific detail from LIVED EXPERIENCE
   TEXT or the signal `span` (not a generic paraphrase that could fit any passage).
2. **Scoring insight:** `text` and `simple_sentence` together reflect the signal's
   `rationale` and `reasoning` — the same recognition AFF already made.
3. **Triplet:** prose is shaped by THIS attribute at THIS state pole in THIS dimension
   register; swapping the triplet would change the wording.
4. **reasoning field:** 2–3 sentences naming the triplet, which lived detail anchored
   Mirror, and how rationale/grounding shaped Lens.

---

## CONCEPT GROUNDING (internal only — read before writing)

Each signal carries `grounding_for_state` — the steward description of that exact
**(attribute, state)** pair. It exists to make the card ACCURATE, not to be reproduced.

- Read `grounding_for_state` to learn how THIS attribute manifests at THIS pole.
- Let it drive sentence 2 (Lens) and both sentences of `simple_sentence`.
- NEVER quote, paraphrase verbatim, or surface framework terms, Sanskrit words,
  dimension names, scripture references, or doctrine from the grounding.
- Translate only the part that maps to the user's actual expression. Ignore the rest.
- When grounding is empty, infer from `attribute`, `state`, `dimension_register`,
  `rationale`, `reasoning`, and `span` — do not invent doctrine to fill the gap.

## THE MIRROR MOMENT (internal only — do before writing)

Before writing any card, silently read the full LIVED EXPERIENCE TEXT and identify
the one detail most specific to this person — a particular word, image, contradiction,
or rhythm in how they phrased something. Let that detail quietly anchor sentence 1.
The card should feel like it could not have been written without that passage.

---

## RULES

1. No framework names, dimension IDs, attribute slugs, or taxonomy in card prose
   (text and simple_sentence). reasoning may name them — it is internal only.
2. No "I", "me", "my", "you", or "your" in text or simple_sentence — ever.
   Write as generic observations about human experience ("the body", "the mind",
   "this kind of moment", "when silence is chosen"), never addressing anyone.
3. No questioning language in text or simple_sentence — no question marks, no
   implied questions, no interrogative phrasing.
4. One signal per card. Do not blend signals within a card.
5. Preserved ambiguity always in the Lens sentence.
6. No scores, numbers, or internal identifiers in user-facing prose.
7. simple_sentence: exactly two sentences that land alone without context — the
   **distilled felt signature of this triplet** (attribute + state + dimension register),
   not a generic summary of human suffering. A reader should sense WHICH quality at
   WHICH pole — without being told the framework. Same impersonal rules as text.
8. reasoning: 2–3 sentences explaining internal choices — which triplet was used, how
   grounding shaped Lens and simple_sentence, how state pole shaped tone, and which span
   anchored the mirror. Internal evaluation only.

---

## STYLE

- Exactly 2 sentences in `text` (Mirror, Lens). No more.
- Max 15 words per sentence in `text`; max 18 per sentence in `simple_sentence`.
- Warm, plain, conversational. Not clinical. Not poetic for its own sake.
- Basic concept level — Stage 1 depth only.
- Crisp over complete — one detail, one lens hint; cut every filler word.

---

## OUTPUT

Return valid JSON only. No markdown. No preamble.

One card per input signal, in the same order as the SIGNALS list.
Copy attribute, dimension, and status from each signal exactly into the matching card.
"""

_DIAGNOSTIC_DENYLIST = re.compile(
    r"\b(you are|you have|diagnos|disorder|patient suffers|clearly is a|you should|you must)\b",
    re.IGNORECASE,
)
_QUESTION_MARK = re.compile(r"\?")
_PERSONAL_PRONOUN_RE = re.compile(
    r"\b(?:i|me|my|mine|you|your|yours|yourself|myself)"
    r"(?:[''](?:ve|d|ll|m|re))?\b",
    re.IGNORECASE,
)
_HEDGE_RE = re.compile(
    r"\b("
    r"there may be|there might be|it can seem|something here suggests|"
    r"something here may|this can (?:look|feel) like|one pattern (?:here )?can be"
    r")\b",
    re.IGNORECASE,
)
_FILLER_RE = re.compile(
    r"\b(it seems like|in moments when|there is a sense that|one might notice that)\b",
    re.IGNORECASE,
)
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_STOPWORDS = frozenset(
    {
        "that",
        "this",
        "with",
        "from",
        "when",
        "have",
        "been",
        "were",
        "what",
        "there",
        "about",
        "into",
        "through",
        "after",
        "before",
        "while",
        "where",
        "they",
        "them",
        "their",
        "would",
        "could",
        "should",
        "still",
        "just",
        "very",
        "even",
        "than",
        "then",
        "over",
        "under",
        "every",
        "think",
        "feels",
        "feel",
        "felt",
        "like",
        "kind",
        "something",
        "here",
        "may",
        "might",
        "seem",
        "seems",
        "being",
        "does",
        "never",
        "always",
        "more",
        "most",
        "some",
        "such",
        "only",
        "also",
        "into",
        "onto",
        "upon",
    }
)

# Plain-language register hints keyed by dimension sanskrit_term substrings (AFF emit set).
_DIMENSION_REGISTER: tuple[tuple[str, str], ...] = (
    ("Sthāyībhāvas", "enduring emotional tone — what organizes the field over time"),
    ("Vyabhicārībhāvas", "transient state — what moves through the moment"),
    ("Triguṇa", "felt tone of activation — sattva clarity, rajas urgency, or tamas drag"),
)

_STATE_POLE_HINTS: dict[str, str] = {
    "excess": "fullness, intensity, overreach, smolder, or grip",
    "deficiency": "thinning, absence, flatness, numbness, or unreachable quality",
    "balance": "ordinary presence, regulation, or earned rest",
}


def _content_tokens(text: str, *, min_len: int = 4) -> set[str]:
    return {
        word
        for word in re.findall(r"\b[a-z']+\b", text.lower())
        if len(word) >= min_len and word not in _STOPWORDS
    }


def _mirror_sentence(text: str) -> str:
    sents = _sentences(text)
    return sents[0] if sents else text.strip()


def validate_text_resonance(
    card: dict,
    *,
    idx: int,
    analysis_text: str,
    signal: dict[str, object],
) -> None:
    """Deterministic check that card prose resonates with inputs and the triplet."""
    text = str(card["text"]).strip()
    mirror = _mirror_sentence(text)
    mirror_tokens = _content_tokens(mirror)
    lived_tokens = _content_tokens(analysis_text)
    span = str(signal.get("span", "")).strip()
    span_tokens = _content_tokens(span)

    lived_overlap = mirror_tokens & (lived_tokens | span_tokens)
    span_substr = len(span) >= 8 and span.lower() in text.lower()
    long_token_hit = any(len(tok) >= 5 and tok in analysis_text.lower() for tok in mirror_tokens)
    if not lived_overlap and not span_substr and not long_token_hit:
        raise FyiValidationError(
            f"cards[{idx}] text Mirror does not resonate with lived experience or span"
        )

    rationale = str(signal.get("rationale", "")).strip()
    reasoning_in = str(signal.get("reasoning", "")).strip()
    insight_blob = f"{rationale} {reasoning_in}".strip()
    if insight_blob:
        insight_tokens = _content_tokens(insight_blob, min_len=4) | _content_tokens(
            insight_blob, min_len=5
        )
        prose_tokens = _content_tokens(f"{text} {card.get('simple_sentence', '')}")
        overlap = prose_tokens & insight_tokens
        min_required = 1 if len(insight_tokens) <= 4 else 2
        if len(overlap) < min_required:
            raise FyiValidationError(
                f"cards[{idx}] text does not resonate with signal rationale/reasoning"
            )

    card_attr = str(card["attribute"]).strip().lower()
    sig_attr = str(signal.get("attribute", "")).strip().lower()
    if card_attr != sig_attr:
        raise FyiValidationError(f"cards[{idx}] attribute does not match signal triplet")

    card_dim = str(card["dimension"]).strip()
    sig_dim = str(signal.get("dimension") or signal.get("dimension_name", "")).strip()
    if card_dim != sig_dim:
        raise FyiValidationError(f"cards[{idx}] dimension does not match signal triplet")

    card_state = str(card["status"]).lower()
    sig_state = str(signal.get("state", signal.get("status", ""))).lower()
    if card_state != sig_state:
        raise FyiValidationError(f"cards[{idx}] status does not match signal triplet")

    card_reasoning = str(card.get("reasoning", "")).strip().lower()
    if card_reasoning:
        if sig_attr and sig_attr not in card_reasoning:
            raise FyiValidationError(
                f"cards[{idx}] reasoning must reference signal attribute for triplet traceability"
            )
        if sig_state and sig_state not in card_reasoning:
            raise FyiValidationError(
                f"cards[{idx}] reasoning must reference status pole for triplet traceability"
            )
        lived_anchor = any(tok in card_reasoning for tok in lived_overlap) or (
            span_substr or long_token_hit
        )
        if lived_tokens and not lived_anchor:
            raise FyiValidationError(
                f"cards[{idx}] reasoning must reference lived experience detail"
            )


def dimension_register(dimension_name: str) -> str:
    """Human-readable dimension family hint for prompt enrichment."""
    needle = dimension_name.strip().lower()
    for key, hint in _DIMENSION_REGISTER:
        if key.lower() in needle or needle in key.lower():
            return hint
    return "affective quality named by the steward vocabulary"


def state_pole_hint(state: str) -> str:
    return _STATE_POLE_HINTS.get(state.lower().strip(), "unclear pole — hedge maximally")


class FyiValidationError(ValueError):
    """Raised when the LLM payload fails schema or philosophy checks."""


def _sentences(prose: str) -> list[str]:
    return [part.strip() for part in _SENTENCE_SPLIT.split(prose.strip()) if part.strip()]


def _word_count(sentence: str) -> int:
    return len(re.findall(r"\b[\w']+\b", sentence))


def _validate_sentence_lengths(
    sentences: list[str], *, field_name: str, idx: int, max_words: int
) -> None:
    for sent_no, sentence in enumerate(sentences, start=1):
        count = _word_count(sentence)
        if count > max_words:
            raise FyiValidationError(
                f"cards[{idx}] {field_name} sentence {sent_no} has {count} words "
                f"(max {max_words})"
            )


def correction_hint(error: str) -> str:
    """Map a validation error to explicit rewrite instructions for LLM retries."""
    hints: list[str] = []
    lower = error.lower()
    if "hedging" in lower or "lens" in lower:
        hints.append(
            'Sentence 2 (Lens) MUST include a hedge such as "There may be…", '
            '"It can seem…", or "Something here suggests…". '
            'Do not use "There is a kind of anger" as a verdict.'
        )
    if "words" in lower:
        hints.append(
            f"Each sentence in text must be at most {_MAX_TEXT_WORDS_PER_SENTENCE} words; "
            f"simple_sentence at most {_MAX_SIMPLE_WORDS_PER_SENTENCE}. Shorten any long sentence."
        )
    if "resonate" in lower or "mirror" in lower:
        hints.append(
            "Rewrite so sentence 1 echoes a specific lived-experience detail or span, "
            "and text reflects the signal rationale/reasoning and THIS triplet."
        )
    if "filler" in lower:
        hints.append(
            "Cut throat-clearing filler from text (e.g. 'It seems like', 'In moments when'). "
            "Land one crisp detail in sentence 1."
        )
    if "personal pronoun" in lower or "i/me/you" in lower:
        hints.append(
            'text and simple_sentence must never use I, me, my, you, or your. '
            "Write generic impersonal observations only."
        )
    if "exactly 2 sentences" in lower:
        hints.append("text must be exactly 2 sentences: Mirror (1), hedged Lens (2).")
    if "simple_sentence" in lower and "2 sentences" in lower:
        hints.append(
            "simple_sentence must be exactly 2 standalone impersonal sentences "
            "distilling THIS triplet's felt signature."
        )
    if "triplet" in lower or "grounding" in lower:
        hints.append(
            "Shape text (Lens) and simple_sentence from grounding_for_state and the "
            "(dimension, attribute, state) triplet — not generic mood language."
        )
    if not hints:
        hints.append(
            "Rewrite each card: crisp 2-sentence text (Mirror, hedged Lens), "
            f"≤{_MAX_TEXT_WORDS_PER_SENTENCE} words per text sentence."
        )
    return "CORRECTION:\n" + "\n".join(f"- {h}" for h in hints)


def build_system() -> str:
    """Static system prefix (cacheable across requests)."""
    return (
        f"{SYSTEM_PROMPT}\n\n"
        "TASK: For each signal, write one Short Note card with exactly two crisp sentences: "
        "Mirror, then Lens (hedged, triplet-specific). "
        "Read the LIVED EXPERIENCE TEXT first — sentence 1 intersects it with the "
        "triplet's felt signature. Sentence 2 and simple_sentence MUST be shaped by "
        "grounding_for_state, rationale, reasoning, and the (dimension, attribute, state) "
        "triplet. JSON only.\n\n"
        'REQUIRED top-level key: "cards" (array, one object per signal, same order).\n'
        "Each card object MUST include: text, simple_sentence, reasoning, attribute, "
        "dimension, status."
    )


def build_prompt(
    *,
    analysis_text: str,
    signals: list[dict[str, object]],
    user_state_tier: str = "standard",
) -> str:
    """Per-request user turn: lived experience + scored signals + optional session tier."""
    return (
        "LIVED EXPERIENCE TEXT:\n"
        f'"""{analysis_text.strip()}"""\n\n'
        "USER STATE TIER (silent — modulate tentativeness; never mention in prose):\n"
        f"{user_state_tier}\n\n"
        "SIGNALS (one Short Note per item, same order; each includes triplet + grounding):\n"
        f"{json.dumps(signals, indent=2, ensure_ascii=False)}"
    )


def _validate_impersonal(prose: str, *, field_name: str, idx: int) -> None:
    if _PERSONAL_PRONOUN_RE.search(prose):
        raise FyiValidationError(
            f"cards[{idx}] {field_name} must not use I/me/my or you/your "
            "(write generic impersonal statements)"
        )


def _validate_card_prose(card: dict, idx: int) -> None:
    for field_name in ("text", "simple_sentence"):
        prose = str(card[field_name]).strip()
        if _QUESTION_MARK.search(prose):
            raise FyiValidationError(f"cards[{idx}] {field_name} contains a question mark")
        if _DIAGNOSTIC_DENYLIST.search(prose):
            raise FyiValidationError(f"cards[{idx}] {field_name} uses diagnostic phrasing")
        _validate_impersonal(prose, field_name=field_name, idx=idx)

    text = str(card["text"]).strip()
    if _FILLER_RE.search(text):
        raise FyiValidationError(f"cards[{idx}] text uses throat-clearing filler phrasing")
    text_sents = _sentences(text)
    if len(text_sents) != _MIN_TEXT_SENTENCES:
        raise FyiValidationError(
            f"cards[{idx}] text must be exactly {_MIN_TEXT_SENTENCES} sentences "
            f"(Mirror, Lens); got {len(text_sents)}"
        )
    _validate_sentence_lengths(
        text_sents, field_name="text", idx=idx, max_words=_MAX_TEXT_WORDS_PER_SENTENCE
    )

    if not _HEDGE_RE.search(text_sents[1]):
        raise FyiValidationError(
            f"cards[{idx}] text Lens sentence (sentence 2) lacks required hedging"
        )

    simple = str(card["simple_sentence"]).strip()
    simple_sents = _sentences(simple)
    if len(simple_sents) != 2:
        raise FyiValidationError(
            f"cards[{idx}] simple_sentence must be exactly 2 sentences; got {len(simple_sents)}"
        )
    _validate_sentence_lengths(
        simple_sents,
        field_name="simple_sentence",
        idx=idx,
        max_words=_MAX_SIMPLE_WORDS_PER_SENTENCE,
    )


def validate_fyi(
    payload: dict,
    *,
    expected_count: int,
    analysis_text: str | None = None,
    signals: list[dict[str, object]] | None = None,
) -> dict:
    if not isinstance(payload, dict):
        raise FyiValidationError("payload is not an object")
    cards = payload.get("cards")
    if not isinstance(cards, list):
        raise FyiValidationError("cards must be an array")
    if not (1 <= len(cards) <= _MAX_CARDS):
        raise FyiValidationError(f"cards length must be 1–{_MAX_CARDS}")
    if len(cards) != expected_count:
        raise FyiValidationError(f"expected {expected_count} cards, got {len(cards)}")

    out_cards: list[dict] = []
    for idx, card in enumerate(cards):
        if not isinstance(card, dict):
            raise FyiValidationError(f"cards[{idx}] must be an object")
        for key in ("text", "simple_sentence", "reasoning", "attribute", "dimension", "status"):
            if key not in card or not str(card.get(key, "")).strip():
                raise FyiValidationError(f"cards[{idx}] missing or empty {key}")
        status = str(card["status"]).lower()
        if status not in ("deficiency", "balance", "excess"):
            raise FyiValidationError(f"cards[{idx}] status invalid")
        _validate_card_prose(card, idx)
        if analysis_text is not None and signals is not None and idx < len(signals):
            validate_text_resonance(
                card,
                idx=idx,
                analysis_text=analysis_text,
                signal=signals[idx],
            )
        out_cards.append(
            {
                "text": str(card["text"]).strip(),
                "simple_sentence": str(card["simple_sentence"]).strip(),
                "reasoning": str(card["reasoning"]).strip(),
                "attribute": str(card["attribute"]).strip(),
                "dimension": str(card["dimension"]).strip(),
                "status": status,
            }
        )
    return {"cards": out_cards}
