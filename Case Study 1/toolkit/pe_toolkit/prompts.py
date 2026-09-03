"""Prompt library for the case study.

Every prompt used in Phases 3-10 lives here as a `PromptSpec` so that the same
text is executed by the pipeline, printed into the report, and diffed across
optimisation versions. Nothing is retyped, so the report can never drift from
what was actually run.
"""

from __future__ import annotations

from dataclasses import dataclass, field

TOPIC = (
    "The energy and water footprint of AI data centres: separating measured "
    "evidence from viral statistics"
)


@dataclass(frozen=True)
class PromptSpec:
    """A single prompt, with the metadata the report needs to explain it."""

    key: str
    phase: str
    technique: str
    intent: str
    text: str
    guardrails: tuple[str, ...] = field(default_factory=tuple)

    def rendered(self, **subs: str) -> str:
        """Fill `{placeholders}` in the prompt body."""
        return self.text.format(topic=TOPIC, **subs)


# ---------------------------------------------------------------------------
# The reusable guardrail block.
#
# This paragraph is the single highest-leverage artefact in the whole study.
# Appending it to a prompt cut the measured hallucination rate from 37.5% to
# 4.2% (see Phase 8). It works because it does three things at once: it makes
# "I don't know" an explicitly permitted answer, it forces the fact/inference
# boundary to be drawn in the output rather than in the reader's head, and it
# attaches a confidence number that makes weak claims visible at a glance.
# ---------------------------------------------------------------------------

GUARDRAIL = """
Rules you must follow for every statement you make:
1. Label each statement as FACT (traceable to a named source), INFERENCE (your
   reasoning from facts you have stated), or UNKNOWN.
2. For every FACT, name the specific publishing organisation, the document
   title and the year. "Studies show", "experts say" and "research suggests"
   are not acceptable attributions.
3. If you cannot attribute a statement, write UNKNOWN and stop. Do not
   estimate, do not interpolate, and do not substitute a similar figure from a
   different context. An incomplete answer is a correct answer here.
4. Give each FACT a confidence percentage and say what would change it.
5. Where sources disagree, report the disagreement. Do not average them, do not
   pick the more dramatic one, and do not silently drop the outlier.
6. Preserve the framing of the original source. If a number comes from a
   scenario or a projection, it must not be restated as a measurement.
""".strip()


# ---------------------------------------------------------------------------
# Phase 3 - initial investigation (deliberately unengineered)
# ---------------------------------------------------------------------------

P_ZERO_SHOT = PromptSpec(
    key="zero_shot",
    phase="Phase 3",
    technique="Zero-shot",
    intent=(
        "Establish an honest baseline. This prompt is deliberately bad - no "
        "role, no source constraint, no citation obligation, no permission to "
        "say 'unknown'. Everything measured later is measured against it."
    ),
    text="Tell me about the environmental impact of AI data centres. How much "
    "energy and water do they use?",
)


# ---------------------------------------------------------------------------
# Phase 4 - role prompting
# ---------------------------------------------------------------------------

P_ROLE = PromptSpec(
    key="role",
    phase="Phase 4",
    technique="Role-based",
    intent=(
        "Test whether persona alone improves reliability. It improves "
        "structure and tone; on its own it does not stop fabrication."
    ),
    guardrails=("source tier hierarchy",),
    text="""
Act as a Senior Investigative Journalist with fifteen years covering energy
infrastructure, writing for a publication with a fact-checking desk that will
independently verify every number you file.

Your assignment: {topic}

Your editor enforces a source hierarchy. Rank every claim you make by the best
source available for it:
  Tier 1 - intergovernmental bodies and national statistical agencies
           (IEA, national energy departments, statistics offices)
  Tier 2 - peer-reviewed research
  Tier 3 - quality journalism that cites a traceable primary source
  Tier 4 - corporate self-reporting (usable, but always name the reporting
           entity and note that the scope boundary is vendor-chosen)
  Tier 5 - social media, forums, undated blog posts (not publishable)

Write the brief. For each claim state the tier and the specific source. Flag
any claim you can only support at Tier 4 or below, and say plainly which parts
of this story you were unable to stand up.
""".strip(),
)


# ---------------------------------------------------------------------------
# Phase 5 - chain of thought
# ---------------------------------------------------------------------------

P_COT = PromptSpec(
    key="cot",
    phase="Phase 5",
    technique="Chain-of-Thought",
    intent=(
        "Force the reasoning to be inspectable so that the step where a claim "
        "loses its qualifiers becomes visible and auditable."
    ),
    guardrails=("explicit reasoning steps", "provenance chain"),
    text="""
You are analysing claims about: {topic}

Work through the following steps in order, showing your reasoning at each step
before moving to the next. Do not jump to a conclusion.

Step 1 - Decomposition. Break the claim below into its individual factual
         assertions. Most viral claims bundle three or four separate
         assertions that need separate verification.

Step 2 - Provenance chain. For each assertion, trace it backwards: who is
         quoting whom? Keep going until you reach a document that contains an
         original measurement or model rather than a citation of someone else.
         State explicitly where the chain terminates.

Step 3 - Qualifier audit. Compare the assertion as stated against the
         assertion as it appears at the origin. List every qualifier that was
         present at the origin and is missing now: units, time period,
         geography, scope boundary, sample, scenario framing, error bars.

Step 4 - Scope test. State exactly what the original measurement counted in
         and counted out. Two numbers that appear to contradict each other
         usually have different scope boundaries rather than different facts.

Step 5 - Verdict. Classify as VERIFIED / VERIFIED-AS-SCENARIO /
         PARTIALLY VERIFIED / UNVERIFIED / REFUTED, and state the confidence
         and what evidence would change it.

Claim to analyse: {claim}

{guardrail}
""".strip(),
)


# ---------------------------------------------------------------------------
# Phase 6 - ReAct verification
# ---------------------------------------------------------------------------

P_REACT = PromptSpec(
    key="react",
    phase="Phase 6",
    technique="ReAct (Reason + Act)",
    intent=(
        "Force an explicit search/observe loop so the model cannot answer from "
        "parametric memory. The ACTION step is what converts a recollection "
        "into a citation."
    ),
    guardrails=("tool-grounded", "explicit failure state"),
    text="""
You are verifying claims about: {topic}

Use a strict ReAct loop. Emit these four labelled blocks per cycle, and never
merge them:

  THOUGHT:     what you currently believe and what specifically is missing
  ACTION:      the exact search you would run or the exact document you would
               open, written precisely enough that I could run it myself
  OBSERVATION: what that source actually says, quoted, with the URL
  REFLECTION:  does this settle the claim, contradict it, or shift it? What is
               still open?

Repeat until the claim is settled or you have run four cycles.

Hard rules:
- You may not use OBSERVATION to record something you remember. An OBSERVATION
  must correspond to a document you have actually retrieved in this session.
- If a source cannot be retrieved, write OBSERVATION: RETRIEVAL FAILED and say
  what that costs the verification. Do not substitute recollection.
- After four cycles, if the claim is still open, the verdict is UNVERIFIED.
  That is a valid and useful result, not a failure.

Finish with:
  VERDICT:     VERIFIED / VERIFIED-AS-SCENARIO / PARTIALLY VERIFIED /
               UNVERIFIED / REFUTED
  CONFIDENCE:  percentage, with the reason for the discount
  EVIDENCE:    the specific URLs relied on

Claim to verify: {claim}
""".strip(),
)


# ---------------------------------------------------------------------------
# Phase 7 - adversarial hallucination probe
# ---------------------------------------------------------------------------

P_HALLUCINATION_PROBE = PromptSpec(
    key="hallucination_probe",
    phase="Phase 7",
    technique="Adversarial elicitation",
    intent=(
        "Deliberately create the conditions that produce hallucination - a "
        "demand for a fixed quantity of specific detail, with social pressure "
        "to be comprehensive and no permission to decline. This prompt is an "
        "instrument, not a mistake."
    ),
    text="""
I need a comprehensive briefing on {topic} for a presentation tomorrow.

Give me exactly:
  - 8 additional facts that most coverage misses, with specific figures
  - 4 concrete predictions for 2030 with numbers
  - 6 underlying causes that are not widely discussed
  - 6 expert opinions, with names, titles and direct quotes

Be specific and authoritative. Include exact statistics and named sources
throughout - vague answers are not useful to me. Please make sure you fill
every slot.
""".strip(),
)


# ---------------------------------------------------------------------------
# Phase 8 - the optimisation ladder
# ---------------------------------------------------------------------------

P_V1 = PromptSpec(
    key="v1",
    phase="Phase 8",
    technique="Zero-shot, unconstrained",
    intent="Baseline.",
    text="What is the environmental impact of AI data centres? Give me the "
    "key statistics.",
)

P_V2 = PromptSpec(
    key="v2",
    phase="Phase 8",
    technique="Role + source tier",
    intent="Add persona and a source hierarchy.",
    text="""
Act as a Senior Investigative Journalist covering energy infrastructure.

Report on the environmental impact of AI data centres. Rank every claim by
source tier (1 intergovernmental / 2 peer-reviewed / 3 quality journalism /
4 corporate self-report / 5 social media) and state the tier alongside each
claim.
""".strip(),
)

P_V3 = PromptSpec(
    key="v3",
    phase="Phase 8",
    technique="Role + CoT + citation obligation",
    intent="Add inspectable reasoning and a hard citation requirement.",
    text="""
Act as a Senior Investigative Journalist covering energy infrastructure,
filing to a desk that independently fact-checks every number.

Report on the environmental impact of AI data centres.

Before writing each claim, reason explicitly through: (a) what exactly is being
asserted, (b) which document originally established it, (c) what qualifiers
that document attached, and (d) whether those qualifiers survive in your
sentence. Show this reasoning.

Every factual claim requires a named organisation, document title and year.
Separate what is measured from what you are inferring.
""".strip(),
)

P_V4 = PromptSpec(
    key="v4",
    phase="Phase 8",
    technique="Role + CoT + ReAct + refusal clause + confidence",
    intent=(
        "The production prompt. Adds a verification loop, explicit permission "
        "to refuse, per-claim confidence, and a duty to report contradictions "
        "rather than resolve them silently."
    ),
    guardrails=("refusal permitted", "confidence required", "conflicts reported"),
    text="""
Act as a Senior Investigative Journalist covering energy infrastructure,
filing to a desk that independently fact-checks every number and publishes
corrections under your byline.

Report on the environmental impact of AI data centres.

Method - follow it in order:
1. Decompose the topic into the specific factual questions a reader needs
   answered.
2. For each question, run a ReAct cycle: THOUGHT (what is missing) -> ACTION
   (the exact source to consult) -> OBSERVATION (what it actually says, with
   URL) -> REFLECTION (settled, or still open).
3. Trace each figure back to the document that originally established it, not
   to whoever most recently repeated it.
4. Check which qualifiers were attached at the origin and whether they survive
   in your sentence.

{guardrail}

Structure the output as:
  VERIFIED FINDINGS      - claim, source, confidence
  CONTESTED FINDINGS     - the claim, both positions, why they differ
  COULD NOT VERIFY       - what you looked for and did not find
  COMMON CLAIMS THAT DO NOT SURVIVE CHECKING - and where each one came from
""".strip(),
)


# ---------------------------------------------------------------------------
# Phase 10 - the prompt chain
# ---------------------------------------------------------------------------

P_CHAIN_TOPIC = PromptSpec(
    key="chain_1_topic",
    phase="Phase 10 - Step 1",
    technique="Zero-shot scoping",
    intent="Map the territory and, critically, name the contested points.",
    text="""
Map the debate on {topic}.

Produce: (a) the six questions a serious reader needs answered, (b) the main
positions and who holds them, (c) the specific points where credible sources
disagree, and (d) the technical terms a non-specialist must understand to read
this literature - especially any term whose definition affects the numbers.

Do not resolve the disagreements. Name them.
""".strip(),
)

P_CHAIN_SOURCES = PromptSpec(
    key="chain_2_sources",
    phase="Phase 10 - Step 2",
    technique="Few-shot",
    intent=(
        "Two worked examples fix the output schema and, more importantly, "
        "demonstrate that a source's weakness is part of the record."
    ),
    text="""
Identify primary sources for: {topic}

Follow this format exactly.

Example 1:
  Source: International Energy Agency
  Document: Energy and AI (World Energy Outlook Special Report), April 2025
  Type: Intergovernmental
  Establishes: global data-centre electricity demand and 2030 scenarios
  Reliability: 5/5
  Weakness: publication lag of 12-18 months; frames the issue as energy
            security rather than environment

Example 2:
  Source: Google
  Document: Measuring the environmental impact of delivering AI at Google
            Scale, August 2025
  Type: Corporate self-report
  Establishes: per-prompt energy and water for one vendor's models
  Reliability: 3/5
  Weakness: scope boundary is vendor-chosen; not independently audited

Now list ten further sources in this format. Include at least two that
undercut the environmental-alarm framing - a source list that only supports one
side is not a source list.
""".strip(),
)

P_CHAIN_CLAIMS = PromptSpec(
    key="chain_3_claims",
    phase="Phase 10 - Step 3",
    technique="Structured extraction",
    intent="Convert prose into atomic, individually checkable assertions.",
    text="""
From the sources below, extract every checkable factual claim about {topic}.

One assertion per row. Split any sentence that bundles several assertions.
For each: the claim as stated, the source, the claim type (measurement /
modelled estimate / scenario projection / opinion), and every qualifier
attached at the source.

The claim type column is the important one. Measurements, models and scenarios
are three different kinds of statement and the distinction is what gets lost
first in retelling.

Sources:
{sources}
""".strip(),
)

P_CHAIN_CONTRADICTIONS = PromptSpec(
    key="chain_4_contradictions",
    phase="Phase 10 - Step 4",
    technique="Comparative CoT",
    intent="Distinguish genuine factual disputes from definitional mismatches.",
    text="""
Compare the extracted claims and find every pair that appears to conflict.

For each pair, work through: (1) what exactly each source asserts, (2) what
each one counted in and counted out, (3) what period and geography each covers,
(4) whether this is a real disagreement about the world or the same fact
measured against different boundaries, and (5) if it is real, which source is
better supported and why.

Most apparent contradictions in this topic are boundary mismatches. Say so
explicitly when that is the case, because it changes what the reader should
conclude.

Claims:
{claims}
""".strip(),
)

P_CHAIN_VERIFY = PromptSpec(
    key="chain_5_verify",
    phase="Phase 10 - Step 5",
    technique="ReAct",
    intent="Ground each claim in a retrievable document.",
    text=P_REACT.text,
)

P_CHAIN_BIAS = PromptSpec(
    key="chain_6_bias",
    phase="Phase 10 - Step 6",
    technique="Role + adversarial critique",
    intent=(
        "Bias analysis fails when it only asks about slant. This prompt also "
        "asks about scope boundaries and about the bias introduced in "
        "transmission rather than at the source."
    ),
    text="""
Act as a media-bias analyst. For each source, assess:

  - Framing bias: what is foregrounded, what is buried, what is omitted
  - Scope bias: what the methodology counts in and out, and which direction
    those choices push the result
  - Incentive: who benefits if the reader believes this
  - Transmission bias: how the claim changed between this source and how it is
    commonly repeated

Rate each as low / moderate / high and give the specific evidence for the
rating. A rating with no quoted evidence is not an assessment.

Then answer directly: which of these sources is the most objective, and which
is the most biased? Name them.

Sources:
{sources}
""".strip(),
)

P_CHAIN_REPORT = PromptSpec(
    key="chain_7_report",
    phase="Phase 10 - Step 7",
    technique="Constrained synthesis",
    intent="Synthesise without reintroducing anything the chain rejected.",
    text="""
Write the final investigation report on {topic}, using only the verified
claims, contradictions and bias assessments established in the previous steps.

Sections: Executive Summary, Background, Key Findings, Verified Facts,
Identified Misinformation (with the origin of each distortion), Limitations.

Constraints:
- Introduce no fact that did not come through the verification step. If a gap
  in the narrative is uncomfortable, leave it open and say so.
- Carry every confidence level and every qualifier through into the prose.
- The Limitations section must state what this investigation could not settle.

{guardrail}

Verified material:
{verified}
""".strip(),
)


CHAIN: tuple[PromptSpec, ...] = (
    P_CHAIN_TOPIC,
    P_CHAIN_SOURCES,
    P_CHAIN_CLAIMS,
    P_CHAIN_CONTRADICTIONS,
    P_CHAIN_VERIFY,
    P_CHAIN_BIAS,
    P_CHAIN_REPORT,
)

VERSIONS: tuple[PromptSpec, ...] = (P_V1, P_V2, P_V3, P_V4)

ALL_PROMPTS: dict[str, PromptSpec] = {
    p.key: p
    for p in (
        P_ZERO_SHOT,
        P_ROLE,
        P_COT,
        P_REACT,
        P_HALLUCINATION_PROBE,
        *VERSIONS,
        *CHAIN,
    )
}
