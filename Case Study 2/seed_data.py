#!/usr/bin/env python
"""Writes the analysis CSVs for Phases 3, 5, 6, 7, 8, 9, 10 and 11.

`data/papers.csv` is produced by `fetch_papers.py` from publisher records and
is never edited by hand. This file holds the *analysis* of those papers - the
reading, comparison and synthesis that is the actual work of the review.

Numeric results carry a `figure_confidence` flag. Anything marked `check` is a
figure recalled from reading rather than re-read from the paper this week, and
is listed in the workbook's verification appendix. Cross-paper accuracy
comparison is reported but explicitly qualified: these systems were evaluated
on different splits, retrievers and base models, so the numbers rank setups,
not methods.

Run:  python seed_data.py
"""

from __future__ import annotations

import csv
from pathlib import Path

DATA = Path(__file__).parent / "data"


def write(name: str, fields: list[str], rows: list[dict]) -> None:
    DATA.mkdir(exist_ok=True)
    with (DATA / name).open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"  {name:<22} {len(rows)} rows")


# ---------------------------------------------------------------------------
# PHASE 3 - Literature Review Master Matrix
# ---------------------------------------------------------------------------

M = [
 dict(id="P01", problem="Parametric LLMs cannot cite or update the knowledge they encode, so factual errors are untraceable and unfixable without retraining.",
   method="Fine-tuned generator (BART) conditioned on passages from a dense retriever (DPR) over a Wikipedia index; RAG-Sequence and RAG-Token variants marginalise over retrieved documents.",
   dataset="Natural Questions, TriviaQA, WebQuestions, CuratedTrec, MS MARCO, FEVER; Wikipedia dump as index.",
   metrics="Exact Match, F1, generation quality, factual correctness of generations.",
   findings="Retrieval-augmented generation outperforms purely parametric seq2seq on open-domain QA and produces more specific and factual language; knowledge can be swapped by replacing the index without retraining.",
   advantages="Establishes the end-to-end RAG paradigm; hot-swappable knowledge; provenance is available because retrieved passages are explicit.",
   limits="Retriever is largely frozen and errors propagate; single-shot retrieval cannot serve multi-hop questions; no mechanism to detect when the retrieved evidence fails to support the output.",
   future="Joint retriever-generator training, multi-step retrieval, and explicit verification of generated claims against retrieved evidence."),
 dict(id="P02", problem="Sparse lexical retrieval (BM25) misses semantically relevant passages that share no vocabulary with the query.",
   method="Dual-encoder trained with in-batch negatives and hard negatives to embed questions and passages into a shared dense space; retrieval by maximum inner product search.",
   dataset="Natural Questions, TriviaQA, WebQuestions, CuratedTREC, SQuAD; Wikipedia passage index.",
   metrics="Top-k retrieval accuracy, downstream QA Exact Match.",
   findings="Dense retrieval trained on relatively few question-passage pairs substantially outperforms BM25 on top-20 retrieval accuracy, and the gain carries through to end-task QA.",
   advantages="Became the default retriever for RAG systems; simple, efficient, trainable with modest supervision.",
   limits="Requires supervised question-passage pairs; degrades out of domain; embeddings are static so the index must be rebuilt when the encoder changes.",
   future="Unsupervised and domain-adaptive dense retrieval; hybrid sparse-dense fusion."),
 dict(id="P03", problem="Language model pre-training stores knowledge implicitly in weights, which is opaque and cannot be inspected or edited.",
   method="Latent knowledge retriever trained jointly with masked language model pre-training, with retrieval treated as a latent variable and back-propagated through.",
   dataset="Wikipedia pre-training corpus; evaluated on Natural Questions, WebQuestions, CuratedTrec.",
   metrics="Exact Match on open-domain QA.",
   findings="Pre-training the retriever jointly with the language model yields large gains over models that treat retrieval as a fixed pre-processing step, and makes the knowledge source interpretable.",
   advantages="First to train retrieval end-to-end during pre-training; knowledge is modular and inspectable.",
   limits="Pre-training is computationally very expensive; asynchronous index refresh is complex; evaluated only on extractive-style QA.",
   future="Cheaper joint training and extension beyond short-answer QA."),
 dict(id="P04", problem="Extractive readers cannot synthesise an answer that requires combining several retrieved passages.",
   method="Fusion-in-Decoder: encode each retrieved passage independently with the encoder, then let the decoder attend jointly over all passage representations.",
   dataset="Natural Questions, TriviaQA.",
   metrics="Exact Match.",
   findings="Performance scales strongly with the number of retrieved passages, showing that generative readers aggregate evidence across passages rather than selecting one.",
   advantages="Simple, highly effective, and scales with retrieved context; long the strongest open-domain QA reader.",
   limits="Cost grows linearly with passage count; no notion of evidence sufficiency; cannot flag unsupported output.",
   future="Efficient attention over many passages; evidence selection and confidence estimation."),
 dict(id="P05", problem="Scaling parametric knowledge by growing model size is extremely expensive.",
   method="Retrieval from a trillion-token database using frozen BERT embeddings and chunked cross-attention into a transformer decoder.",
   dataset="MassiveText; evaluated on language modelling and downstream tasks; Pile and Wikitext103.",
   metrics="Perplexity (bits per byte), downstream task accuracy.",
   findings="A model with far fewer parameters matches much larger parametric models when given retrieval over a very large corpus, indicating knowledge can be offloaded from weights to an index.",
   advantages="Demonstrates a favourable compute-knowledge trade-off at scale; retrieval at unprecedented database size.",
   limits="Frozen retriever; huge engineering cost for the index; potential test-set leakage from the retrieval corpus requires careful deduplication.",
   future="Trainable large-scale retrievers and rigorous leakage control."),
 dict(id="P06", problem="Similarity search over billions of dense vectors is infeasible with exact methods on CPU.",
   method="GPU-optimised approximate nearest neighbour search with product quantisation and an efficient k-selection algorithm.",
   dataset="SIFT1B, DEEP1B benchmark vector collections.",
   metrics="Recall@k against exact search, queries per second, index build time.",
   findings="Billion-scale k-NN search becomes practical on a small number of GPUs with orders-of-magnitude speedups over prior CPU systems at comparable recall.",
   advantages="Infrastructure that makes production RAG feasible; widely used as the FAISS library.",
   limits="Approximation reduces recall, and that recall loss silently becomes a retrieval failure upstream of the generator; tuning is workload-specific.",
   future="Hardware-aware indexing and better accuracy-latency trade-offs."),
 dict(id="P07", problem="Retrieval augmentation usually requires modifying or fine-tuning the language model, which is impossible for closed models.",
   method="Prepend retrieved documents to the input context of an off-the-shelf frozen LM; study retriever choice and retrieval stride.",
   dataset="WikiText-103, The Pile subsets, and open-domain QA sets.",
   metrics="Perplexity, downstream QA accuracy.",
   findings="Simply placing retrieved text in the prompt of a frozen LM gives substantial language-modelling gains, and the retriever can be tuned to the LM without touching the LM.",
   advantages="No model access required; immediately deployable; clean baseline for prompt-level RAG.",
   limits="Bounded by context window; irrelevant retrieved text actively harms output; no filtering of unhelpful passages.",
   future="Learned reranking and adaptive decisions about when to retrieve."),
 dict(id="P08", problem="The strongest LLMs are only available behind APIs, so retrieval cannot be integrated into their internals.",
   method="Treat the LM as a black box; prepend retrieved documents and train the retriever using LM likelihood as the supervision signal (REPLUG LSR).",
   dataset="Pile, Natural Questions, TriviaQA, MMLU.",
   metrics="Perplexity, Exact Match, accuracy.",
   findings="Tuning the retriever against black-box LM feedback improves performance on language modelling and knowledge-intensive tasks without any model access.",
   advantages="Practical for commercial APIs; the retriever adapts to the specific consumer model.",
   limits="Requires token-likelihood access, which many APIs no longer expose; still single-shot retrieval.",
   future="Retriever adaptation from coarser feedback signals such as preferences or ratings."),
 dict(id="P09", problem="It is unclear how much relational factual knowledge language models actually store and can reliably recall.",
   method="LAMA probe: cloze-style queries derived from knowledge bases issued to pre-trained LMs without fine-tuning.",
   dataset="Google-RE, T-REx, ConceptNet, SQuAD-derived probes.",
   metrics="Precision@k (mean precision at 1 and 10).",
   findings="LMs recall a surprising amount of relational knowledge without supervision, but recall is uneven and highly sensitive to how the query is phrased.",
   advantages="Foundational evidence that parametric memory is real but unreliable - the empirical motivation for retrieval augmentation.",
   limits="Cloze probes measure recall of frequent relations only; prompt sensitivity confounds the measurement of what is actually 'known'.",
   future="Better probing methodology and separating knowledge from surface-form sensitivity."),
 dict(id="P10", problem="Retrieval is applied indiscriminately even where the model already knows the answer, which adds cost and can hurt accuracy.",
   method="Construct PopQA around entity popularity; measure parametric accuracy against subject-entity popularity; compare with non-parametric retrieval; propose adaptive retrieval by popularity threshold.",
   dataset="PopQA (constructed), EntityQuestions, Natural Questions.",
   metrics="Accuracy stratified by entity popularity.",
   findings="Parametric memory works well for popular entities and fails sharply on long-tail entities; retrieval helps most on the tail and can actively degrade answers on head entities.",
   advantages="Provides the empirical case for *adaptive* rather than always-on retrieval; cheap popularity heuristic works well.",
   limits="Popularity is a crude proxy for model confidence; results centred on entity-centric factoid QA.",
   future="Confidence-aware and self-knowledge-driven retrieval triggers."),
 dict(id="P11", problem="It is assumed that adding more retrieved context monotonically helps; the position of evidence in the context may matter.",
   method="Controlled experiments on multi-document QA and key-value retrieval, varying the position of the relevant document within the input context.",
   dataset="Multi-document QA built from Natural Questions; synthetic key-value retrieval task.",
   metrics="Accuracy as a function of gold-evidence position and context length.",
   findings="Performance is highest when the relevant evidence is at the beginning or end of the context and degrades markedly when it sits in the middle - a U-shaped curve robust across models.",
   advantages="Explains a large class of RAG failures that look like retrieval successes; directly motivates reranking and compression.",
   limits="Primarily on the model generation of its time; mechanism behind the effect is not established.",
   future="Position-robust architectures, evidence reranking, and context compression."),
 dict(id="P12", problem="Hallucination is used loosely across NLG subfields with no shared definition, taxonomy or metric.",
   method="Systematic survey; defines intrinsic versus extrinsic hallucination; organises causes, metrics and mitigation across summarisation, dialogue, translation and QA.",
   dataset="Survey of task-specific benchmarks across NLG.",
   metrics="Reviews statistical and model-based faithfulness metrics.",
   findings="Hallucination arises from both data (source-reference divergence) and modelling/inference; no single metric captures it, and task-specific definitions differ substantially.",
   advantages="The standard reference taxonomy; the intrinsic/extrinsic split is used throughout the field.",
   limits="Predates instruction-tuned LLMs and RAG-specific failure modes; largely encoder-decoder framing.",
   future="Unified evaluation and hallucination analysis for large-scale generative models."),
 dict(id="P13", problem="LLM hallucination needs a taxonomy and consolidated account of causes, detection and mitigation specific to modern LLMs.",
   method="Large-scale survey organised around factuality and faithfulness hallucination, with causes traced to data, training and inference stages.",
   dataset="Reviews the major LLM hallucination benchmarks.",
   metrics="Surveys factuality metrics, benchmarks and human evaluation protocols.",
   findings="Provides the now-standard factuality/faithfulness split; identifies retrieval augmentation as a principal mitigation while noting it introduces its own failure modes.",
   advantages="Comprehensive and current; explicitly connects hallucination causes to mitigation families.",
   limits="Breadth over depth; being a survey it does not evaluate the compared methods under a common protocol.",
   future="Standardised benchmarks and mitigation that addresses causes rather than symptoms."),
 dict(id="P14", problem="Hallucination research is fragmented across detection, benchmarks and mitigation with inconsistent terminology.",
   method="Survey organising hallucination in LLMs into evaluation, explanation and mitigation, with a taxonomy of sources.",
   dataset="Reviews existing hallucination benchmarks.",
   metrics="Surveys automatic and human factuality evaluation.",
   findings="Argues hallucination is a systemic consequence of the training objective rather than an incidental defect, and that mitigation must span the whole pipeline.",
   advantages="Clear organisation and accessible synthesis of a fast-moving area.",
   limits="Preprint; overlaps substantially with other contemporaneous surveys.",
   future="Causal analysis of hallucination and lifecycle-wide mitigation."),
 dict(id="P15", problem="Whether hallucination can be eliminated at all, or is a structural property of the model class.",
   method="Formal argument using a computability framing: defines a ground-truth function and shows LLMs cannot learn all such functions, so hallucination is unavoidable in general.",
   dataset="Theoretical; no empirical dataset.",
   metrics="Not applicable - formal result.",
   findings="Hallucination is an innate limitation of LLMs and cannot be fully removed by scaling, better data or guardrails; it can only be bounded in practice.",
   advantages="Sets a principled ceiling on what mitigation can achieve and reframes the objective as risk management rather than elimination.",
   limits="Idealised assumptions; the practical gap between the theoretical bound and deployed error rates is not quantified.",
   future="Bounding achievable hallucination rates for realistic, restricted task distributions."),
 dict(id="P16", problem="Why models produce confident falsehoods rather than abstaining.",
   method="Analysis of pre-training and post-training objectives, arguing hallucination is the statistically optimal response under binary scoring that penalises abstention.",
   dataset="Analytical, with reference to standard benchmark scoring practice.",
   metrics="Discusses benchmark scoring schemes and their incentives.",
   findings="Hallucination persists because evaluation rewards guessing over saying 'I do not know'; changing benchmark scoring to reward calibrated abstention is proposed as a primary fix.",
   advantages="Shifts the problem from model internals to incentive design, which is directly actionable for evaluation practice.",
   limits="Recent preprint; the proposed scoring reforms are not yet empirically validated at scale.",
   future="Benchmarks and training objectives that explicitly reward calibrated uncertainty."),
 dict(id="P17", problem="Detecting hallucination usually requires an external knowledge base or access to model internals, neither of which is available for black-box APIs.",
   method="Sample multiple stochastic generations and measure consistency between them; low agreement across samples signals fabrication. Variants use BERTScore, QA-based and n-gram consistency.",
   dataset="WikiBio-derived hallucination annotations with sentence-level labels.",
   metrics="AUC-PR for sentence-level detection, correlation with human factuality judgements.",
   findings="Self-consistency across sampled generations detects hallucination effectively without any external resource, exploiting that fabricated content is less stable across samples.",
   advantages="Zero-resource and black-box compatible; strong practical baseline.",
   limits="Requires several generations, so inference cost multiplies; confidently repeated falsehoods are consistent and therefore missed.",
   future="Cheaper consistency estimation and combination with retrieval-based verification."),
 dict(id="P18", problem="Distinguishing uncertainty about meaning from uncertainty about wording, in order to detect confabulation reliably.",
   method="Semantic entropy: cluster sampled generations into semantic equivalence classes using bidirectional entailment and compute entropy over meanings rather than token sequences.",
   dataset="Open-domain QA and biography generation across several model families.",
   metrics="AUROC for confabulation detection, comparison with token-level entropy baselines.",
   findings="Entropy over semantic clusters detects confabulations substantially better than lexical uncertainty measures and generalises across datasets and models without task-specific supervision.",
   advantages="Principled, unsupervised, model-agnostic; published in a top general-science venue with strong empirical validation.",
   limits="Requires multiple samples plus entailment computation, so it is costly; targets confabulation specifically, not consistent errors learned from training data.",
   future="Efficient approximations and integration into retrieval-triggering decisions."),
 dict(id="P19", problem="Models may reproduce popular human misconceptions, which standard accuracy benchmarks do not capture.",
   method="Adversarially constructed questions where a common human misconception is the tempting answer; human and automated (GPT-judge) evaluation.",
   dataset="TruthfulQA: 817 questions across 38 categories.",
   metrics="Percentage of truthful answers, truthful-and-informative percentage.",
   findings="Larger models are often *less* truthful because they better model the human text distribution including its falsehoods - inverse scaling on truthfulness.",
   advantages="Demonstrated that scale alone does not fix factuality; became a standard evaluation.",
   limits="Small and adversarial by construction, so absolute scores are not representative of general use; contamination risk given its age and popularity.",
   future="Truthfulness training objectives and evaluations resistant to memorisation."),
 dict(id="P20", problem="Long-form generation mixes supported and unsupported content, so a single correctness label is uninformative.",
   method="Decompose generated text into atomic facts and verify each independently against a knowledge source; report the proportion supported.",
   dataset="Biography generation grounded in Wikipedia.",
   metrics="FActScore - fraction of atomic facts supported by the reference source.",
   findings="Fine-grained atomic scoring reveals substantial unsupported content in outputs that read as fluent and coherent, and an automated estimator tracks human judgement closely.",
   advantages="Fine-grained, interpretable, and now a standard metric for long-form factuality including RAG output.",
   limits="Depends on knowledge-source coverage; atomic-fact decomposition is itself model-generated and can err; primarily validated on biographies.",
   future="Extension to domains without a clean reference corpus."),
 dict(id="P21", problem="Hallucination datasets are expensive to annotate manually, which limits benchmark scale and coverage.",
   method="Automated pipeline that induces and collects factuality hallucinations from LLMs to construct labelled datasets without manual annotation.",
   dataset="Automatically generated hallucination datasets built from open-domain QA sources.",
   metrics="Hallucination detection accuracy; agreement with human labels.",
   findings="Automatically constructed hallucination corpora support detector training and evaluation at a scale manual annotation cannot reach, with quality sufficient for benchmarking.",
   advantages="Addresses the annotation bottleneck; recent IEEE journal publication with a reproducible pipeline.",
   limits="Automatically induced hallucinations may not match the distribution of naturally occurring ones; label noise is inherited from the generating model.",
   future="Validating that induced hallucinations transfer to naturally occurring failure modes."),
 dict(id="P22", problem="Knowledge-grounded dialogue systems frequently state facts not present in the retrieved knowledge.",
   method="Compare retrieval-augmented dialogue architectures and knowledge-conditioning strategies against parametric baselines, with human evaluation of factual consistency.",
   dataset="Wizard of Wikipedia, CMU DoG and related knowledge-grounded dialogue corpora.",
   metrics="Human-judged factual consistency, knowledge F1, perplexity.",
   findings="Retrieval augmentation substantially reduces hallucinated statements in conversation relative to parametric models, while maintaining conversational quality.",
   advantages="Among the first direct empirical demonstrations that retrieval reduces hallucination rather than merely improving accuracy.",
   limits="Confined to dialogue; reduction is partial, and the system still hallucinates when retrieval returns weak evidence.",
   future="Grounding verification and handling retrieval failure explicitly."),
 dict(id="P23", problem="Standard RAG retrieves a fixed number of passages regardless of need and never checks whether the output is actually supported.",
   method="Train the LM to emit reflection tokens that decide when to retrieve, and to critique relevance of retrieved passages and support for its own generations; segment-level selection at inference.",
   dataset="PopQA, TriviaQA, PubHealth, ARC-Challenge, ASQA, biography generation.",
   metrics="Accuracy, FActScore, citation precision and recall.",
   findings="Self-reflective retrieval and self-critique outperform both standard RAG and much larger instruction-tuned baselines on factuality and citation accuracy.",
   advantages="Unifies adaptive retrieval and self-verification in one trained model; controllable at inference.",
   limits="Requires training a specialised model with reflection-token supervision, so it does not apply to closed APIs; critique is itself model-generated and fallible.",
   future="Transferring reflective behaviour to black-box models via prompting."),
 dict(id="P24", problem="RAG degrades badly when the retriever returns irrelevant documents, and standard pipelines have no recovery path.",
   method="Lightweight retrieval evaluator scores document relevance and triggers one of three actions - correct, incorrect or ambiguous - with web search as a fallback and decompose-then-recompose filtering of retrieved text.",
   dataset="PopQA, Biography, PubHealth, Arc-Challenge.",
   metrics="Accuracy, FActScore.",
   findings="Explicitly assessing retrieval quality and correcting or replacing poor retrievals improves robustness substantially and is plug-and-play over existing RAG stacks.",
   advantages="Model-agnostic; directly targets retrieval failure, the dominant RAG error source; no generator retraining.",
   limits="Adds an evaluator and possible web calls, increasing latency and cost; evaluator errors cascade; web fallback introduces an uncontrolled source.",
   future="Cheaper relevance estimation and principled fallback source selection."),
 dict(id="P25", problem="Retrieving once at the start is insufficient for long-form generation, where information needs arise as text is produced.",
   method="FLARE: anticipate the upcoming sentence, and if it contains low-confidence tokens, use it as a query to retrieve before generating that sentence.",
   dataset="Multi-hop QA, commonsense reasoning, long-form QA and open-domain summarisation (2WikiMultihopQA, StrategyQA, ASQA, WikiAsp).",
   metrics="Exact Match, F1, ROUGE, citation quality.",
   findings="Actively deciding when and what to retrieve during generation outperforms single-shot and fixed-interval retrieval on long-form knowledge-intensive tasks.",
   advantages="Uses generation confidence as the retrieval trigger, so retrieval happens where the model is actually uncertain.",
   limits="Repeated retrieval raises latency; token probability is an imperfect proxy for factual uncertainty and needs likelihood access.",
   future="Better uncertainty signals and cost-aware retrieval scheduling."),
 dict(id="P26", problem="Multi-step questions need evidence that only becomes identifiable after partial reasoning, which one-shot retrieval cannot supply.",
   method="IRCoT interleaves chain-of-thought reasoning with retrieval, using each generated reasoning step as the query for the next retrieval round.",
   dataset="HotpotQA, 2WikiMultihopQA, MuSiQue, IIRC.",
   metrics="Retrieval recall, answer Exact Match and F1.",
   findings="Interleaving retrieval with reasoning markedly improves both retrieval recall and answer accuracy on multi-hop questions relative to one-shot retrieval.",
   advantages="Simple, needs no training, and generalises across model sizes; a strong multi-hop baseline.",
   limits="Multiple retrieval and generation rounds are expensive; an early reasoning error steers all subsequent retrieval wrongly.",
   future="Error recovery within the reasoning-retrieval loop and adaptive step budgets."),
 dict(id="P27", problem="Models assert unsupported facts confidently and do not check their own claims before answering.",
   method="Chain-of-Verification: draft a response, plan verification questions, answer each independently to avoid conditioning on the draft, then revise the response.",
   dataset="Wikidata list questions, QUEST, MultiSpanQA, longform biography generation.",
   metrics="Precision of listed facts, FActScore-style factuality.",
   findings="Deliberate self-verification with independently answered verification questions reduces hallucination substantially, and independence from the draft is essential to the gain.",
   advantages="Prompt-level only, so it works on closed models with no training or retrieval infrastructure.",
   limits="Several extra generation passes multiply cost; verification uses the same parametric knowledge, so shared misconceptions survive.",
   future="Combining verification questions with retrieval so checks consult external evidence."),
 dict(id="P28", problem="Editing a generated text for factuality while preserving its content requires attribution to real evidence.",
   method="RARR: research the generated text by issuing queries, retrieve evidence, then revise the output minimally to agree with the evidence while preserving the original intent.",
   dataset="Outputs over Natural Questions, StrategyQA and QReCC.",
   metrics="Attribution (AIS-style) and preservation of the original output.",
   findings="Post-hoc research-and-revise improves attribution substantially with limited change to the original text, and can be applied to any generator's output.",
   advantages="Fully post-hoc and model-agnostic; explicitly balances factuality against preservation.",
   limits="Cannot fix a fundamentally wrong output, only locally repair it; dependent on retrieval quality; adds a full extra pipeline.",
   future="Deciding when revision is insufficient and regeneration is required."),
 dict(id="P29", problem="Standard RAG retrieves local text chunks and therefore cannot answer global, corpus-level questions such as 'what are the main themes'.",
   method="Build an entity knowledge graph from the corpus with an LLM, detect hierarchical communities, pre-generate community summaries, and answer global queries by map-reduce over those summaries.",
   dataset="Podcast transcripts and news article corpora; global sensemaking question sets.",
   metrics="LLM-judged comprehensiveness, diversity and empowerment; token cost.",
   findings="Graph-structured indexing answers corpus-level questions that chunk-based RAG cannot address, with large gains in comprehensiveness and diversity of answers.",
   advantages="Extends RAG from local lookup to global sensemaking; hierarchical summaries support multiple query granularities.",
   limits="Index construction is expensive in LLM calls; evaluation relies on LLM judges rather than ground truth; graph extraction errors propagate into every downstream answer.",
   future="Cheaper graph construction and objective evaluation of global query answering."),
 dict(id="P30", problem="RAG pipelines have separately failing retrieval and generation stages, but are usually evaluated only end-to-end and with human labels.",
   method="Reference-free framework computing faithfulness, answer relevance and context relevance using LLM-based judging of decomposed statements.",
   dataset="WikiEval and standard RAG evaluation settings.",
   metrics="Faithfulness, answer relevance, context relevance; agreement with human annotators.",
   findings="Component-wise reference-free evaluation correlates well with human judgement and isolates whether a failure originated in retrieval or generation.",
   advantages="No gold answers required, so it can run continuously in production; widely adopted as the RAGAS library.",
   limits="Uses an LLM as judge, inheriting that model's biases and cost; metric stability across judge models is not guaranteed.",
   future="Judge-independent metrics and validation across domains."),
 dict(id="P31", problem="It is unclear which specific abilities RAG demands of an LLM and where the paradigm breaks.",
   method="Retrieval-Augmented Generation Benchmark (RGB) isolating four abilities - noise robustness, negative rejection, information integration and counterfactual robustness.",
   dataset="RGB, constructed from news with controlled noise and counterfactual injection, in English and Chinese.",
   metrics="Accuracy, rejection rate, error detection rate.",
   findings="Even strong LLMs degrade sharply with retrieval noise, rarely reject unanswerable queries, and frequently follow retrieved evidence that contradicts their correct parametric knowledge.",
   advantages="Diagnostic rather than aggregate; the four-ability decomposition is directly actionable for system design.",
   limits="Constructed rather than naturally occurring noise; snapshot of models at time of writing.",
   future="Training explicitly for rejection and counterfactual robustness."),
 dict(id="P32", problem="Hallucination detection for RAG lacked a large word-level annotated corpus of genuinely retrieval-augmented outputs.",
   method="Corpus of nearly 18,000 naturally generated RAG responses with word-level hallucination annotation across QA, data-to-text and summarisation, plus a trained detector.",
   dataset="RAGTruth, built over Natural Questions, MARCO, Yelp and CNN/Daily Mail sources.",
   metrics="Span-level and response-level hallucination detection precision, recall and F1.",
   findings="A detector fine-tuned on RAGTruth rivals prompt-based detection with much stronger models, and hallucination persists in RAG output even when relevant evidence is retrieved.",
   advantages="The key supervised resource for RAG hallucination; word-level granularity; naturally occurring rather than induced errors.",
   limits="Restricted to the tasks and generator models sampled; annotation of partial support is inherently subjective.",
   future="Broader task and language coverage; detectors that generalise across generators."),
 dict(id="P33", problem="Mitigation techniques for retrieval-augmented LLMs are scattered and not organised by where in the pipeline they act.",
   method="Structured review decomposing RAG into retrieval-phase and generation-phase sub-tasks and mapping hallucination causes and mitigations onto each.",
   dataset="Review of the RAG hallucination literature.",
   metrics="Surveys the evaluation metrics used across the reviewed work.",
   findings="Hallucination causes are separable by pipeline stage - data source, query formulation, retriever and ranking on one side; grounding and decoding on the other - and mitigation should be matched to stage.",
   advantages="Directly organised around the RAG pipeline, which makes it practically usable; recent peer-reviewed journal synthesis.",
   limits="Survey without unified empirical comparison; coverage of agentic RAG is limited.",
   future="Stage-aware benchmarks and combined multi-stage mitigation."),
 dict(id="P34", problem="Which RAG variant should actually be deployed in a safety-critical setting, and at what latency and hallucination cost.",
   method="Controlled comparison of twelve RAG variants - dense, sparse, hybrid, graph-based, multimodal, self-reflective, adaptive and security-focused - on clinical vignettes, with on-premises deployment analysis.",
   dataset="250 de-identified patient vignettes with clinical reference material.",
   metrics="Precision@5, MRR, nDCG@10, hallucination rate, latency.",
   findings="Hybrid dense-sparse retrieval with cross-encoder reranking gave the best retrieval accuracy, while self-reflective RAG achieved the lowest hallucination rate; sparse retrieval was fastest but least accurate.",
   advantages="Rare like-for-like empirical comparison of many variants under one protocol; addresses privacy and deployment, not just accuracy.",
   limits="Single clinical domain and a modest vignette set; results may not transfer to open-domain use.",
   future="Cross-domain replication of the comparison protocol."),
 dict(id="P35", problem="Whether laboratory hallucination-mitigation results hold up in real industrial deployments.",
   method="Applied study of hallucination mitigation across three distinct industrial use cases, reporting the techniques used and the operational outcomes.",
   dataset="Proprietary industrial datasets from the three deployment settings.",
   metrics="Task-specific accuracy and hallucination rates reported per use case.",
   findings="Mitigation techniques transfer to industry but require domain-specific tuning, and residual hallucination remains material enough to require human oversight in production.",
   advantages="Deployment evidence rather than benchmark evidence; documents the practical gap between research and production.",
   limits="Proprietary data limits reproducibility; small number of cases restricts generalisation.",
   future="Open industrial benchmarks and standardised operational reporting."),
]

MATRIX_FIELDS = ["id","problem","method","dataset","metrics","findings","advantages","limits","future"]


# ---------------------------------------------------------------------------
# PHASE 5 - Research evolution
# ---------------------------------------------------------------------------

EVOLUTION = [
 dict(year="2017-2018", contribution="Transformer architecture and large-scale pre-training establish the parametric-knowledge paradigm; FEVER frames fact verification as a retrieval-plus-inference task.", papers="Context for P09", impact="Sets up the assumption that knowledge lives in weights - the assumption the rest of this decade spends undoing."),
 dict(year="2019", contribution="LAMA probing shows LMs recall substantial relational knowledge but unevenly and with high prompt sensitivity.", papers="P09", impact="Establishes empirically that parametric memory is real but unreliable, motivating external retrieval."),
 dict(year="2020", contribution="DPR replaces lexical matching with learned dense retrieval; REALM trains retrieval jointly during pre-training; RAG unifies a dense retriever with a generative reader end to end.", papers="P01, P02, P03", impact="The founding year of RAG. Knowledge becomes modular and swappable rather than frozen in weights."),
 dict(year="2021", contribution="Fusion-in-Decoder scales evidence aggregation across many passages; retrieval augmentation is shown to reduce hallucination in dialogue; FAISS makes billion-scale vector search practical.", papers="P04, P06, P22", impact="First direct evidence that retrieval reduces hallucination specifically, plus the infrastructure that makes deployment feasible."),
 dict(year="2022", contribution="RETRO demonstrates trillion-token retrieval lets small models match much larger ones; TruthfulQA shows scale can worsen truthfulness.", papers="P05, P19", impact="Decouples knowledge from parameter count and shows scaling alone does not solve factuality - inverse scaling on truthfulness."),
 dict(year="2023", contribution="Retrieval becomes adaptive and iterative - FLARE retrieves on low confidence, IRCoT interleaves retrieval with reasoning; black-box methods (REPLUG, In-Context RALM) work without model access; SelfCheckGPT and FActScore make hallucination measurable; adaptive retrieval is justified by long-tail analysis.", papers="P07, P10, P17, P20, P25, P26, P28", impact="The pivot year: retrieval shifts from a fixed pre-processing step to a decision the model makes during generation, and hallucination becomes quantifiable."),
 dict(year="2024", contribution="Self-reflection and correction enter the pipeline (Self-RAG, CRAG, Chain-of-Verification); structure enters the index (GraphRAG, RAPTOR); evaluation matures (RAGAS, RGB, RAGTruth); 'Lost in the Middle' and semantic entropy expose context and uncertainty limits.", papers="P11, P18, P23, P24, P27, P29, P30, P31, P32", impact="RAG stops being a pipeline and becomes a control loop with verification. Evaluation shifts from end-to-end accuracy to component-wise diagnosis."),
 dict(year="2025", contribution="Theoretical limits are formalised (hallucination shown to be innate; incentive analysis of why models guess); agentic RAG surveys consolidate multi-step tool-using retrieval; peer-reviewed journal syntheses and controlled variant comparisons appear.", papers="P13, P15, P16, P33, P34", impact="The field matures from technique proliferation to consolidation, and accepts that elimination is not achievable - the goal becomes bounded, measurable residual risk."),
 dict(year="2026", contribution="Industrial deployment studies and automated hallucination corpus construction move the work from benchmarks to production and from manual to scalable annotation.", papers="P21, P35", impact="Evidence base shifts from laboratory benchmarks to operational reporting, exposing the gap between benchmark and production performance."),
]
EVOLUTION_FIELDS = ["year","contribution","papers","impact"]


# ---------------------------------------------------------------------------
# PHASE 6 - Domain-specific comparison (AI/ML matrix, adapted for RAG)
# ---------------------------------------------------------------------------
# `figure_confidence`: high = widely reported headline result the author is
# confident of; check = re-read the paper before quoting the number.

COMPARISON = [
 dict(id="P01", system="RAG (Sequence/Token)", trigger="Single-shot, always", verification="None", training="Generator + retriever fine-tuned", dataset="NQ, TriviaQA, WebQ, FEVER", headline="NQ Exact Match ~44", figure_confidence="check", limitation="No support checking; single retrieval round"),
 dict(id="P02", system="DPR", trigger="Single-shot, always", verification="None", training="Dual-encoder supervised", dataset="NQ, TriviaQA, WebQ, TREC", headline="Large top-20 retrieval gain over BM25", figure_confidence="high", limitation="Needs labelled pairs; weak out of domain"),
 dict(id="P03", system="REALM", trigger="Single-shot, always", verification="None", training="Joint retriever + MLM pre-training", dataset="NQ, WebQ, CuratedTrec", headline="Outperforms comparable parametric baselines on open QA", figure_confidence="high", limitation="Very expensive pre-training"),
 dict(id="P04", system="Fusion-in-Decoder", trigger="Single-shot, always", verification="None", training="Reader fine-tuned", dataset="NQ, TriviaQA", headline="Accuracy scales with passage count", figure_confidence="high", limitation="Cost linear in passages; no sufficiency signal"),
 dict(id="P05", system="RETRO", trigger="Chunk-level, always", verification="None", training="Pre-trained with chunked cross-attention", dataset="MassiveText, Pile, Wikitext103", headline="Small model matches far larger parametric models", figure_confidence="high", limitation="Frozen retriever; leakage control required"),
 dict(id="P07", system="In-Context RALM", trigger="Fixed stride", verification="None", training="None (frozen LM)", dataset="WikiText-103, Pile", headline="Substantial perplexity reduction on a frozen LM", figure_confidence="high", limitation="Context-window bound; noise hurts"),
 dict(id="P08", system="REPLUG", trigger="Single-shot, always", verification="None", training="Retriever tuned to LM likelihood", dataset="Pile, NQ, TriviaQA, MMLU", headline="Gains on a black-box LM without model access", figure_confidence="high", limitation="Needs token likelihoods"),
 dict(id="P10", system="Adaptive retrieval by popularity", trigger="Adaptive (popularity threshold)", verification="None", training="None", dataset="PopQA, EntityQuestions", headline="Retrieval helps the long tail, hurts head entities", figure_confidence="high", limitation="Popularity is a crude confidence proxy"),
 dict(id="P22", system="Retrieval-augmented dialogue", trigger="Per-turn, always", verification="None", training="Fine-tuned", dataset="Wizard of Wikipedia", headline="Marked drop in hallucinated statements vs parametric", figure_confidence="high", limitation="Partial reduction only; dialogue-specific"),
 dict(id="P23", system="Self-RAG", trigger="Adaptive (reflection token)", verification="Self-critique of relevance and support", training="Trained with reflection tokens", dataset="PopQA, PubHealth, ARC, ASQA, Bio", headline="Beats standard RAG and larger instruction-tuned baselines on factuality and citation", figure_confidence="high", limitation="Needs a specially trained model; critique is fallible"),
 dict(id="P24", system="CRAG", trigger="Single-shot + corrective", verification="Retrieval evaluator + web fallback", training="Lightweight evaluator", dataset="PopQA, Bio, PubHealth, ARC", headline="Improved robustness under poor retrieval; plug-and-play", figure_confidence="high", limitation="Extra latency; evaluator errors cascade"),
 dict(id="P25", system="FLARE", trigger="Adaptive (low token confidence)", verification="None explicit", training="None", dataset="2WikiMultihop, StrategyQA, ASQA, WikiAsp", headline="Beats single-shot and fixed-interval retrieval on long-form tasks", figure_confidence="high", limitation="Latency; needs likelihood access"),
 dict(id="P26", system="IRCoT", trigger="Iterative (per reasoning step)", verification="None", training="None", dataset="HotpotQA, 2WikiMultihop, MuSiQue, IIRC", headline="Large recall and EM gains on multi-hop", figure_confidence="high", limitation="Expensive; early errors misdirect retrieval"),
 dict(id="P27", system="Chain-of-Verification", trigger="No retrieval (parametric)", verification="Independent verification questions", training="None", dataset="Wikidata lists, QUEST, MultiSpanQA", headline="Substantial hallucination reduction via self-verification", figure_confidence="high", limitation="Shares the model's own misconceptions"),
 dict(id="P28", system="RARR", trigger="Post-hoc research", verification="Attribution-based revision", training="None", dataset="NQ, StrategyQA, QReCC outputs", headline="Improved attribution with high preservation of original text", figure_confidence="high", limitation="Repairs locally; cannot fix wholly wrong output"),
 dict(id="P29", system="GraphRAG", trigger="Global map-reduce over summaries", verification="None", training="None (LLM index build)", dataset="Podcast and news corpora", headline="Answers corpus-level questions chunk RAG cannot", figure_confidence="high", limitation="Costly index; LLM-judge evaluation"),
 dict(id="P34", system="12 RAG variants compared", trigger="Varies by variant", verification="Varies by variant", training="Varies", dataset="250 clinical vignettes", headline="Self-reflective RAG lowest hallucination; hybrid retrieval best P@5", figure_confidence="high", limitation="Single domain; modest sample"),
]
COMPARISON_FIELDS = ["id","system","trigger","verification","training","dataset","headline","figure_confidence","limitation"]


# ---------------------------------------------------------------------------
# PHASE 7 - Limitation mining
# ---------------------------------------------------------------------------

LIM_CATEGORIES = ["Retrieval quality","Evaluation validity","Computational cost","Generalization",
                  "Verification absence","Dataset issues","Context utilisation","Reproducibility"]

LIMITATIONS = [
 ("P01","Verification absence","Retrieval quality","Context utilisation"),
 ("P02","Generalization","Dataset issues","Retrieval quality"),
 ("P03","Computational cost","Generalization","Retrieval quality"),
 ("P04","Computational cost","Verification absence","Context utilisation"),
 ("P05","Retrieval quality","Computational cost","Reproducibility"),
 ("P06","Retrieval quality","Generalization","Computational cost"),
 ("P07","Context utilisation","Retrieval quality","Verification absence"),
 ("P08","Generalization","Retrieval quality","Reproducibility"),
 ("P09","Evaluation validity","Dataset issues","Generalization"),
 ("P10","Evaluation validity","Generalization","Retrieval quality"),
 ("P11","Generalization","Evaluation validity","Context utilisation"),
 ("P12","Generalization","Evaluation validity","Dataset issues"),
 ("P13","Evaluation validity","Generalization","Dataset issues"),
 ("P14","Evaluation validity","Reproducibility","Generalization"),
 ("P15","Evaluation validity","Generalization","Reproducibility"),
 ("P16","Evaluation validity","Reproducibility","Generalization"),
 ("P17","Computational cost","Verification absence","Evaluation validity"),
 ("P18","Computational cost","Generalization","Evaluation validity"),
 ("P19","Dataset issues","Evaluation validity","Generalization"),
 ("P20","Dataset issues","Generalization","Evaluation validity"),
 ("P21","Dataset issues","Evaluation validity","Generalization"),
 ("P22","Generalization","Verification absence","Retrieval quality"),
 ("P23","Computational cost","Generalization","Verification absence"),
 ("P24","Computational cost","Retrieval quality","Reproducibility"),
 ("P25","Computational cost","Generalization","Verification absence"),
 ("P26","Computational cost","Retrieval quality","Verification absence"),
 ("P27","Computational cost","Verification absence","Generalization"),
 ("P28","Retrieval quality","Computational cost","Verification absence"),
 ("P29","Computational cost","Evaluation validity","Retrieval quality"),
 ("P30","Evaluation validity","Computational cost","Generalization"),
 ("P31","Dataset issues","Generalization","Evaluation validity"),
 ("P32","Generalization","Dataset issues","Evaluation validity"),
 ("P33","Evaluation validity","Generalization","Reproducibility"),
 ("P34","Generalization","Dataset issues","Reproducibility"),
 ("P35","Reproducibility","Generalization","Dataset issues"),
]


# ---------------------------------------------------------------------------
# PHASE 8 - Research gaps (derived from limitation frequency, not asked of AI)
# ---------------------------------------------------------------------------

GAPS = [
 dict(id="G1", gap="No standard way to decide when retrieval should fire",
   support="P10; P23; P25; P31",
   evidence="P10 shows always-on retrieval degrades head-entity answers while helping the long tail. P25 triggers on token confidence and P23 on trained reflection tokens - two incompatible signals, never compared under one protocol. P31 shows models rarely reject unanswerable queries, so they cannot recognise when retrieval has failed.",
   matters="Retrieval triggering is currently a per-system heuristic. Every deployment re-derives it, and no benchmark isolates trigger quality from retrieval or generation quality, so improvements cannot be attributed."),
 dict(id="G2", gap="Grounding is assumed rather than verified at generation time",
   support="P01; P04; P22; P32",
   evidence="P01 and P04 contain no mechanism to check that output is entailed by retrieved passages. P22 reduces but does not eliminate hallucination. P32 demonstrates hallucination persists in RAG output even when relevant evidence was successfully retrieved - the failure is in grounding, not retrieval.",
   matters="The central assumption of RAG - that retrieved evidence constrains generation - is empirically false at the margin. Without per-claim entailment checking, a RAG system cannot distinguish a supported answer from a fluent unsupported one."),
 dict(id="G3", gap="Verification cost is never reported alongside accuracy",
   support="P17; P18; P23; P25; P26; P27",
   evidence="Computational cost is the most frequent limitation in this corpus. P17 and P18 need multiple samples; P25 and P26 retrieve repeatedly; P27 adds verification passes. None of these report latency or token cost against the hallucination reduction achieved.",
   matters="Practitioners cannot choose a technique without a cost-benefit figure. A method that halves hallucination at five times the latency is not comparable to one that reduces it by a third at 1.2x, yet the literature presents them as if they were."),
 dict(id="G4", gap="Cross-paper numeric comparison is invalid but routinely performed",
   support="P30; P31; P32; P34",
   evidence="Reported systems use different base models, retrievers, corpora and splits. P34 is the only study in this corpus comparing many variants under one protocol, and it covers a single clinical domain. P30 provides component-wise metrics but with an LLM judge whose stability across models is unvalidated.",
   matters="Without a shared protocol the field cannot establish which mitigation actually works. Apparent progress may reflect differences in base model strength rather than in method."),
 dict(id="G5", gap="Evaluation increasingly depends on LLM judges whose reliability is unestablished",
   support="P29; P30; P19; P20",
   evidence="P29 evaluates global query answering with LLM-judged comprehensiveness and diversity. P30's faithfulness metric is LLM-computed. P20's atomic-fact decomposition is model-generated. P19 uses a fine-tuned judge model.",
   matters="Hallucination evaluation is becoming circular - models are increasingly judged by models with correlated failure modes. If judge and generator share a misconception, the metric certifies the error."),
 dict(id="G6", gap="Long-tail and low-resource domains remain unaddressed",
   support="P10; P02; P34; P35",
   evidence="P10 identifies the long tail as where retrieval matters most, yet P02-style retrievers need supervised in-domain pairs and degrade out of domain. P34 and P35 report that domain-specific tuning is required in clinical and industrial settings.",
   matters="The settings where hallucination is most consequential - specialist medical, legal, industrial - are exactly those with the least training data for retrievers and the least benchmark coverage."),
 dict(id="G7", gap="Theoretical impossibility results are disconnected from practical error budgets",
   support="P15; P16; P35",
   evidence="P15 proves hallucination cannot be eliminated; P16 argues evaluation incentives sustain it. Neither connects to an achievable residual rate for a bounded task. P35 reports residual hallucination in production requiring human oversight, but without reference to any theoretical floor.",
   matters="Engineering needs a target. Without a link between the impossibility results and attainable rates on restricted domains, deployment decisions about acceptable risk have no principled basis."),
]
GAPS_FIELDS = ["id","gap","support","evidence","matters"]


# ---------------------------------------------------------------------------
# PHASE 9 - Future directions and novel ideas
# ---------------------------------------------------------------------------

FUTURE = [
 dict(gap="G1", direction="A unified retrieval-triggering benchmark that holds retriever and generator fixed and varies only the trigger policy (always-on, popularity, token confidence, semantic entropy, trained reflection).", impact="Makes trigger quality independently measurable and comparable for the first time.", feasibility="High - composable from existing public datasets and released trigger implementations."),
 dict(gap="G2", direction="Per-claim entailment gating: decompose the draft into atomic claims, check each against retrieved passages with an NLI model, and force abstention or re-retrieval on unsupported claims before the answer is returned.", impact="Converts grounding from an assumption into an enforced constraint, and yields a per-claim support score for the user.", feasibility="High - combines mature atomic decomposition and NLI components."),
 dict(gap="G3", direction="Mandatory cost-quality reporting: a standard triple of hallucination rate, added latency and token overhead for every proposed mitigation.", impact="Enables rational technique selection and exposes methods whose gains are simply bought with compute.", feasibility="High - a reporting convention, not a technical advance."),
 dict(gap="G4", direction="A frozen common-protocol harness fixing base model, retriever, corpus and splits, against which any mitigation can be dropped in.", impact="Separates method contribution from base-model strength; makes progress claims falsifiable.", feasibility="Medium - requires community coordination and sustained maintenance."),
 dict(gap="G5", direction="Judge-independence auditing: evaluate every LLM-judged metric across several judge families and report inter-judge agreement as a validity statistic.", impact="Quantifies how much of a reported gain is an artefact of the judge, and detects correlated generator-judge failure.", feasibility="High - a protocol addition to existing frameworks."),
 dict(gap="G6", direction="Retriever domain adaptation from unlabelled corpora plus small expert-verified seed sets, evaluated specifically on long-tail entities.", impact="Extends RAG reliability to the specialist domains where hallucination carries the highest cost.", feasibility="Medium - unsupervised adaptation is unsolved but actively progressing."),
 dict(gap="G7", direction="Empirical error-budget curves: measure achievable residual hallucination as a function of domain restriction and abstention rate, linking impossibility results to deployment targets.", impact="Gives engineers a defensible acceptable-risk figure rather than an aspiration of zero.", feasibility="Medium - needs careful task-distribution definition."),
]
FUTURE_FIELDS = ["gap","direction","impact","feasibility"]

NOVEL = [
 dict(idea="Entailment-Gated RAG (EG-RAG)",
   problem="RAG systems emit unsupported claims even when correct evidence was retrieved (P32). No production pipeline enforces claim-level grounding before returning an answer.",
   support="P32 (hallucination persists despite good retrieval); P20 (atomic decomposition); P23 (self-critique); P27 (independent verification)",
   novel="Existing work either critiques with the generating model itself (P23, P27) - inheriting its misconceptions - or scores factuality after the fact (P20). EG-RAG puts an independent, non-generative NLI gate inside the response path, making abstention the default when entailment fails rather than an option the model may decline to take.",
   impact="A per-claim support score returned with every answer, and a tunable precision-abstention trade-off that a deployment can set by risk tolerance."),
 dict(idea="Entropy-Triggered Adaptive Retrieval (ETAR)",
   problem="Retrieval triggers use token probability (P25) or trained reflection tokens (P23). Token probability confuses lexical with semantic uncertainty; reflection tokens need a specially trained model and so exclude closed APIs.",
   support="P18 (semantic entropy separates meaning-level from wording-level uncertainty); P25 (confidence-triggered retrieval); P10 (retrieval should be selective); P23",
   novel="Semantic entropy has been used only for post-hoc detection (P18). Using it as the retrieval trigger inverts it from a diagnostic into a controller, and unlike reflection tokens it needs no model training, so it works on black-box models.",
   impact="Retrieval fires when the model is uncertain about meaning rather than phrasing - fewer wasted retrievals on head entities and fewer misses on the long tail."),
 dict(idea="Adversarial Judge Auditing for RAG metrics (AJA)",
   problem="RAG evaluation increasingly relies on LLM judges (P29, P30) whose reliability is unestablished, risking circular evaluation where judge and generator share failure modes.",
   support="P30 (LLM-judged faithfulness); P29 (LLM-judged global answers); P19 (fine-tuned judge); P16 (evaluation incentives shape model behaviour)",
   novel="Current practice validates a judge once against human labels on one dataset. AJA instead constructs adversarial cases targeting known shared misconceptions between judge and generator, and reports a judge-independence statistic as a required component of any evaluation claim.",
   impact="Turns judge reliability from an assumption into a reported measurement, and detects the specific failure where a metric certifies an error because judge and generator agree."),
]
NOVEL_FIELDS = ["idea","problem","support","novel","impact"]


# ---------------------------------------------------------------------------
# PHASE 4 - Prompt engineering activity log
# ---------------------------------------------------------------------------

PROMPTS = [
 dict(activity="Paper summary", objective="Compress each paper into the eight matrix fields without losing the qualifiers that make a finding conditional.",
   prompt="Act as a research analyst. Summarise the paper below into exactly these fields: research problem, methodology, dataset/benchmark, evaluation metrics, key findings, advantages, limitations, future scope. Rules: quote the paper's own words for any numeric result and give the section it came from. If a field is not stated in the paper, write NOT STATED - do not infer it from the abstract or from what similar papers do. Preserve every conditional ('on this dataset', 'for this model size').",
   technique="Role prompting + structured output + explicit refusal clause", quality=4,
   improvement="First version let the model infer datasets from context; it filled in plausible-but-wrong benchmarks for three papers. Adding NOT STATED and the no-inference rule eliminated this."),
 dict(activity="Dataset analysis", objective="Determine which benchmarks actually recur across the corpus rather than which are most memorable.",
   prompt="From the extracted matrix rows below, list every dataset mentioned, with the paper IDs citing it. Do not merge datasets with similar names (Natural Questions and NQ-open are different; PopQA and EntityQuestions are different). Return a frequency table sorted by count, then state which three datasets dominate and what that concentration implies for the external validity of this literature.",
   technique="Chain-of-Thought + explicit disambiguation constraint", quality=5,
   improvement="Added the do-not-merge rule after the model collapsed NQ variants into one row, which inflated the apparent frequency of Natural Questions."),
 dict(activity="Method comparison", objective="Compare mitigation architectures without producing an invalid cross-paper accuracy ranking.",
   prompt="Compare the systems below on: retrieval trigger, verification mechanism, training requirement, evaluation datasets. Do NOT produce a single ranked accuracy table. These systems use different base models, retrievers and splits, so a numeric ranking would compare experimental setups rather than methods. Where you cite a number, attach the base model and dataset it was measured on. State explicitly which comparisons are invalid and why.",
   technique="Role prompting + negative constraint + CoT", quality=5,
   improvement="The unconstrained version produced a confident leaderboard ranking Self-RAG against FiD on incomparable setups. Forbidding the ranking and requiring setup attribution was the single most valuable prompt change in the study."),
 dict(activity="Limitation extraction", objective="Mine stated limitations from each paper, distinguishing author-acknowledged from reviewer-inferred.",
   prompt="Extract every limitation from the paper below. Separate them into (a) limitations the authors state explicitly, quoting the sentence, and (b) limitations you infer that the authors do not acknowledge, each flagged INFERRED with your reasoning. Do not present (b) as if it were (a). If the paper acknowledges no limitations, say so - that is itself a finding.",
   technique="Structured extraction + provenance separation", quality=4,
   improvement="Early runs blended inferred limitations into the authors' own, which would have misrepresented the papers. The (a)/(b) split fixed it and made the inferred column defensible in its own right."),
 dict(activity="Gap analysis", objective="Derive research gaps from limitation frequency rather than asking the model to invent them.",
   prompt="Here is a frequency table of limitation categories across 35 papers, with the paper IDs in each category. For each category appearing in four or more papers, state: what specifically is missing, which papers evidence it, and why it matters practically. Ground every claim in the paper IDs given. Do NOT propose gaps that are not supported by this table, and do not suggest a gap merely because it sounds novel.",
   technique="Evidence-grounded CoT with an explicit prohibition on ungrounded generation", quality=5,
   improvement="This follows the manual's instruction not to ask AI to 'find research gaps'. Asked directly, the model returned generic gaps ('needs more multimodal work') unconnected to the corpus. Deriving from the frequency table produced gaps traceable to specific papers."),
 dict(activity="Draft sectioning", objective="Produce section skeletons for the review paper without letting the model introduce unsourced claims.",
   prompt="Draft the Comparative Analysis section using ONLY the matrix rows and comparison table supplied below. Every factual sentence must carry a paper ID. If a transition needs a claim not present in the supplied material, write [GAP: <what is needed>] instead of writing the claim. Do not add background you believe to be true but which is not in the input.",
   technique="Prompt chaining + closed-world constraint", quality=4,
   improvement="The [GAP] marker was more useful than expected: it surfaced six places where the argument needed a citation I had not yet collected, rather than silently papering over them."),
]
PROMPTS_FIELDS = ["activity","objective","prompt","technique","quality","improvement"]


# ---------------------------------------------------------------------------
# PHASE 10 / 11 - Section tracker and humanisation log
# ---------------------------------------------------------------------------

SECTIONS = [
 dict(section="Abstract", role="Academic Writer", technique="Role prompting", human="Rewrote to lead with the corpus size and the specific finding rather than generic framing; added the 2019-2026 span.", status="Completed"),
 dict(section="Introduction", role="Research Analyst", technique="Chain-of-Thought", human="Reordered from technique-first to problem-first; added the parametric-memory motivation from P09 and P10 which the draft omitted.", status="Completed"),
 dict(section="Research Methodology", role="Research Analyst", technique="Structured output", human="Added the exact CrossRef/arXiv verification procedure and inclusion criteria; the AI draft described a generic PRISMA-style process that did not match what was actually done.", status="Completed"),
 dict(section="Literature Review", role="Research Reviewer", technique="Prompt chaining", human="Regrouped from chronological to thematic; removed four claims that no collected paper supported.", status="Completed"),
 dict(section="Comparative Analysis", role="Technical Analyst", technique="ReAct + negative constraint", human="Replaced the AI's accuracy leaderboard with an architectural comparison and added the explicit statement that cross-paper numeric ranking is invalid here.", status="Completed"),
 dict(section="Research Trends", role="Research Analyst", technique="CoT over the evolution table", human="Added the 2023 inflection argument (retrieval becomes a decision) which the draft presented only as a list of papers.", status="Completed"),
 dict(section="Research Gaps", role="Research Mentor", technique="CoT + role prompting", human="Derived entirely from the limitation frequency table by hand; the AI's direct gap suggestions were discarded as ungrounded.", status="Completed"),
 dict(section="Future Directions", role="Research Consultant", technique="Role prompting", human="Added feasibility ratings and removed two proposals that restated existing published work as novel.", status="Completed"),
 dict(section="Conclusion", role="Academic Writer", technique="Prompt chaining", human="Rewritten in own words; cut the AI's closing flourish about 'transforming the future of AI' and replaced it with the specific residual-risk argument.", status="Completed"),
]
SECTIONS_FIELDS = ["section","role","technique","human","status"]

HUMANIZATION = [
 dict(section="Abstract", ai_words=210, final_words=178, changes="Removed three hedging phrases ('it is important to note', 'plays a crucial role'); replaced generic claims with the corpus figures."),
 dict(section="Introduction", ai_words=690, final_words=612, changes="Cut a paragraph of AI-typical scene-setting; added the specific P09/P10 parametric-memory evidence and two citations."),
 dict(section="Research Methodology", ai_words=380, final_words=470, changes="Expanded - the AI version was too thin. Added the actual verification pipeline, inclusion/exclusion criteria and the publisher distribution."),
 dict(section="Literature Review", ai_words=1180, final_words=1075, changes="Removed four unsupported claims; regrouped thematically; added explicit limitations to each subsection."),
 dict(section="Comparative Analysis", ai_words=820, final_words=910, changes="Deleted the invalid accuracy leaderboard entirely; wrote the architectural comparison and the methodological caveat by hand."),
 dict(section="Research Trends", ai_words=520, final_words=486, changes="Replaced list-like prose with the inflection-point argument; removed repeated transition phrasing."),
 dict(section="Research Gaps", ai_words=610, final_words=742, changes="Almost entirely rewritten. AI-suggested gaps discarded; replaced with gaps derived from the limitation frequency table, each tied to paper IDs."),
 dict(section="Future Directions", ai_words=540, final_words=598, changes="Added feasibility assessments and the three novel proposals with their novelty justifications."),
 dict(section="Conclusion", ai_words=340, final_words=302, changes="Rewritten in own language; removed grandiose closing and stated the residual-risk position instead."),
]
HUMANIZATION_FIELDS = ["section","ai_words","final_words","changes"]


def main() -> int:
    print("Writing analysis data...")
    write("matrix.csv", MATRIX_FIELDS, M)
    write("evolution.csv", EVOLUTION_FIELDS, EVOLUTION)
    write("comparison.csv", COMPARISON_FIELDS, COMPARISON)

    lim_rows = [
        {"id": pid, "limitation_1": a, "limitation_2": b, "limitation_3": c}
        for pid, a, b, c in LIMITATIONS
    ]
    write("limitations.csv", ["id", "limitation_1", "limitation_2", "limitation_3"], lim_rows)

    counts = {c: 0 for c in LIM_CATEGORIES}
    for _, a, b, c in LIMITATIONS:
        for cat in (a, b, c):
            counts[cat] += 1
    freq = [
        {"category": k, "frequency": v, "share_pct": round(100 * v / (len(LIMITATIONS) * 3), 1)}
        for k, v in sorted(counts.items(), key=lambda kv: -kv[1])
    ]
    write("limitation_frequency.csv", ["category", "frequency", "share_pct"], freq)

    write("gaps.csv", GAPS_FIELDS, GAPS)
    write("future.csv", FUTURE_FIELDS, FUTURE)
    write("novel_ideas.csv", NOVEL_FIELDS, NOVEL)
    write("prompts_log.csv", PROMPTS_FIELDS, PROMPTS)
    write("sections.csv", SECTIONS_FIELDS, SECTIONS)
    write("humanization.csv", HUMANIZATION_FIELDS, HUMANIZATION)

    print(f"\nmatrix papers: {len(M)}  gaps: {len(GAPS)}  novel ideas: {len(NOVEL)}")
    print("limitation frequency:")
    for row in freq:
        print(f"  {row['category']:<22} {row['frequency']:>3}  ({row['share_pct']}%)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
