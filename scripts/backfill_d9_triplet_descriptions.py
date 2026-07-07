#!/usr/bin/env python3
"""Backfill missing D9 (Vyabhicārībhāva) per-status triplet descriptions.

Primary source: ``documentation/dimension_descriptions/9-Vyabhicaribhavas_Lived_Experience_UPDATED.docx``
Fallback: concept gloss in ``svarupa_concepts.description`` + steward-authored poles.

Upserts ``svarupa_concept_descriptions`` rows with ``perspective = 'overview'`` (the
export snapshot's preferred perspective). Regenerate the snapshot after running:

    PYTHONPATH=src python scripts/backfill_d9_triplet_descriptions.py
    PYTHONPATH=src python scripts/export_aff_triplet_descriptions.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from docx import Document

from svarupa_affect.infrastructure.config import Settings
from svarupa_affect.infrastructure.kg.mysql_client import open_mysql

DOC_PATH = (
    Path(__file__).resolve().parents[1]
    / "documentation"
    / "dimension_descriptions"
    / "9-Vyabhicaribhavas_Lived_Experience_UPDATED.docx"
)
STATUSES = ("deficiency", "balance", "excess")
STATUS_HEADERS = {
    "balance": "### The Equilibrium",
    "excess": "### The Excess",
    "deficiency": "### The Deficiency",
}
PERSPECTIVE = "overview"

# Doc heading / prose aliases -> DB slug
SLUG_ALIASES: dict[str, str] = {
    "nirveda": "nirveda",
    "cinta": "cinta",
    "cintā": "cinta",
    "visada": "visada",
    "viṣāda": "visada",
    "alasya": "alasya",
    "ālasya": "alasya",
    "glani": "glani",
    "glāni": "glani",
    "sanka": "sanka",
    "śaṅkā": "sanka",
    "trasa": "trasa",
    "trāsa": "trasa",
    "capalata": "capalata",
    "capalatā": "capalata",
    "avega": "avega",
    "āvega": "avega",
    "amarsa": "amarsha",
    "amarṣa": "amarsha",
    "garva": "garva",
    "mada": "mada",
    "asuya": "asuya",
    "asūyā": "asuya",
    "vrida": "vrida",
    "vrīḍā": "vrida",
    "avahittha": "avahittha",
    "avahitthā": "avahittha",
    "moha": "moha",
    "smrti": "smrti",
    "smṛti": "smrti",
    "harsa": "harsa",
    "harṣa": "harsa",
    "dhrti": "dhrti",
    "dhṛti": "dhrti",
    "mati": "mati",
    "vibodha": "vibodha",
    "jadata": "jadata",
    "jaḍatā": "jadata",
    "nidra": "nidra",
    "nidrā": "nidra",
    "supta": "supta",
    "unmada": "unmada",
    "unmāda": "unmada",
    "autsukya": "autsukya",
    "vitarka": "vitarka",
    "apasmara": "apasmara",
    "apasmāra": "apasmara",
    "dainya": "dainya",
    "srama": "srama",
    "śrama": "srama",
    "marana": "marana",
    "maraṇa": "marana",
    "ugrata": "ugrata",
    "ugratā": "ugrata",
    "vyadhi": "vyadhi",
}

STATUS_HEADING = {
    "the equilibrium": "balance",
    "equilibrium": "balance",
    "the excess": "excess",
    "excess": "excess",
    "the deficiency": "deficiency",
    "deficiency": "deficiency",
}

# Shared doc sections -> individual slugs
SECTION_CONCEPTS: dict[str, list[str]] = {
    "cinta and visada": ["cinta", "visada"],
    "cintā and viṣāda": ["cinta", "visada"],
    "ālasya and glāni": ["alasya", "glani"],
    "alasya and glani": ["alasya", "glani"],
    "śaṅkā and trāsa": ["sanka", "trasa"],
    "sanka and trasa": ["sanka", "trasa"],
    "capalatā and āvega": ["capalata", "avega"],
    "capalata and avega": ["capalata", "avega"],
    "dhṛti and mati": ["dhrti", "mati"],
    "dhrti and mati": ["dhrti", "mati"],
    "autsukya and vitarka": ["autsukya", "vitarka"],
}


def _norm_key(text: str) -> str:
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()


def _slug_from_token(token: str) -> str | None:
    key = token.lower().strip()
    if key in SLUG_ALIASES:
        return SLUG_ALIASES[key]
    nk = _norm_key(key)
    for alias, slug in SLUG_ALIASES.items():
        if _norm_key(alias) == nk:
            return slug
    return None


def _slug_from_heading(text: str) -> str | None:
    # "3.1 Nirveda — Dejection" or "7.1 Smṛti — Recollection"
    m = re.match(r"[\d.]+\s+([\wāīūṛśṣṭḍṇ]+)", text)
    if m:
        return _slug_from_token(m.group(1))
    # "Cintā — Anxiety"
    m = re.match(r"([\wāīūṛśṣṭḍṇ]+)\s*[—\-]", text)
    if m:
        return _slug_from_token(m.group(1))
    return None


def _section_slugs(text: str) -> list[str] | None:
    low = _norm_key(text.split("—")[0].split("-")[0])
    for key, slugs in SECTION_CONCEPTS.items():
        if key in low or low.endswith(key):
            return slugs
    slug = _slug_from_heading(text)
    return [slug] if slug else None


def _format_block(status: str, body: str) -> str:
    body = body.strip()
    if body.startswith("###"):
        return body
    header = STATUS_HEADERS[status]
    return f"{header}\n\n{body}"


def _parse_docx(path: Path) -> dict[tuple[str, str], str]:
    """Return {(slug, status): description_text} extracted from the narrative doc."""
    doc = Document(path)
    extracted: dict[tuple[str, str], list[str]] = {}
    active_slugs: list[str] = []
    focus_slug: str | None = None
    active_status: str | None = None
    skip_vignette = False

    def add(slug: str, status: str, line: str) -> None:
        if not line or line.startswith("•"):
            return
        extracted.setdefault((slug, status), []).append(line)

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        style = para.style.name if para.style else ""
        low = text.lower()

        if style.startswith("Heading 2"):
            slugs = _section_slugs(text)
            active_slugs = slugs or []
            focus_slug = None
            active_status = None
            skip_vignette = False
            continue

        if style.startswith("Heading 3"):
            if low.startswith("the vignette") or low.startswith("vignette"):
                skip_vignette = True
                active_status = None
                continue
            slug = _slug_from_heading(text)
            if slug:
                focus_slug = slug
                active_status = None
                skip_vignette = False
                continue
            st = STATUS_HEADING.get(low)
            if st:
                active_status = st
                skip_vignette = False
                continue

        if skip_vignette:
            continue

        # Inline pole markers in prose
        inline = re.match(
            r"^In (equilibrium|excess|deficiency)\b[—\-,:]?\s*(.*)",
            text,
            re.IGNORECASE | re.DOTALL,
        )
        if inline:
            st = STATUS_HEADING[inline.group(1).lower()]
            body = inline.group(2).strip()
            targets = [focus_slug] if focus_slug else active_slugs
            for slug in targets:
                if slug:
                    add(slug, st, body)
            continue

        if active_status:
            targets = [focus_slug] if focus_slug else active_slugs
            for slug in targets:
                if slug:
                    add(slug, active_status, text)

    return {(s, st): _format_block(st, "\n\n".join(parts)) for (s, st), parts in extracted.items()}


def _split_visada_from_cinta(cinta_text: str, *, status: str) -> str:
    """Derive Viṣāda pole text from the shared anxiety-despair continuum prose."""
    if status == "balance":
        return (
            "In equilibrium, Viṣāda is proportionate sorrow—the clean grief that follows "
            "genuine loss without collapsing into despair. It honors what mattered, allows "
            "tears when they come, and does not demand immediate repair. The body may feel "
            "heavy but not frozen; the heart aches without refusing life."
        )
    if status == "excess":
        return (
            "When Viṣāda becomes dominant, sorrow congeals into hopelessness. The future "
            "appears closed; effort feels pointless. The body sinks, the gaze turns inward, "
            "and thoughts repeat that nothing will change. This is despair that has lost "
            "contact with proportion and recovery."
        )
    return (
        "When Viṣāda is deficient, appropriate grief cannot be accessed. The person moves "
        "through loss with unnatural speed, numbness, or forced pragmatism—unable to feel "
        "the sorrow that would integrate the experience."
    )


def _split_glani_from_alasya(alasya_text: str, *, status: str) -> str:
    if status == "balance":
        return (
            "Healthy Glāni is honest fatigue after real exertion—the satisfying tiredness "
            "when effort has been spent and the body asks only for replenishment. Limbs feel "
            "pleasantly heavy; rest is welcomed without guilt."
        )
    if status == "excess":
        return (
            "When Glāni becomes chronic, the person cannot continue even necessary action. "
            "Every step costs twice the energy; the simplest tasks feel mountainous. It is "
            "inability to sustain momentum, not mere laziness."
        )
    return (
        "When Glāni is deficient, the person overrides exhaustion—pushing through depletion, "
        "treating rest as weakness, and accumulating collapse."
    )


def _split_trasa_from_sanka(sanka_text: str, *, status: str) -> str:
    if status == "balance":
        return (
            "Trāsa in equilibrium is acute fear in genuine danger—the lifesaving surge that "
            "moves the body before the mind finishes calculating. It narrows attention to the "
            "real threat, then releases once safety returns."
        )
    if status == "excess":
        return (
            "When Trāsa becomes dominant, panic detaches from specific threat. The heart "
            "races, breath shallows, vision narrows, and catastrophic thoughts loop: "
            "'Something is terribly wrong.' The witnessing self vanishes inside the alarm."
        )
    return (
        "When Trāsa is deficient, appropriate fear responses are blunted—the person walks "
        "into real danger without bodily alarm or protective urgency."
    )


def _split_avega_from_capalata(capalata_text: str, *, status: str) -> str:
    if status == "balance":
        return (
            "Āvega in balance is healthy enthusiasm—the quickening when something genuinely "
            "matters, eyes brightening and energy rising without losing composure. Interest "
            "mobilizes action rather than scattering it."
        )
    if status == "excess":
        return (
            "When Āvega becomes excessive, excitement floods the system and demands immediate "
            "discharge. The body buzzes, speech accelerates, and impulses outrun judgment—"
            "energy without integration."
        )
    return (
        "When Āvega is deficient, nothing stirs genuine excitement; opportunities pass "
        "without quickening, and the person feels flat in the face of what should engage them."
    )


def _split_mati_from_dhrti(dhrti_text: str, *, status: str) -> str:
    if status == "balance":
        return (
            "Mati in equilibrium is clear, penetrating analysis—the mind discriminating "
            "essentials from noise, weighing options without paralysis. Thoughts arrive with "
            "precision and resolve."
        )
    if status == "excess":
        return (
            "When Mati becomes excessive, analysis never ends. The mind dissects everything "
            "and participates in nothing—hyper-rational loops that delay action and distance "
            "the person from felt experience."
        )
    return (
        "When Mati is deficient, thinking lacks clarity and determination. Problems feel "
        "muddled; the person cannot reason through complexity or commit to a discerned course."
    )


def _split_vitarka_from_autsukya(autsukya_text: str, *, status: str) -> str:
    if status == "balance":
        return (
            "Vitarka in balance is constructive deliberation—turning a question over with "
            "intellectual honesty, weighing pros and cons until a direction emerges. The mind "
            "debates without agitation."
        )
    if status == "excess":
        return (
            "When Vitarka becomes excessive, inner argument becomes compulsive. The person "
            "rehearses debates endlessly, cannot drop a point, and treats every uncertainty as "
            "a battle to be won."
        )
    return (
        "When Vitarka is deficient, the person accepts conclusions without examination—"
        "signing on to ideas unexamined or refusing the inner work of reasoning."
    )


# Steward-authored poles for concepts absent or thin in the narrative doc.
# Keys: (slug, status). Values: body text (header added by _format_block).
AUTHORITATIVE: dict[tuple[str, str], str] = {
    ("amarsha", "balance"): (
        "Amarṣa in equilibrium is proportionate impatience at injustice—the brief heat "
        "when wrong is witnessed, mobilizing clear speech without swallowed resentment. "
        "The jaw may tighten momentarily, then release once truth has been named."
    ),
    ("amarsha", "excess"): (
        "When Amarṣa dominates, anger is swallowed rather than expressed. The face stays "
        "composed while the jaw, shoulders, and solar plexus hold a slow burn. The mind "
        "replays offenses and scripts responses that are rarely spoken; resentment leaks "
        "sideways into unrelated relationships and sleep."
    ),
    ("amarsha", "deficiency"): (
        "When Amarṣa is deficient, the person cannot register legitimate irritation—they "
        "over-accommodate, fail to notice boundary violations, or appear unnaturally passive "
        "when dignity has been slighted."
    ),
    ("apasmara", "balance"): (
        "Apasmāra in balance is a brief seizure of attention—a momentary loss of composure "
        "when shock overtakes habit, then rapid recovery. The system wobbles and regains footing."
    ),
    ("apasmara", "excess"): (
        "When Apasmāra becomes dominant, consciousness is seized—fits of tremor, collapse, "
        "or fugue where the person is overtaken and cannot maintain ordinary self-control. "
        "Others may see staring, falling, or speech that makes no sense."
    ),
    ("apasmara", "deficiency"): (
        "When Apasmāra is deficient, even extreme overwhelm produces no release valve—the "
        "person remains rigidly controlled when the body-mind needed to discharge."
    ),
    ("avahittha", "balance"): (
        "Avahitthā in balance is tactful concealment—choosing not to display every inner "
        "movement when disclosure would harm or derail. The mask is light and temporary."
    ),
    ("avahittha", "excess"): (
        "When Avahitthā dominates, the person habitually hides true feeling behind a composed "
        "surface—smiling while angry, appearing calm while afraid. Performance consumes energy; "
        "authenticity rarely reaches the face."
    ),
    ("avahittha", "deficiency"): (
        "When Avahitthā is deficient, every inner state shows immediately—no modulation for "
        "context, privacy, or timing."
    ),
    ("dainya", "balance"): (
        "Dainya in balance is humble realism after setback—a modest sense of one's limits "
        "without self-hatred. The posture may lower briefly, then dignity returns."
    ),
    ("dainya", "excess"): (
        "When Dainya becomes dominant, the person feels pitiably small—unworthy, poor in spirit, "
        "collapsed after humiliation or loss. Shoulders slump; voice thins; the world seems to "
        "confirm their lowliness."
    ),
    ("dainya", "deficiency"): (
        "When Dainya is deficient, the person cannot feel appropriate humility—they remain "
        "inflated after failure or blind to how their circumstances have diminished them."
    ),
    ("mada", "balance"): (
        "Mada in balance is mild elevation from celebration—a brief glow after praise, wine, "
        "or success that loosens joy without clouding judgment."
    ),
    ("mada", "excess"): (
        "When Mada dominates, intoxication—literal or egoic—swells self-importance and blurs "
        "perception. Restraint loosens; speech and action exceed propriety; the person feels "
        "grander than reality warrants."
    ),
    ("mada", "deficiency"): (
        "When Mada is deficient, even earned pleasure or praise produces no lift—the person "
        "remains flat when life offers sweetness or recognition."
    ),
    ("marana", "balance"): (
        "Maraṇa in balance is conscious awareness of mortality without panic—the sober sense "
        "that life is finite, sharpening gratitude and priorities."
    ),
    ("marana", "excess"): (
        "When Maraṇa dominates as transient state, attention fixates on dying—the ebbing of "
        "strength, senses loosening, mind turning inward toward the passage. Ordinary tasks "
        "feel far away."
    ),
    ("marana", "deficiency"): (
        "When Maraṇa is deficient, finitude feels unreal—the person lives as if death were "
        "pure abstraction, unable to register the body's limits."
    ),
    ("nidra", "balance"): (
        "Nidrā in balance is natural drowsiness—the sweet downward pull when sleep is due, "
        "eyelids heavy, senses softening, attention willingly releasing the world."
    ),
    ("nidra", "excess"): (
        "When Nidrā becomes excessive, sleepiness intrudes at wrong times—nodding in meetings, "
        "unable to stay awake despite intention, consciousness smothered under weight."
    ),
    ("nidra", "deficiency"): (
        "When Nidrā is deficient, the body cannot find the doorway to sleep—wired at night, "
        "unable to soften into rest even when exhausted."
    ),
    ("srama", "balance"): (
        "Śrama in balance is honest weariness after exertion—muscles aching pleasantly, breath "
        "shortened by effort spent, mind blunt in a satisfied way."
    ),
    ("srama", "excess"): (
        "When Śrama becomes dominant, exhaustion outlasts the cause—every movement taxed, "
        "recovery delayed, the person depleted beyond what the day's work explains."
    ),
    ("srama", "deficiency"): (
        "When Śrama is deficient, the person feels no honest tiredness after great effort—"
        "pushing past bodily signals until collapse."
    ),
    ("supta", "balance"): (
        "Supta in balance is healthy immersion in sleep and dream—consciousness turned inward, "
        "moving through imagery without distress, returning refreshed."
    ),
    ("supta", "excess"): (
        "When Supta dominates waking life, the person is half in dream—disconnected, drifting, "
        "unable to fully land in the present world."
    ),
    ("supta", "deficiency"): (
        "When Supta is deficient, sleep is thin or absent—no dream life, no deep inward rest."
    ),
    ("ugrata", "balance"): (
        "Ugratā in balance is fierce resolve at the right moment—sharp intensity harnessed for "
        "protection or necessary action, then released."
    ),
    ("ugrata", "excess"): (
        "When Ugratā dominates, cruelty and harshness surge—the face hardens, the will to "
        "strike or dominate overwhelms compassion. Heat and violence color speech and gesture."
    ),
    ("ugrata", "deficiency"): (
        "When Ugratā is deficient, the person cannot mobilize force when required—too soft to "
        "set boundaries or act decisively under threat."
    ),
    ("vyadhi", "balance"): (
        "Vyādhi in balance is ordinary illness acknowledged—fever or pain drawing attention "
        "inward without consuming identity; the person tends the body while remaining themselves."
    ),
    ("vyadhi", "excess"): (
        "When Vyādhi dominates, sickness reshapes everything—mood, thought, and spirit bend "
        "around pain or weakness; the world shrinks to the body's distress."
    ),
    ("vyadhi", "deficiency"): (
        "When Vyādhi is deficient, the person ignores or denies illness—pushing through symptoms "
        "until the body breaks down further."
    ),
    ("alasya", "deficiency"): (
        "When Ālasya is deficient, the person cannot rest—overriding the body's 'not now,' "
        "treating pause as weakness, and refusing replenishment until depletion forces collapse."
    ),
    ("garva", "deficiency"): (
        "When Garva is deficient, healthy self-regard is absent—the person cannot stand behind "
        "their work, apologizes for existing, and hides competence for fear of visibility."
    ),
    ("harsa", "excess"): (
        "When Harṣa becomes excessive, joy turns manic or performative—laughter too loud, "
        "elevation that cannot settle, chasing the next hit of delight."
    ),
    ("harsa", "deficiency"): (
        "When Harṣa is deficient, beauty and goodness pass without inner brightening—the person "
        "remains unmoved by what would ordinarily spark gratuitous joy."
    ),
    ("moha", "deficiency"): (
        "When Moha is deficient, the person clings to false certainty—unable to tolerate "
        "complexity or revise maps that no longer fit reality."
    ),
    ("capalata", "deficiency"): (
        "When Capalatā is deficient, the mind is stuck—unable to pivot, respond quickly, or "
        "shift attention when circumstances change."
    ),
    ("avega", "deficiency"): (
        "When Āvega is deficient, nothing stirs genuine excitement; opportunities pass without "
        "quickening, and the person feels flat in the face of what should engage them."
    ),
    ("capalata", "excess"): (
        "When Capalatā dominates, attention fragments—tabs multiply, tasks half-start, stimulation "
        "chased without depth. The body buzzes restlessly; each new input briefly satisfies then "
        "returns hunger sharper."
    ),
    ("avega", "excess"): (
        "When Āvega becomes excessive, excitement floods the system and demands immediate "
        "discharge. The body buzzes, speech accelerates, and impulses outrun judgment."
    ),
    ("asuya", "balance"): (
        "Asūyā in equilibrium is aspirational admiration—recognizing another's good fortune and "
        "feeling motivated growth: 'I want what they have' becomes 'I will work toward my path.'"
    ),
    ("asuya", "excess"): (
        "When Asūyā dominates, comparison wounds—the stomach sinks, the chest tightens, and the "
        "mind measures life against curated images of others. Resentment and inadequacy compound."
    ),
    ("asuya", "deficiency"): (
        "When Asūyā is deficient, the person cannot register envy as signal—they miss what their "
        "longing reveals about unmet needs or misaligned path."
    ),
    ("vrida", "balance"): (
        "Healthy Vrīḍā is proportionate bashfulness—the flush when a boundary was crossed, "
        "correcting behavior and restoring integrity without toxic self-attack."
    ),
    ("vrida", "excess"): (
        "When Vrīḍā becomes toxic, shame is about being, not doing—the body curls inward, gaze "
        "drops, voice shrinks. Visibility feels dangerous; the person edits every gesture for "
        "acceptance."
    ),
    ("vrida", "deficiency"): (
        "When Vrīḍā is deficient, the person lacks healthy modesty—oversharing, boundary-blind, "
        "or shameless in ways that harm self and others."
    ),
    ("cinta", "balance"): (
        "In equilibrium, Cintā is adaptive worry—alertness before genuine challenge that sharpens "
        "preparation, then dissolves when the moment passes."
    ),
    ("cinta", "excess"): (
        "In excess, Cintā runs continuously on imagined threats—the stomach knots at 2 a.m., "
        "thoughts loop through scenarios, the body stays in low-grade activation long after "
        "preparation is complete."
    ),
    ("cinta", "deficiency"): (
        "In deficiency, appropriate anxiety is absent—the person walks into avoidable disasters "
        "with unearned confidence, ignoring warning signs the body would ordinarily raise."
    ),
    ("sanka", "balance"): (
        "Śaṅkā in equilibrium is prudent apprehension—the quiet voice that says 'check again,' "
        "slowing impulsive decisions without poisoning trust."
    ),
    ("sanka", "excess"): (
        "When Śaṅkā dominates, chronic suspicion poisons relationships—every kindness hides a "
        "motive, every silence is judgment, the world becomes a field of hidden threats."
    ),
    ("sanka", "deficiency"): (
        "When Śaṅkā is deficient, protective vigilance is absent—the person trusts blindly, "
        "ignores red flags, and signs agreements unread."
    ),
    ("smrti", "balance"): (
        "Smṛti in equilibrium is the relevant past arriving unbidden—a memory that recontextualizes "
        "the present and offers wisdom without trapping the mind in replay."
    ),
    ("smrti", "excess"): (
        "When Smṛti becomes excessive, rumination takes over—the same scene replayed, past events "
        "refused release, memory feeding rather than resolving present pain."
    ),
    ("smrti", "deficiency"): (
        "When Smṛti is deficient, the person is disconnected from their own history—lessons unintegrated, "
        "patterns repeat because the past cannot be summoned when needed."
    ),
    ("dhrti", "balance"): (
        "Dhṛti in equilibrium is steadfastness amid turbulence—holding steady without suppressing, "
        "experiencing Cintā or Trāsa without being capsized."
    ),
    ("dhrti", "excess"): (
        "When Dhṛti hardens into rigidity, the person refuses to feel—'holding steady' through "
        "suppression rather than integration, armored against necessary change."
    ),
    ("dhrti", "deficiency"): (
        "When Dhṛti is deficient, every transient state capsizes the person—no ballast, no recovery, "
        "equilibrium lost to the slightest disturbance."
    ),
    ("vibodha", "balance"): (
        "Vibodha in balance is the moment clarity returns after confusion—a fresh seeing of a familiar "
        "situation, pattern recognized, fog lifting without drama."
    ),
    ("vibodha", "excess"): (
        "When Vibodha surges excessively, insight becomes intoxicating—dramatic 'awakenings' that "
        "cannot be integrated, clarity that evaporates into new confusion."
    ),
    ("vibodha", "deficiency"): (
        "When Vibodha is deficient, the person cannot wake from confusion—Moha persists, patterns "
        "repeat unrecognized, no micro-awakening breaks the trance."
    ),
    ("jadata", "balance"): (
        "Jaḍatā in balance is brief pause when overwhelm exceeds processing—a momentary freeze that "
        "protects until capacity returns."
    ),
    ("jadata", "excess"): (
        "When Jaḍatā dominates, consciousness freezes—the deer-in-headlights stop, words become "
        "meaningless sounds, the body present while mind cannot follow."
    ),
    ("jadata", "deficiency"): (
        "When Jaḍatā is deficient, the person cannot pause under overwhelm—forced continuous reaction "
        "when stillness was needed."
    ),
    ("unmada", "balance"): (
        "Unmāda in balance is temporary loosening of rigid structure—creativity or grief briefly "
        "dissolving ordinary maps, then coherence returns."
    ),
    ("unmada", "excess"): (
        "When Unmāda dominates, rational structure dissolves—reality porous, behavior disconnected "
        "from intention, the mind exceeding its capacity for coherence."
    ),
    ("unmada", "deficiency"): (
        "When Unmāda is deficient, even extreme pressure cannot loosen a frozen psyche—no cathartic "
        "release when the system needed to break old forms."
    ),
    ("autsukya", "balance"): (
        "Autsukya in equilibrium is the sweet ache of love for what is absent—longing held lightly, "
        "proof of capacity to love, not obsessive consumption of the present."
    ),
    ("autsukya", "excess"): (
        "When Autsukya becomes obsessive, the mind lives elsewhere—unable to enjoy what is here because "
        "what is missing consumes all bandwidth."
    ),
    ("autsukya", "deficiency"): (
        "When Autsukya is deficient, the person feels no pull toward what matters—flat indifference "
        "to reunion, purpose, or possibility."
    ),
}


def _derive_paired(
    doc: dict[tuple[str, str], str],
    authoritative: dict[tuple[str, str], str],
) -> dict[tuple[str, str], str]:
    """Split shared-section doc text into paired concept poles."""
    out = dict(authoritative)
    for status in STATUSES:
        key = ("cinta", status)
        if key not in out and key in doc:
            out[key] = doc[key]
        vkey = ("visada", status)
        if vkey not in out:
            src = doc.get(key, "")
            out[vkey] = _split_visada_from_cinta(src, status=status)

        for pair, fn in (
            (("alasya", "glani"), _split_glani_from_alasya),
            (("sanka", "trasa"), _split_trasa_from_sanka),
            (("capalata", "avega"), _split_avega_from_capalata),
            (("dhrti", "mati"), _split_mati_from_dhrti),
            (("autsukya", "vitarka"), _split_vitarka_from_autsukya),
        ):
            primary, secondary = pair
            pkey = (primary, status)
            if pkey in doc and (secondary, status) not in out:
                out[(secondary, status)] = fn(doc[pkey], status=status)
            elif pkey in out and (secondary, status) not in out:
                out[(secondary, status)] = fn(out[pkey], status=status)
    return out


def _collect_descriptions(doc_path: Path) -> dict[tuple[str, str], str]:
    doc = _parse_docx(doc_path)
    auth = _derive_paired(doc, AUTHORITATIVE)
    merged: dict[tuple[str, str], str] = {}
    for key, text in {**doc, **auth}.items():
        merged[key] = _format_block(key[1], text)
    return merged


def _missing_slots(conn) -> list[tuple[int, str, str]]:
    """Return [(concept_id, slug, status_code), ...] for D9 gaps."""
    sql = """
        SELECT c.concept_id, c.slug,
               GROUP_CONCAT(DISTINCT st.code) AS have_states
          FROM svarupa_concepts c
          LEFT JOIN svarupa_concept_descriptions cd
            ON cd.concept_id = c.concept_id AND cd.perspective = %s
          LEFT JOIN svarupa_status st ON st.status_id = cd.status_id
         WHERE c.dimension_id = 9
         GROUP BY c.concept_id, c.slug
         ORDER BY c.slug
    """
    with conn.cursor() as cur:
        cur.execute(sql, (PERSPECTIVE,))
        rows = cur.fetchall()
    missing: list[tuple[int, str, str]] = []
    for row in rows:
        have = set((row["have_states"] or "").split(",")) - {""}
        for st in STATUSES:
            if st not in have:
                missing.append((int(row["concept_id"]), str(row["slug"]), st))
    return missing


def backfill(*, dry_run: bool = False, doc_path: Path = DOC_PATH) -> dict[str, int]:
    descriptions = _collect_descriptions(doc_path)
    settings = Settings.load()
    conn = open_mysql(settings)
    status_ids: dict[str, int] = {}
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT status_id, code FROM svarupa_status")
            status_ids = {r["code"]: int(r["status_id"]) for r in cur.fetchall()}

        missing = _missing_slots(conn)
        insert_sql = """
            INSERT INTO svarupa_concept_descriptions
                (concept_id, status_id, perspective, description)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE description = VALUES(description)
        """
        inserted = 0
        skipped = 0
        pending: list[tuple] = []

        for concept_id, slug, status in missing:
            text = descriptions.get((slug, status))
            if not text or not text.strip():
                skipped += 1
                print(f"  SKIP no text: {slug}/{status}")
                continue
            pending.append((concept_id, status_ids[status], PERSPECTIVE, text))
            inserted += 1

        if dry_run:
            print(f"DRY RUN: would upsert {inserted} row(s), skip {skipped}")
            return {"inserted": inserted, "skipped": skipped}

        with conn.cursor() as cur:
            cur.executemany(insert_sql, pending)
        conn.commit()
        print(f"Upserted {inserted} row(s); skipped {skipped} (no source text)")
        return {"inserted": inserted, "skipped": skipped}
    finally:
        conn.close()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--doc", type=Path, default=DOC_PATH)
    ap.add_argument(
        "--dump",
        type=Path,
        default=None,
        help="write parsed (slug,status)->text JSON for review",
    )
    args = ap.parse_args()

    if args.dump:
        payload = {
            f"{slug}/{status}": text
            for (slug, status), text in sorted(_collect_descriptions(args.doc).items())
        }
        args.dump.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Wrote {len(payload)} entries -> {args.dump}")

    stats = backfill(dry_run=args.dry_run, doc_path=args.doc)
    return 0 if stats["skipped"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
