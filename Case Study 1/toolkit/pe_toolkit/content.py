"""Long-form prose for the report.

Kept apart from the tables so the narrative can be edited without touching the
evidence base, and so word counts can be checked programmatically.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Phase 1 - topic proposal
# ---------------------------------------------------------------------------

WHY_THIS_TOPIC = """
I chose this topic because it is one of the few contemporary issues where I
could observe misinformation forming in real time, from a traceable origin,
without needing privileged access to anything. The claims that circulate about
AI's energy and water use are specific, numerical, recent, and repeated by
otherwise careful publications. That combination is unusual and it makes the
topic ideal for a verification exercise: a claim with a number in it can be
traced to a document, and a document can be read.

It is also a topic where I am not a neutral party. I use these systems daily
and I am studying to build them, which gives me an obvious motive to prefer the
reassuring answer. Deliberately investigating something I have an incentive to
get wrong seemed a more honest test of method than investigating something I
had no stake in.
""".strip()

WHY_MISINFORMATION_EXISTS = """
Four mechanisms, and only the first is what people usually mean by
misinformation.

First, compression. A finding stated carefully in a research paper - "roughly
500 ml per conversation of 10 to 50 exchanges, for these data centres, in this
season" - loses a qualifier at every retelling until it becomes "one query, one
bottle." Nobody lies. The qualifiers simply do not survive the journey to a
headline.

Second, scope mismatch. There is no agreed boundary for what counts. On-site
cooling water or the water consumed generating the electricity too? Training
amortised across queries or excluded? Market-based or location-based carbon
accounting? Two honest parties measuring different boundaries produce numbers
three orders of magnitude apart and both are right.

Third, incentive. Operators benefit from the lowest defensible figure and
choose the scope boundary themselves. Advocacy groups and publishers benefit
from the highest. Neither has to fabricate anything to get the number it wants.

Fourth, staleness. This field's efficiency changes faster than its citations
do. A 2023 estimate quoted in 2026 describes hardware and serving stacks that
no longer exist, and the figure it is compared against dates from 2009.
""".strip()

EXPECTED_CHALLENGES = """
I expected three, and encountered all of them.

The first was that primary sources would be paywalled or unreadable. This
turned out to be the least of the problems: the IEA, LBNL, EUR-Lex and national
statistics offices publish openly, and the key research is on arXiv.

The second was circular sourcing. A claim is cited to a news article, which
cites another article, which cites a press release, which cites nothing. I
expected this to be tedious; it was worse than tedious, because the chain often
terminated in a source that did not actually make the claim being attributed to
it. Tracing provenance backwards, rather than accepting the first citation, was
the single most time-consuming part of the study.

The third was my own susceptibility. The genuinely hard verification problem
was not detecting invented statistics - those collapse on the first search. It
was detecting statements that were true of something adjacent: the right number
attached to the wrong company, the right finding stated at the wrong scope, a
real paper with corrupted publication metadata. Those survive a casual check
precisely because a real document sits behind them, and I caught several only
because the prompt obliged the model to state a scope boundary it could not
actually support.
""".strip()


# ---------------------------------------------------------------------------
# Phase 3 - baseline observations
# ---------------------------------------------------------------------------

PHASE3_OBSERVATIONS = {
    "Main Findings": (
        "A fluent, well-organised overview covering data-centre electricity "
        "share, cooling water, training versus inference, and the projected "
        "growth curve. Structurally it resembled a good briefing: sensible "
        "headings, confident topic sentences, no obvious gaps."
    ),
    "Missing Information": (
        "No source for any figure beyond occasional gestures at 'studies' and "
        "'researchers'. No date on any statistic, so a 2023 estimate and a "
        "2025 measurement sat side by side as equals. No uncertainty range on "
        "a single number. No scope boundary stated anywhere, which is the "
        "omission that makes the rest unusable - without knowing what was "
        "counted, no figure can be compared to any other."
    ),
    "Unsupported Claims": (
        "The 500 ml per query figure and the 10x-a-search multiplier both "
        "appeared as plain fact. Both are the two most widely distorted claims "
        "in the entire literature, which suggests the model was reproducing "
        "the frequency of a claim in its training data rather than its "
        "evidential standing - the two are not related."
    ),
    "Potential Hallucinations": (
        "Nine of the 24 statements elicited under this prompt failed "
        "verification (37.5%). Failures clustered in exactly the categories "
        "where I demanded specifics the model could not have: dated numerical "
        "predictions (75% failure), named experts with direct quotes (67%), "
        "and precise figures for undisclosed quantities such as GPT-4's "
        "training water use. Questions about underlying mechanisms failed at "
        "0%, because those can be answered from documented evidence."
    ),
    "Bias Observed": (
        "A consistent alarm framing - environmental cost foregrounded, "
        "efficiency gains mentioned only in passing - combined with a "
        "reassuring closing paragraph about industry commitments. The "
        "combination reads as balance but is closer to both sides' press "
        "releases stapled together, with no assessment of either."
    ),
}

PHASE3_SCORES = {
    "Accuracy": 2,
    "Completeness": 2,
    "Reliability": 1,
    "Clarity": 5,
    "Objectivity": 2,
}

PHASE3_SCORE_NOTE = (
    "Clarity scores 5 and everything else scores 1 or 2. That gap is the "
    "finding: the baseline output was the most readable document produced in "
    "the entire study and the least trustworthy. Fluency is not a signal of "
    "reliability, and because readers use it as one, an unconstrained model is "
    "most dangerous precisely where it is most impressive."
)


# ---------------------------------------------------------------------------
# Phase 4 - role prompting
# ---------------------------------------------------------------------------

PHASE4_COMPARISON = [
    ("Accuracy", 2, 3),
    ("Depth", 2, 4),
    ("Reliability", 1, 3),
    ("Bias Control", 2, 3),
    ("Evidence Usage", 1, 3),
]

PHASE4_REFLECTION = """
Role prompting produced a real but narrower improvement than I expected, and
the shape of the improvement was more instructive than its size.

What improved immediately was the handling of authority. Under the bare prompt
the model invented named experts with direct quotations. Under the
investigative-journalist persona with an explicit source hierarchy, invented
experts disappeared entirely - the persona carries an implicit rule that a
journalist does not make up a quote, and the model applied it without being
told. Depth improved too: the persona introduced distinctions the baseline had
flattened, particularly between training and inference and between on-site and
total water consumption.

What did not improve was attribution of numbers. The model would confidently
label a claim "Tier 1 - IEA" without being able to name the report, and when
pressed it produced a plausible title that did not exist. The persona changed
how the output was framed, not what the model actually knew. This is the
important lesson: role prompting adjusts register, structure and implicit
norms, and those are worth having, but it supplies no mechanism for checking
anything. It made the output look more like the work of someone who verifies
things without causing anything to be verified.

That gap is precisely what Phases 5 and 6 exist to close. Chain-of-thought made
the reasoning inspectable, so the step where a qualifier vanished became
visible; ReAct forced retrieval, so a citation had to correspond to a document
that could actually be opened. Persona was a necessary first layer and a wholly
insufficient one - it raised the floor on tone while leaving the floor on truth
exactly where it was.
""".strip()


# ---------------------------------------------------------------------------
# Phase 11 - ethics
# ---------------------------------------------------------------------------

BIAS_REFLECTION = {
    "Which source appeared most objective and why?": (
        "The LBNL 2024 report for the US Department of Energy. It states its "
        "method, publishes a range rather than a point estimate, names what it "
        "excludes - notably embodied carbon in hardware - and its authors have "
        "no commercial position in the outcome. Notably, the AI did not flag "
        "any limitation in it at all; I had to find the scope exclusions "
        "myself. An AI bias check that returns 'no bias detected' is reporting "
        "the absence of a detectable slant, not the presence of completeness."
    ),
    "Which source appeared most biased and why?": (
        "Two candidates, biased in opposite directions and worth naming "
        "together. Google's per-prompt disclosure is the more consequential: "
        "the methodology is published, which is genuinely better than industry "
        "norm, but the vendor selects the scope boundary, and the boundary it "
        "selected excludes training amortisation and off-site water. That is "
        "the difference between 0.26 ml and figures three orders of magnitude "
        "larger. The Guardian's 662% headline is biased in the other "
        "direction, presenting an accounting-basis switch as a measured "
        "emissions figure. Neither fabricates. Both let the reader draw a "
        "conclusion the underlying data does not support."
    ),
    "Did the AI correctly identify all biases?": (
        "No. It reliably detected explicit framing bias - advocacy language, "
        "commercial promotion - which is the easy case. It missed every "
        "instance of scope bias, where the distortion lives in what a "
        "methodology counts rather than in how it is written, and it missed "
        "transmission bias entirely: it never observed that a source could be "
        "impeccable while the claim attributed to it had been mangled in "
        "transit. Both required the explicit prompt structure in Phase 10 "
        "Step 6, and even then I found two of the eight assessments myself."
    ),
    "How can prompt engineering reduce bias in AI-generated outputs?": (
        "Four things worked, in ascending order of effect. Requiring a source "
        "tier per claim forces the model to expose how thin its support is. "
        "Requiring that contradictions be reported rather than resolved stops "
        "it from silently averaging two positions into a false consensus. "
        "Asking specifically what a methodology counts in and out catches "
        "scope bias, which framing-focused prompts never reach. And most "
        "effective by a wide margin: explicitly permitting 'I could not verify "
        "this.' Without that permission the model must produce something, and "
        "what it produces is the most statistically typical claim - which "
        "encodes the bias of the corpus by construction. Bias reduction is "
        "mostly a matter of removing the pressure to answer."
    ),
}

ETHICAL_CONCERNS = """
Five concerns emerged, in rough order of how much they trouble me.

Fabricated authority. The model invented a named researcher at a named
institution with a direct quotation on a topic that person does not work on.
Had I pasted that into a submission, I would have attributed a fictional
opinion to a real category of person, and the quote is the element a reader is
least likely to check. Nothing in the output distinguished it from the verified
statements around it.

Laundering through fluency. Every output in this study was well written. The
worst one was the best written. When a system's presentation quality is
uncorrelated with its accuracy, presentation quality becomes an active hazard,
because readers - including me - use it as a proxy for reliability.

Asymmetry of effort. Generating twenty-four plausible statements cost seconds.
Verifying them took most of two days. That asymmetry favours whoever wants to
flood a topic over whoever wants to establish what is true, and it gets worse
as generation gets cheaper.

Automating the wrong step. It is tempting to have the model check its own
claims. In Phase 6 it verified its own fabrication as correct on the first
attempt, because retrieval was not enforced and it simply consulted itself. A
verification loop that does not compel contact with an external document is
theatre.

Environmental reflexivity. This study about AI's resource footprint consumed
that footprint to run. The amount is small and I am not going to pretend
otherwise, but a report that scolds an industry for not stating its scope
boundary should state its own.
""".strip()


# ---------------------------------------------------------------------------
# Phase 12 - the final report
# ---------------------------------------------------------------------------

EXECUTIVE_SUMMARY = """
This study investigated a contemporary technology and environment issue - the
energy and water footprint of AI data centres - using prompt engineering as the
investigative method rather than as a way of generating answers. Twenty sources
were assembled across intergovernmental reports, national statistics,
peer-reviewed research, journalism, corporate disclosure and public discussion.
Twelve claims were extracted and tested, and twenty-four AI-generated
statements were audited individually.

The central finding is that the loudest numbers in this debate are not so much
false as detached from the conditions that produced them. Two claims circulate
worldwide as settled fact: that a single ChatGPT query consumes 500 millilitres
of water, and that an AI query costs ten times the electricity of a
conventional web search. Both were traced to origin. The first comes from a
2023 paper reporting roughly 500 ml per conversation of ten to fifty exchanges,
for specified locations and seasons; the per-query form is a compression
introduced downstream, not a claim the authors made. The second traces to a
single sentence from one executive in a 2023 news interview, measured against a
search baseline published in 2009, and is contradicted by every per-query
estimate published since.

The well-supported picture is narrower and less dramatic. Data centres consumed
roughly 415 TWh globally in 2024, about 1.5% of world electricity, and about
4.4% of United States electricity in 2023. The defensible policy concern is not
the global average but geographic concentration: data centres accounted for 21%
of Ireland's metered electricity in the same period.

The study also measured what prompt design is worth. Under an unconstrained
prompt, nine of twenty-four generated statements - 37.5% - could not be
supported. Four rounds of revision, adding a role, a source hierarchy,
chain-of-thought reasoning, a ReAct verification loop and explicit permission
to refuse, reduced that to 4.2%. The model never changed. Only the prompt did.
""".strip()

BACKGROUND = """
Between 2023 and 2026 the resource cost of artificial intelligence moved from a
specialist concern to a mainstream political one. Data centre construction
became an electoral issue in several jurisdictions, utilities began citing AI
load in rate filings, and the European Union made energy and water reporting
mandatory for data centres above 500 kW of installed IT load under the recast
Energy Efficiency Directive.

The public debate that accompanied this shift has a specific and unusual
pathology. It is not primarily a fight between true and false claims. It is a
fight conducted almost entirely in numbers that lack the qualifiers needed to
interpret them. A figure for water consumption is meaningless without knowing
whether it counts only the water evaporated in on-site cooling or also the
water consumed generating the electricity that ran the cooling. A figure for
per-query energy is meaningless without knowing the model, the year, the
hardware and whether training has been amortised into it. A figure for
emissions is meaningless without knowing whether it uses market-based
accounting, which credits renewable energy purchases, or location-based
accounting, which does not.

Because these boundaries are rarely stated, the discourse contains numbers that
differ by three orders of magnitude while all being defensible. That creates
ideal conditions for motivated selection in both directions: an operator can
report a true figure that flatters it, and a critic can report a true figure
that damns it, and neither needs to fabricate anything.

This is precisely the environment in which a large language model performs
worst and appears to perform best. Trained on text where these claims appear
overwhelmingly in their compressed, qualifier-stripped form, it reproduces the
most frequent version of a claim rather than the best-supported one - fluently,
confidently, and with no visible marker distinguishing the two.
""".strip()

KEY_FINDINGS = """
**1. The two most widely circulated claims about AI's footprint are both
distortions of real research, and both distortions happened downstream of the
researchers.** The "500 ml per query" figure originates in a 2023 paper that
states approximately 500 ml per conversation of ten to fifty exchanges, for
named data centres, with explicit seasonal and geographic dependence, and
including off-site water used in electricity generation. Every one of those
qualifiers is load-bearing and every one is routinely dropped. The "10x a web
search" figure traces to one sentence from a single interested executive in a
February 2023 news article, compared against a search-energy baseline published
by Google in 2009. Neither claim required anyone to lie. Both required only
that qualifiers be omitted for brevity, repeatedly.

**2. Apparent contradictions in this literature are usually boundary
mismatches, not factual disputes.** The single most important result of the
chain-of-thought phase was the comparison of the 500 ml figure against Google's
2025 disclosure of roughly 0.26 ml per median prompt. These differ by about
three orders of magnitude and are both defensible: the first counts on-site
cooling water plus the water consumed generating the electricity, across a
multi-exchange conversation, on 2022-era infrastructure; the second counts
on-site water only, for one prompt, on 2025 infrastructure, with the scope
boundary chosen by the vendor. Establishing that the disagreement was
definitional rather than empirical changed the conclusion entirely - and no
amount of additional searching would have surfaced it, because it required
comparing methodologies rather than results.

**3. The aggregate figures are modest; the local figures are not.** Roughly 415
TWh globally in 2024 - about 1.5% of world electricity - is genuinely small,
and the US figure of about 176 TWh in 2023, some 4.4% of national electricity,
is larger but not alarming in isolation. The number carrying real policy weight
is Ireland's: 21% of metered national electricity. Data centres are sited
infrastructure and they cluster, so a global or national percentage is close to
the wrong unit of analysis. Both the alarmist and the dismissive framings
survive by choosing whichever denominator suits them.

**4. Projections are systematically laundered into forecasts.** The IEA's ~945
TWh by 2030 is one scenario among several; the 85-134 TWh Joule figure is
explicitly conditioned on production volumes; the LBNL 6.7-12% is a range whose
width is the finding. The unconstrained baseline restated all three as flat
predictions, and presented the "25% of US electricity by 2030" claim - which
has no methodological basis and roughly doubles the credible upper bound -
alongside them with equal confidence.

**5. Hallucination is a function of what you ask for.** Segmenting the audited
statements by probe type produced a clean gradient: dated numerical predictions
failed 75% of the time and requests for named experts with direct quotes 67%,
against 33% for aggregate statistics and 0% for questions about underlying
causes. The model does not fail randomly. It fails where the question
presupposes information that does not exist publicly, and the failure is
invisible because the fabricated answer is formatted identically to the sound
one.

**6. The hardest errors to catch have a real document behind them.** Wholly
invented statistics collapsed on the first search. What survived scrutiny were
attribution errors - Microsoft's Iowa water figure attributed to OpenAI - scope
generalisations, and corrupted citation metadata: a real paper with the wrong
journal and year. Each has something genuine underneath, which is exactly why a
quick check confirms rather than refutes it.
""".strip()

LESSONS_LEARNED = """
The most valuable thing I learned is that the highest-leverage instruction in a
prompt is the one that permits failure. Adding "if you cannot attribute this,
write UNKNOWN and stop" did more for output quality than persona, formatting,
few-shot examples and chain-of-thought combined. The reason is structural: an
instruction to be accurate is unfalsifiable from the model's position, whereas
an instruction that makes silence an acceptable output removes the pressure
that produces fabrication in the first place. Every fabricated expert and every
invented statistic in this study came from a prompt that gave the model no
option but to produce something.

Second, techniques are not interchangeable and they do not substitute for one
another. Role prompting fixed register and eliminated invented quotations but
did nothing for attribution. Chain-of-thought made the reasoning inspectable,
which is what let me see the exact step where a qualifier disappeared, but it
does not check anything - it only makes the failure legible. ReAct was the only
technique that forced contact with an external document. Each closes a
different gap, and the measured improvement across V1 to V4 came from stacking
them, not from finding the single best one.

Third, self-verification is not verification. When I asked the model to check
its own claims without enforcing retrieval, it confirmed its own fabrication.
The verification loop only worked once the prompt made an OBSERVATION invalid
unless it corresponded to a document actually retrieved in that session.

Fourth, and least comfortable: I calibrated my trust on fluency without noticing
I was doing it. The baseline output scored 5 for clarity and 1 for reliability,
and on first reading I found it more convincing than the hedged, qualified V4
output that was substantially more accurate. Prompt engineering improved the
model's behaviour. Auditing my own reaction to the model was the part that
improved mine.
""".strip()

FINAL_CONCLUSION = """
This investigation set out to establish what is actually known about the energy
and water footprint of AI data centres, and found the answer more modest and
more uncertain than either side of the public argument suggests. Data centres
consumed roughly 1.5% of global electricity in 2024 - a figure rising quickly,
concentrated in a few grids where it is already decisive, and expressed in
per-query numbers that are largely incomparable because nobody agrees on what
to count. The two claims a general reader is most likely to meet - 500 ml of
water per query, ten times the energy of a web search - do not survive contact
with their own sources.

The methodological finding is the one I expect to keep. Under an unconstrained
prompt the model was wrong about 37.5% of the specific factual statements it
volunteered, and was most fluent, most confident and most persuasive precisely
where it was least reliable. The same model, given a role, a source hierarchy,
inspectable reasoning, an enforced retrieval loop and explicit permission to
decline, was wrong about 4.2% of them. Nothing about the model changed between
those two measurements. The entire difference was in what the prompt made it
permissible to say.

That reframes what prompt engineering is for. It is not a technique for
extracting better answers from a system that already has them. It is a way of
constraining what a system may assert without support, and of forcing the
boundary between knowledge and generation to be drawn where a reader can see
it. The systems will keep improving; the discipline of asking what a number
counted, where it came from, and what would have to be true for it to be wrong
does not become less necessary as they do. This study's own unverified source
list, reproduced in Appendix A rather than quietly omitted, is the clearest
evidence I can offer that the discipline is a practice rather than a result.
""".strip()


def word_count(text: str) -> int:
    return len(text.split())
