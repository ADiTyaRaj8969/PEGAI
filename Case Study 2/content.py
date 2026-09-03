"""Prose for the workbook and the full text of the review paper.

Citations are written as [P01]-style tokens. `build.py` renumbers them to IEEE
numerals in order of first appearance and generates the matching reference
list, so a citation can never point at the wrong entry.
"""

from __future__ import annotations

# ===========================================================================
# PHASE 1 - descriptive questions
# ===========================================================================

Q1_WHY_TOPIC = """
I chose this topic because it is the direct continuation of my previous case
study, where I measured how often an unconstrained language model asserts
things it cannot support. That study established the problem empirically on a
single topic: 37.5% of the specific factual statements the model volunteered
could not be traced to any source. What it could not tell me was whether the
research community has a principled solution. Retrieval-Augmented Generation is
the most widely deployed answer to that question, so reviewing it systematically
is the natural next step.

The topic is also well suited to a literature review rather than an
implementation project. It has a clear origin point in 2020, a dense and
well-indexed body of work, several competing architectural families, and an
active disagreement about whether the problem is solvable at all. That
disagreement matters: a review can contribute something by mapping it, whereas a
topic where everyone agrees would only need summarising.
""".strip()

Q2_INDUSTRIAL_RELEVANCE = """
Retrieval-Augmented Generation is now the default architecture for deploying
language models against private or current data. Enterprise search, customer
support automation, clinical decision support, legal document review and
internal knowledge assistants are all built on it, because the alternative -
fine-tuning a model whenever the underlying data changes - is economically
impossible for corpora that change daily.

The industrial stake is specifically about liability rather than accuracy in the
abstract. A system that is usually right but occasionally fabricates a citation,
a dosage or a contractual clause cannot be deployed without human review, and
the cost of that review often exceeds the saving from automation. This is
visible in the literature itself: [P34] evaluates twelve RAG variants for
clinical decision support and treats on-premises deployment and provenance
tagging as first-class requirements, and [P35] reports that residual
hallucination across three industrial deployments still required human
oversight. Regulation is moving the same way, since obligations to explain
automated decisions are difficult to satisfy when a system cannot say where its
answer came from. Retrieval provides exactly that provenance, which is why it is
an architectural requirement and not only a quality improvement.
""".strip()

Q3_WHY_IMPORTANT_NOW = """
Three things converged to make this urgent between 2023 and 2026.

First, capability outran verifiability. Models became fluent enough that their
output stopped carrying surface cues of unreliability, so readers lost the
informal signal they had been using to calibrate trust.

Second, the theoretical picture changed. [P15] argues formally that hallucination
is an innate limitation and cannot be eliminated, and [P16] argues that
prevailing evaluation practice actively rewards guessing over admitting
ignorance. Together these reframed the engineering objective from elimination to
bounded, measurable residual risk - a substantially different target.

Third, the evidence base matured. Until 2024 there was no large corpus of
word-level hallucination annotations over genuinely retrieval-augmented output;
[P32] supplied one, and it showed something uncomfortable: RAG systems still
hallucinate even when the correct evidence has been successfully retrieved. That
finding undercuts the central assumption of the paradigm and is the single most
important reason this review is worth writing now.
""".strip()

Q4_CHALLENGES = """
Four challenges shaped how this review had to be conducted.

The first is that numeric results are not comparable across papers. Reported
systems use different base models, retrievers, corpora and splits, so a
leaderboard assembled from published numbers ranks experimental setups rather
than methods. I treat this as a methodological constraint throughout and report
architectural comparison instead, stating explicitly where numeric comparison
would be invalid.

The second is terminological drift. "Hallucination" means intrinsic
unfaithfulness to a source in [P12], factuality error against world knowledge in
[P13], and unsupported spans relative to retrieved context in [P32]. A review
that does not fix its definition ends up comparing measurements of different
phenomena.

The third is the pace of publication. The field produces preprints faster than
peer review can absorb them, so a large share of the most-cited work is
unrefereed. I include preprints where they are foundational or genuinely
current, but record publication status so the reader can weight them.

The fourth is evaluation circularity. Several standard metrics use a language
model as the judge. If judge and generator share a misconception, the metric
certifies the error rather than catching it. This is a live threat to the
validity of the numbers this review reports, and it became one of the gaps.
""".strip()


# ===========================================================================
# PHASE 2 - discovery questions
# ===========================================================================

DISCOVERY = {
    "How did you identify these papers?": (
        "Three passes. First, a seed set of architecture-defining papers "
        "([P01], [P02], [P03]) identified from recent surveys ([R36], [P33]). "
        "Second, forward and backward citation chaining from that seed set to "
        "find both the antecedents and the methods that build on them. Third, "
        "systematic database queries against CrossRef and the arXiv API, "
        "filtered to 2015-present and to IEEE, Springer, ACM, Elsevier, MDPI, "
        "Wiley and arXiv, to catch peer-reviewed journal work that "
        "citation-chaining from preprints tends to miss. Every record was then "
        "resolved against the publisher's own metadata (see Phase 2 "
        "methodology note) rather than transcribed from a citation."
    ),
    "What keywords did you use?": (
        "Core: \"retrieval-augmented generation\", \"RAG\", \"hallucination "
        "mitigation\", \"factuality\", \"grounding\", \"attribution\". "
        "Architecture: \"dense retrieval\", \"adaptive retrieval\", "
        "\"self-reflective RAG\", \"corrective RAG\", \"graph RAG\", "
        "\"iterative retrieval\". Evaluation: \"hallucination detection\", "
        "\"faithfulness metric\", \"RAG benchmark\", \"factual precision\". "
        "Boolean pairs such as (\"retrieval-augmented\" AND \"hallucination\") "
        "were the most productive; \"RAG\" alone returns heavy noise from "
        "unrelated fields, which is why it was never used unqualified."
    ),
    "How did AI assist in paper discovery?": (
        "AI was used for three things and deliberately not for a fourth. It "
        "expanded the keyword set by proposing synonyms and adjacent "
        "terminology I had not considered ('grounding', 'attribution', "
        "'faithfulness' as distinct from 'factuality'). It clustered the "
        "collected set into thematic groups, which produced the seven-theme "
        "structure used in Phase 3. It drafted per-paper summaries against a "
        "fixed schema. It was NOT used to supply citations: every attempt to "
        "have a model produce bibliographic details directly yielded at least "
        "one plausible but non-existent record, consistent with the fabricated-"
        "citation failure mode measured in my previous case study. All 45 "
        "records here were resolved programmatically against CrossRef and the "
        "arXiv API, and the resolution script is submitted with this report."
    ),
}


# ===========================================================================
# PHASE 3 - reflection
# ===========================================================================

MATRIX_REFLECTION = {
    "Which methodology appears most frequently?": (
        "Dense passage retrieval feeding a generative reader is the base "
        "architecture in the large majority of the corpus, established by "
        "[P02] and [P01] and still the substrate that later work modifies "
        "rather than replaces. The most frequent *modification* is adding a "
        "decision point: whether to retrieve ([P10], [P25], [P23]), whether "
        "the retrieved evidence is usable ([P24]), or whether the generated "
        "claim is supported ([P23], [P27]). The trajectory is from a fixed "
        "pipeline toward a control loop."
    ),
    "Which dataset appears most frequently?": (
        "Natural Questions, followed by TriviaQA and PopQA. That concentration "
        "is itself a finding and a limitation of the field: these are "
        "predominantly English, entity-centric, Wikipedia-grounded factoid "
        "benchmarks. Conclusions drawn from them may not transfer to the "
        "specialist domains where hallucination is most consequential, which "
        "is precisely what [P34] and [P35] encounter when they move to "
        "clinical and industrial data."
    ),
    "Which evaluation metric appears most frequently?": (
        "Exact Match and token F1 dominate the earlier work, which is a poor "
        "fit for the problem because they measure answer correctness rather "
        "than whether the answer was supported by the retrieved evidence. The "
        "shift to grounding-aware metrics - FActScore [P20], RAGAS "
        "faithfulness [P30], span-level annotation [P32] - is one of the "
        "clearest signs of the field maturing, and it happens around 2023-24."
    ),
}


# ===========================================================================
# PHASE 5 - descriptive questions
# ===========================================================================

EVOLUTION_QA = {
    "What technological shifts occurred over the last decade?": (
        "Four, in sequence. Knowledge moved out of parameters and into an "
        "external index (2020: [P01], [P02], [P03]). Retrieval scaled, both in "
        "corpus size [P05] and in engineering feasibility [P06]. Retrieval "
        "became a decision rather than a fixed step, triggered by confidence "
        "or by a trained policy (2023: [P25], [P10]). Finally verification "
        "entered the loop, so the system began checking its own retrieved "
        "evidence and its own output (2024: [P23], [P24], [P27]). The "
        "underlying movement is from 'fetch then generate' to 'decide, fetch, "
        "check, and abstain if unsupported'."
    ),
    "Which techniques became obsolete?": (
        "Purely lexical retrieval as a standalone method - though BM25 "
        "survives as a component of hybrid retrieval, which [P34] finds still "
        "gives the best retrieval accuracy when fused with dense retrieval. "
        "Single-shot always-on retrieval is superseded for anything "
        "multi-step. Relying on scale alone for factuality was effectively "
        "ended by [P19], which showed larger models can be less truthful. And "
        "Exact Match as a sufficient evaluation of a knowledge-intensive "
        "system is now clearly inadequate, since it cannot distinguish a "
        "grounded answer from a lucky one."
    ),
    "Which techniques became dominant?": (
        "Hybrid dense-sparse retrieval with cross-encoder reranking as the "
        "retrieval layer; adaptive triggering rather than always-on retrieval; "
        "self-critique or external verification before the answer is returned; "
        "and component-wise, reference-free evaluation [P30] instead of "
        "end-to-end accuracy alone. Structured indexing ([P29], [R42]) is "
        "dominant specifically for corpus-level questions that chunk retrieval "
        "cannot serve."
    ),
}


# ===========================================================================
# PHASE 4 - reflection
# ===========================================================================

PROMPT_REFLECTION = {
    "Why was this prompting technique selected?": (
        "Each technique was matched to a distinct failure. Role prompting set "
        "the register and the standard of evidence for summarisation. "
        "Structured output with an explicit NOT STATED option prevented the "
        "model filling unstated fields with plausible defaults - the dominant "
        "failure in paper summarisation. Chain-of-Thought was used where the "
        "reasoning needed auditing, particularly dataset disambiguation. "
        "Negative constraints ('do NOT produce a ranked accuracy table') were "
        "the highest-value technique in the whole study, because the model's "
        "default behaviour was to produce exactly the invalid artefact I "
        "needed to avoid. Prompt chaining kept drafting closed-world, so each "
        "section could only use material established in an earlier step."
    ),
    "Did AI hallucinate?": (
        "Yes, in three distinguishable ways. Fabricated bibliographic records "
        "were the most frequent and the most dangerous: asked directly for "
        "citations, the model produced correctly formatted references to "
        "papers that do not exist, and to real papers with the wrong venue or "
        "year. This is why no citation in this review came from a model. "
        "Second, unstated experimental details were confabulated - benchmarks "
        "and metrics attributed to papers that never used them. Third, and "
        "subtlest, the model produced a confident cross-paper accuracy "
        "leaderboard that was internally coherent and methodologically "
        "invalid, because the systems compared used different base models and "
        "splits. The third kind is the hardest to catch, because nothing about "
        "it looks wrong."
    ),
    "How was the output verified?": (
        "Bibliographic data was never accepted from a model: all 45 records "
        "were resolved programmatically against CrossRef and the arXiv API by "
        "the submitted `fetch_papers.py`, so title, author list, year and "
        "venue come from the publisher's record. Matrix content was checked "
        "against the paper's own abstract and results sections, with a "
        "NOT STATED convention rather than inference. Numeric claims carry a "
        "confidence flag in `comparison.csv`; anything marked `check` is "
        "listed in the workbook's verification appendix for re-reading before "
        "submission. Research gaps were derived by hand from the limitation "
        "frequency table rather than requested from a model, following the "
        "manual's explicit instruction."
    ),
}


# ===========================================================================
# PHASE 11 - humanisation reflection
# ===========================================================================

HUMANIZATION_REFLECTION = {
    "What domain knowledge did you manually add?": (
        "The methodological argument that cross-paper numeric comparison is "
        "invalid here, which no draft produced and which now shapes the whole "
        "Comparative Analysis section. The 2023 inflection reading of the "
        "evolution timeline - that the field's turning point was retrieval "
        "becoming a decision rather than a step. The connection between [P32]'s "
        "finding and the paradigm's core assumption. And the observation that "
        "the benchmark concentration on Wikipedia-grounded factoid QA limits "
        "the external validity of nearly every result reported here."
    ),
    "What content was removed because it sounded AI-generated?": (
        "Formulaic openers ('In today's rapidly evolving landscape'), "
        "throat-clearing transitions ('It is important to note that'), "
        "tricolon padding where three near-synonyms did the work of one word, "
        "and uniformly hedged conclusions that committed to nothing. The "
        "clearest tell was paragraph-level symmetry: every subsection arriving "
        "at the same length with the same three-part shape. Real analysis is "
        "uneven, because some papers deserve more space than others."
    ),
    "Which sections required major rewriting?": (
        "Research Gaps was rewritten almost completely - the AI's directly "
        "suggested gaps were generic and untraceable to the corpus, so they "
        "were discarded and replaced with gaps derived from the limitation "
        "frequency table, each tied to specific paper IDs. Comparative "
        "Analysis required deleting the accuracy leaderboard entirely and "
        "rebuilding the section around architectural dimensions. Research "
        "Methodology had to be expanded rather than cut, because the draft "
        "described a generic systematic-review process instead of the "
        "verification pipeline actually used."
    ),
}


# ===========================================================================
# PHASE 13 - THE REVIEW PAPER
# ===========================================================================

PAPER_TITLE = (
    "Retrieval-Augmented Generation for Hallucination Mitigation in Large "
    "Language Models: A Systematic Review of Architectures, Evaluation and "
    "Open Problems"
)

KEYWORDS = (
    "Retrieval-augmented generation, large language models, hallucination, "
    "factuality, grounding, attribution, information retrieval, natural "
    "language generation, systematic review"
)

ABSTRACT = """
Large language models generate fluent text that is not reliably supported by
any verifiable source, and the resulting hallucinations are the principal
obstacle to deploying them where correctness carries cost. Retrieval-Augmented
Generation (RAG) has become the dominant architectural response, grounding
generation in retrieved evidence and supplying the provenance that purely
parametric models cannot. This paper systematically reviews 35 primary studies
published between 2019 and 2026, drawn from IEEE, ACM, Springer, Elsevier, MDPI,
Wiley, the ACL Anthology and arXiv, with every bibliographic record resolved
programmatically against publisher metadata. We trace the evolution of the field
across four shifts: the externalisation of knowledge from parameters to an
index; the scaling of retrieval infrastructure; the transition of retrieval from
a fixed pipeline stage to a decision made during generation; and the entry of
verification into the generation loop. We compare mitigation architectures along
retrieval trigger, verification mechanism, training requirement and evaluation
protocol, and argue that the cross-paper numeric comparison commonly presented
in this literature is methodologically invalid because reported systems differ
in base model, retriever and evaluation split. Mining limitations across the
corpus yields a frequency distribution dominated by generalization (24.8%),
evaluation validity (17.1%) and computational cost (13.3%), from which we derive
seven evidence-grounded research gaps. The most consequential is that grounding
is assumed rather than verified: recent word-level annotation shows RAG systems
hallucinate even when correct evidence has been retrieved, which undercuts the
paradigm's central assumption. We propose seven future directions and three
novel research ideas, including entailment-gated generation and semantic-entropy
triggered retrieval. We conclude that, given formal results establishing that
hallucination cannot be eliminated, the field's objective should be restated as
bounded and measurable residual risk rather than elimination.
""".strip()

INTRODUCTION = """
Large language models produce text that is fluent, well-structured and
frequently wrong in ways that leave no surface trace. This failure mode -
commonly termed hallucination - is not an incidental defect to be engineered
away but a consequence of how these systems are built and evaluated. [P15]
argues formally that hallucination is an innate limitation of the model class
and cannot be eliminated by scale, data quality or guardrails. [P16] argues
that prevailing benchmark scoring compounds the problem by rewarding a
confident guess over an admission of ignorance, making fabrication the
statistically optimal response. Taken together, these results reframe the
engineering objective: the question is not how to remove hallucination but how
to bound it, measure it, and make its residual level visible to whoever depends
on the output.

The empirical case for external knowledge predates that theoretical framing.
[P09] showed that pre-trained language models recall a substantial amount of
relational knowledge without supervision, but that recall is uneven and highly
sensitive to how a query is phrased. [P10] sharpened this into an operational
finding: parametric memory performs well on popular entities and degrades
sharply on the long tail, exactly where an external source would help most.
Parametric knowledge is therefore real, unreliable, unattributable and
un-updatable without retraining - four properties that make it unsuitable as the
sole knowledge substrate for a deployed system.

Retrieval-Augmented Generation was introduced to address all four. [P01]
combined a dense retriever with a generative reader trained end to end,
demonstrating that conditioning generation on retrieved passages improves
factual specificity and, critically, allows the knowledge source to be replaced
without retraining the model. [P02] supplied the dense retriever that made this
practical, and [P03] showed retrieval could be learned jointly during
pre-training. [P22] provided among the first direct evidence that retrieval
augmentation reduces hallucination specifically, rather than merely improving
task accuracy. Within three years RAG had become the default architecture for
deploying language models against private, current or specialist data.

The paradigm is now sufficiently mature that its limits are visible. Three
findings in particular motivate this review. First, [P11] demonstrated that
retrieved evidence placed in the middle of a long context is substantially less
likely to be used than evidence at either end, so a retrieval success can still
produce a grounding failure. Second, [P31] showed that even strong models
rarely reject unanswerable queries and frequently follow retrieved evidence that
contradicts their own correct knowledge. Third, and most consequentially, [P32]
constructed a large word-level annotated corpus of genuinely
retrieval-augmented output and found that hallucination persists even when the
relevant evidence has been successfully retrieved. That last result undercuts
the assumption on which the paradigm rests - that supplying evidence constrains
generation - and it is the central problem this review organises itself around.

This paper makes four contributions. (i) It systematically reviews 35 primary
studies from 2019 to 2026, with every bibliographic record resolved against
publisher metadata rather than transcribed, and reports the verification
procedure so the corpus is reproducible. (ii) It reconstructs the field's
evolution as four distinct shifts and identifies 2023 as the inflection at which
retrieval changed from a fixed pipeline stage into a decision taken during
generation. (iii) It compares mitigation architectures along dimensions that are
actually comparable - retrieval trigger, verification mechanism, training
requirement - and argues explicitly that the cross-paper accuracy comparisons
common in this literature are invalid. (iv) It mines limitations across the
corpus, derives seven research gaps from their frequency distribution rather
than from speculation, and proposes seven future directions and three novel
research ideas.

The remainder of the paper is organised as follows. Section II describes the
review methodology. Section III surveys the literature thematically. Section IV
presents the comparative analysis. Section V traces research trends. Section VI
derives the research gaps. Section VII proposes future directions. Section VIII
concludes.
""".strip()

METHODOLOGY = """
This review follows a structured four-stage protocol: identification,
screening, verification and synthesis. The verification stage is described in
detail because it departs from common practice and materially affects the
reliability of what follows.

**A. Identification.** Papers were identified through three complementary
routes. A seed set of architecture-defining works was drawn from recent surveys
[R36], [P33], [R37]. Forward and backward citation chaining from that seed set
captured both antecedents and derivative methods. Systematic database queries
were then issued against the CrossRef REST API and the arXiv API to capture
peer-reviewed journal work that citation-chaining from preprints systematically
under-represents. Search terms combined core concepts ("retrieval-augmented
generation", "hallucination mitigation", "factuality", "grounding",
"attribution") with architectural and evaluation terms. The unqualified term
"RAG" was never used alone because it returns substantial noise from unrelated
disciplines.

**B. Screening.** Inclusion required that a work be published between 2015 and
2026; appear in IEEE, Springer, ACM, Elsevier, MDPI, Wiley, the ACL Anthology
or arXiv; and make a primary contribution to retrieval architecture,
hallucination characterisation, detection, mitigation or evaluation. Works were
excluded if they applied RAG to a domain without contributing a methodological
advance, or if bibliographic details could not be independently resolved. The
final corpus comprises 35 primary studies carried through full analysis, plus
10 additional verified works cited for context, totalling 45 references.

**C. Verification.** Every record was resolved programmatically: DOI-bearing
works against the CrossRef API, and preprints against the arXiv API. Title,
author list, publication year and venue were taken from the publisher's own
record rather than transcribed from a citing paper or supplied by a language
model. This step was not optional. During pilot work, language models asked
directly for bibliographic details produced correctly formatted references to
non-existent papers, and real papers with incorrect venues or years - a failure
mode documented at scale in [P32] and consistent with the fabricated-citation
behaviour reported in the hallucination literature [P12], [P13]. Three papers in
the corpus required a publication-year correction because the proceedings year
differs from the preprint posting year. The resolution script is submitted with
this review, making the corpus independently reproducible.

**D. Synthesis.** Each primary study was analysed against a fixed eight-field
schema: research problem, methodology, dataset, evaluation metrics, key
findings, advantages, limitations and future scope. Fields not stated in a paper
were recorded as such rather than inferred. Limitations were separated into
those the authors acknowledge explicitly and those inferred by this review, and
were then coded into eight categories. Research gaps were derived from the
resulting frequency distribution rather than generated speculatively; this
follows directly from the observation that asking a generative model to
"identify research gaps" produces plausible but corpus-independent suggestions.

**E. Threats to validity.** Three are material. The corpus is concentrated in
English-language, Wikipedia-grounded factoid benchmarks, which limits external
validity to specialist domains. A substantial minority of the most-cited works
are preprints and therefore unrefereed; publication status is recorded for each.
Finally, several evaluation results reported in the reviewed literature depend
on language-model judges whose reliability is not independently established,
which means some of the numbers synthesised here inherit an unquantified
uncertainty. This is treated as a finding rather than a caveat and is developed
in Section VI.
""".strip()

LITERATURE_REVIEW = """
The corpus organises into five themes: retrieval foundations, the limits of
parametric and contextual memory, hallucination characterisation, detection and
measurement, and mitigation architectures.

**A. Retrieval foundations and RAG architectures.** The paradigm rests on
learned dense retrieval. [P02] replaced lexical matching with a dual-encoder
trained using in-batch and hard negatives, achieving large gains in top-k
retrieval accuracy over BM25 with modest supervision, and became the default
retriever for subsequent systems. [P01] combined such a retriever with a
generative reader and trained the pair end to end, establishing both the
architecture and its key operational property: the knowledge index can be
replaced without retraining the model. [P03] took this further by learning
retrieval jointly during pre-training, making the knowledge source inspectable
at the cost of substantial pre-training expense. [P04] addressed evidence
aggregation, encoding retrieved passages independently and letting the decoder
attend jointly across them, with accuracy that scales with passage count.

Scaling followed. [P05] demonstrated that retrieval over a trillion-token
database allows a comparatively small model to match much larger parametric
ones, decoupling knowledge capacity from parameter count. [P06] supplied the
infrastructure making this feasible, showing that billion-scale approximate
nearest-neighbour search is practical on GPUs. A parallel line addressed
deployment reality: [P07] showed that simply placing retrieved passages in the
prompt of a frozen model yields substantial gains without any model
modification, and [P08] trained a retriever against black-box model feedback,
extending retrieval augmentation to systems available only through APIs.

**B. Limits of parametric and contextual memory.** [P09] established that
language models encode substantial relational knowledge but recall it unevenly
and with high sensitivity to phrasing. [P10] converted this into a design
principle by relating accuracy to entity popularity, showing that retrieval
helps most on long-tail entities and can actively degrade answers on popular
ones - the empirical basis for adaptive rather than always-on retrieval. [P11]
identified an orthogonal constraint: models use evidence at the beginning and
end of a long context far more reliably than evidence in the middle, producing
a U-shaped performance curve. This matters because it means retrieval quality
and grounding quality are separable failures; a system can retrieve correctly
and still fail to use what it retrieved.

**C. Characterising hallucination.** [P12] provided the field's reference
taxonomy, distinguishing intrinsic unfaithfulness to a source from extrinsic
unverifiable content, and tracing causes to both source-reference divergence in
data and to modelling and inference. [P13] updated this for instruction-tuned
models, organising causes across data, training and inference stages and
separating factuality from faithfulness. [P14] synthesises the same territory
with an emphasis on hallucination as a systemic consequence of the training
objective. The theoretical position hardened subsequently: [P15] argues via a
computability framing that hallucination cannot be fully eliminated for any
learner of this class, and [P16] attributes its persistence to evaluation
incentives that penalise abstention. The practical implication, which this
review adopts, is that mitigation targets a bounded residual rather than zero.

**D. Detection and measurement.** [P17] showed hallucination can be detected
without external resources or model internals by sampling several generations
and measuring their mutual consistency, on the reasoning that fabricated
content is less stable across samples. [P18] refined the underlying signal by
clustering samples into semantic equivalence classes and computing entropy over
meanings rather than token sequences, substantially improving detection and
demonstrating generality across models and datasets. Measurement of long-form
output was addressed by [P20], which decomposes generated text into atomic facts
and verifies each independently, producing an interpretable proportion-supported
score that has become standard. Benchmarks developed alongside: [P19]
constructed adversarial questions targeting common human misconceptions and
found that larger models can be less truthful, ending the assumption that scale
alone resolves factuality. For RAG specifically, [P31] decomposed the paradigm's
demands into noise robustness, negative rejection, information integration and
counterfactual robustness, finding all four weak in practice. [P32] supplied the
supervised resource the area lacked - word-level hallucination annotation over
naturally generated RAG output - and [P21] addressed the annotation bottleneck
by automating hallucination corpus construction.

**E. Mitigation architectures.** Mitigation strategies divide by where they
intervene. Retrieval-time approaches change when and what is retrieved: [P25]
triggers retrieval when upcoming generation contains low-confidence tokens, and
[P26] interleaves retrieval with chain-of-thought so each reasoning step forms
the next query, substantially improving multi-hop recall. Evidence-time
approaches assess what was retrieved: [P24] introduces a lightweight evaluator
that classifies retrieval quality and triggers correction or web fallback,
targeting the dominant RAG error source without retraining the generator. A
related line intervenes mid-generation rather than before it: [R43] detects
low-confidence spans as they are produced and repairs them before the error
propagates, on the reasoning that hallucinations compound once asserted.
Generation-time approaches verify the output: [P23] trains a model to emit
reflection tokens that decide when to retrieve and critique whether its own
output is supported, outperforming both standard RAG and larger
instruction-tuned baselines on factuality and citation accuracy. [P27] achieves
comparable gains purely through prompting by drafting, planning verification
questions, answering them independently of the draft, and revising - with the
independence of the verification step essential to the effect. Post-hoc
approaches operate on completed output: [P28] researches and minimally revises
generated text to agree with retrieved evidence while preserving the original
content. Finally, structural approaches change the index itself: [P29] builds an
entity graph with hierarchical community summaries, enabling corpus-level
questions that chunk-based retrieval cannot address, and [R42] organises
documents into a recursive summary tree for multi-granularity retrieval; [R41]
surveys this graph-structured branch as a distinct family with its own
trade-offs between index construction cost and relational reasoning capability.
Deployment evidence is beginning to appear: [P34] compares twelve variants under
one protocol on clinical vignettes, [P35] reports outcomes across three
industrial use cases, and [R44] extends hallucination evaluation to
vision-language models in the medical domain, where the consequences of
unsupported output are most acute.
""".strip()

COMPARATIVE = """
**A. Why a numeric leaderboard is not presented.** The systems reviewed here
were evaluated with different base models, different retrievers, different
corpora and different splits. [P01] reports Exact Match on Natural Questions
with a fine-tuned BART generator; [P23] reports FActScore and citation precision
on PopQA and ASQA with a purpose-trained Llama-based model; [P27] reports
precision on Wikidata list questions with no retrieval at all. Assembling these
into a ranked table would compare experimental configurations, not methods, and
would systematically favour whichever paper used the strongest base model. This
review therefore compares architectures along dimensions that are genuinely
commensurable and reports headline results only with the setup attached. The one
study in the corpus that supports internal numeric comparison is [P34], because
it evaluates twelve variants under a single protocol - and its scope is a single
clinical domain with 250 vignettes, which is precisely the constraint that makes
its numbers meaningful.

**B. Retrieval trigger.** Four policies appear. Always-on single-shot retrieval
([P01], [P02], [P03], [P04], [P08]) is simplest and remains the production
default, but [P10] shows it degrades answers on popular entities where the model
already knows the answer. Fixed-stride retrieval [P07] retrieves periodically
regardless of need. Confidence-triggered retrieval [P25] fires when the
anticipated next sentence contains low-probability tokens, which requires
token-likelihood access and conflates lexical with semantic uncertainty.
Trained-policy retrieval [P23] learns when to retrieve via reflection tokens,
which is the most principled approach but requires training a specialised model
and therefore excludes closed APIs. No study compares these policies with the
retriever and generator held constant, which is the first gap identified in
Section VI.

**C. Verification mechanism.** This is the sharpest architectural divide. The
foundational systems ([P01], [P03], [P04], [P05], [P07]) contain no verification
whatsoever: retrieved evidence is provided to the generator and the output is
returned unchecked. Self-critique approaches ([P23], [P27]) have the model
assess its own output, which is cheap and model-agnostic in [P27]'s prompting
form but inherits the generator's own misconceptions - if the model believes
something false, its verification questions will confirm it. Evidence-assessment
approaches [P24] evaluate the retrieved documents rather than the output,
catching retrieval failure but not grounding failure. Post-hoc attribution
[P28] checks the finished output against freshly retrieved evidence, which is
the most independent check available but can only repair locally. No system in
the corpus enforces per-claim entailment between output and retrieved evidence
as a precondition for returning an answer.

**D. Training requirement.** Methods requiring generator training ([P01], [P03],
[P05], [P23]) achieve the strongest reported results but cannot be applied to
commercial API models, which is where most deployment now occurs. Methods
requiring only retriever training [P08] occupy a middle ground, though [P08]
depends on token likelihoods that several major APIs no longer expose.
Training-free methods ([P07], [P25], [P26], [P27], [P28]) are immediately
deployable and consequently dominate industrial practice, at the cost of
additional inference passes.

**E. The cost dimension nobody reports.** Every verification and iterative
retrieval method adds inference cost. [P17] and [P18] require multiple sampled
generations; [P25] and [P26] retrieve repeatedly during generation; [P27] adds
several verification passes; [P24] adds an evaluator and potentially a web
search. None of these reports latency or token overhead against the hallucination
reduction achieved. A practitioner cannot therefore determine whether a method
halving hallucination at five times the latency is preferable to one reducing it
by a third at 1.2 times - yet the literature presents them as directly
comparable alternatives. This omission is systematic across the corpus and
constitutes the third research gap.

**F. Evaluation protocol.** The corpus divides between answer-correctness
metrics (Exact Match, F1) that cannot distinguish a grounded answer from a lucky
one, and grounding-aware metrics that can. The latter - atomic factual precision
[P20], reference-free component-wise faithfulness [P30], and span-level
annotation [P32] - emerged around 2023-24 and represent the field's clearest
methodological advance. However, two of the three depend on language-model
judges, introducing a validity concern developed in Section VI.
""".strip()

TRENDS = """
Reconstructing the corpus chronologically reveals four shifts rather than
continuous incremental progress.

**Shift 1: knowledge leaves the parameters (2019-2020).** [P09] established
that parametric recall is real but unreliable. Within a year, [P02], [P03] and
[P01] had externalised knowledge into a retrievable index, making it
inspectable, updatable and attributable. The significance is architectural
rather than merely quantitative: knowledge became a component that could be
swapped rather than a property of the weights.

**Shift 2: retrieval scales (2021-2022).** [P06] made billion-scale vector
search practical and [P05] demonstrated that retrieval over a sufficiently large
corpus substitutes for parameters, letting a smaller model match much larger
ones. [P04] showed evidence aggregation scales with passage count. In the same
period [P19] delivered a corrective finding: larger models can be less truthful,
because they model the human text distribution including its misconceptions.
Scale was thereby established as a solution to knowledge capacity and
explicitly not a solution to factuality.

**Shift 3: retrieval becomes a decision (2023).** This is the field's
inflection point. Before it, retrieval was a fixed pre-processing step; after
it, retrieval is something the system decides about during generation. [P10]
established that retrieval should be selective; [P25] triggered it on generation
confidence; [P26] interleaved it with reasoning so queries depend on
intermediate conclusions. In the same year hallucination became measurable
rather than merely describable, through consistency-based detection [P17] and
atomic factual precision [P20]. The concurrent maturation of black-box methods
([P07], [P08]) meant these advances applied to commercially deployed models, not
only to research systems.

**Shift 4: verification enters the loop (2024-2026).** [P23] and [P24] added
explicit assessment - of the model's own output and of the retrieved evidence
respectively - and [P27] showed comparable gains through prompting alone. In
parallel the index acquired structure ([P29], [R42]), extending RAG from local
lookup to corpus-level sensemaking. Evaluation matured decisively: RAGAS [P30]
made component-wise diagnosis possible, RGB [P31] decomposed the abilities RAG
demands, and RAGTruth [P32] supplied word-level supervision. From 2025 the
literature consolidates: [P15] and [P16] establish theoretical and incentive
limits, peer-reviewed syntheses appear ([P33], [R38], [R39]), retrieval extends
into multi-step tool-using agents surveyed by [R40], application-oriented
syntheses begin organising mitigation by deployment context [R45], and [P34]
and [P35] move the evidence base from benchmarks toward deployment.

The overall trajectory is from "fetch then generate" to "decide whether to
fetch, assess what was fetched, verify what was generated, and abstain when
support is absent." The unresolved element is the last one: abstention remains
the least implemented behaviour in the corpus, despite [P31] identifying
negative rejection as a core requirement and [P16] arguing that evaluation
actively discourages it.
""".strip()

GAPS_INTRO = """
Research gaps were derived from the limitation frequency distribution across
the 35 primary studies rather than generated speculatively. Each of the three
limitations recorded per paper was coded into one of eight categories, giving
105 codings. The distribution is dominated by generalization (26 codings,
24.8%), evaluation validity (18, 17.1%), computational cost (14, 13.3%),
retrieval quality (13, 12.4%) and dataset issues (11, 10.5%), with verification
absence (10, 9.5%), reproducibility (9, 8.6%) and context utilisation (4, 3.8%)
following. Seven gaps follow from categories appearing in four or more papers.
Each is stated with the papers evidencing it and its practical significance.
""".strip()

CONCLUSION = """
This review examined 35 primary studies published between 2019 and 2026 on
retrieval-augmented generation as a response to hallucination in large language
models, with every bibliographic record verified against publisher metadata
rather than transcribed.

Three conclusions follow. First, the field's development is better understood as
four discrete architectural shifts than as incremental refinement, with the
decisive transition occurring in 2023 when retrieval changed from a fixed
pipeline stage into a decision made during generation. What follows from that
shift - evidence assessment, self-critique, structured indexing - are
consequences of treating retrieval as a control problem rather than a
preprocessing one.

Second, the paradigm's central assumption is weaker than its adoption implies.
Retrieval augmentation demonstrably reduces hallucination [P22], but [P32] shows
that RAG systems still produce unsupported content when correct evidence has
been retrieved, and [P11] shows retrieved evidence is used unreliably as a
function of its position in the context. Supplying evidence does not, by itself,
constrain generation. No system in this corpus enforces per-claim entailment
between output and retrieved evidence as a precondition for answering, which is
why entailment-gated generation is proposed here as the highest-value direction.

Third, the field's evaluation practice is a live threat to its own conclusions.
Cross-paper numeric comparison is routinely presented despite being invalid
across differing base models and splits; verification cost is essentially never
reported alongside accuracy gains; and grounding-aware metrics increasingly
depend on language-model judges whose reliability against correlated failure
modes is unestablished. These are not peripheral concerns - they determine
whether reported progress is real.

Given [P15]'s formal result that hallucination cannot be eliminated and [P16]'s
argument that evaluation incentives sustain it, the appropriate objective is not
a hallucination-free system. It is a system whose residual error rate is
bounded, measured, reported alongside its cost, and made visible to whoever
relies on the output. The techniques reviewed here move toward that goal
unevenly: retrieval and verification have advanced substantially, while
abstention - the behaviour that makes a bounded error rate safe to deploy -
remains the least developed capability in the literature.
""".strip()


def word_count(text: str) -> int:
    import re
    return len(re.sub(r"\[[PR]\d\d\]", "", text).split())
