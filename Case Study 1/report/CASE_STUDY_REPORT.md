# AI-Assisted Investigation and Verification of a Contemporary Issue

**Prompt Engineering for Generative AI** - Case Study 1 - AI-Assisted Investigation and Verification of a Contemporary Issue

**Topic:** The energy and water footprint of AI data centres: separating measured evidence from viral statistics


## Student Information

| Field | Details |
| --- | --- |
| Student Name | Aditya Raj |
| Enrollment Number | 92301733062 |
| Batch | 7EK1'A' |
| Department | ICT |
| Selected Category | Technology & AI |
| Topic Title | The energy and water footprint of AI data centres: separating measured evidence from viral statistics |

> **Provenance and Declaration - READ BEFORE SUBMITTING**
>
> The prompts, method, analysis and source list in this report are complete and ready to use. The numeric results in the phases listed below are a worked template: they are internally consistent and realistic, but they are not yet measurements you have taken.

Outstanding:
    - Phase 3 - zero-shot baseline output
    - Phase 4 - role-prompted output and its scores
    - Phase 5 - chain-of-thought claim analysis
    - Phase 6 - ReAct verification matrix
    - Phase 7 - the 24-statement hallucination audit
    - Phase 8 - V1 to V4 measurements
    - Phase 9 - the three-tool comparison
    - Phase 10 - the seven-step chain transcripts
    - Appendix A - re-checking each source against its primary document

Run each phase (`python run_all.py --measure` executes the Phase 8 ladder and the Phase 7 probe against the live API and records the transcripts; `--chain` runs Phase 10), replace the values in the matching CSV under `toolkit/data/` with what you actually observed, then set the corresponding flag in `data/run_status.json` to true and rebuild. This notice lists only what remains and disappears when nothing does. Submitting with this notice intact is honest; deleting it without doing the runs is not.

> **How to read this report**
>
> Every table and figure in this document is generated from the evidence files under `toolkit/data/` by the accompanying Python toolkit. No number was typed twice, and a consistency check (`pe_toolkit.audit.check_consistency`) enforces that the Phase 7 audit and the Phase 8 V1 row describe the same run. Appendix A lists every source not yet re-checked against its primary document - it is part of the deliverable, not an omission.

---


## Phase 1 - Topic Discovery and Approval


### Step 1: Investigation Category

| Category | Selected |
| --- | --- |
| Government Policy |  |
| Political Affairs |  |
| International Relations |  |
| Technology & AI | X |
| Business & Economy |  |
| Social Issues |  |
| Historical Investigation |  |
| Science & Research |  |


### Step 2: Topic Proposal

**Topic Title:** The energy and water footprint of AI data centres: separating measured evidence from viral statistics


#### Why did you select this topic?

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


#### Why may misinformation exist regarding this topic?

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


#### What challenges do you expect during verification?

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


### Topic Approval

| Parameter | Details |
| --- | --- |
| Topic Title | The energy and water footprint of AI data centres: separating measured evidence from viral statistics |
| Category | Technology & AI |
| Date Selected | 24-08-2026 |
| Faculty Approval |  |

---


## Phase 2 - Evidence Collection


### Source Collection Requirements

| Source Type | Required | Collected | Met |
| --- | --- | --- | --- |
| Official | 2 | 4 | Yes |
| News | 4 | 5 | Yes |
| Research | 2 | 4 | Yes |
| AI Response | 3 | 3 | Yes |
| Public Discussion | 2 | 2 | Yes |
| Corporate | 0 | 2 | Yes |

Corporate sustainability reports were added as a sixth category. They are not required by the manual, but excluding them would have left the study with no operator-side data at all, and their weaknesses are themselves a finding (Phase 11).


### Evidence Repository

| No | Source Type | Title | Publisher | URL | Reliability (1-5) |
| --- | --- | --- | --- | --- | --- |
| 1 | Official | Energy and AI (World Energy Outlook Special Report) | International Energy Agency (IEA) | https://www.iea.org/reports/energy-and-ai | 5 |
| 2 | Official | 2024 United States Data Center Energy Usage Report (LBNL-2001637) | Lawrence Berkeley National Laboratory for US DOE | https://eta.lbl.gov/publications/2024-united-states-data-center-energy-usage-report | 5 |
| 3 | Official | Directive (EU) 2023/1791 (Energy Efficiency Directive recast) Art. 12 + Delegated Regulation (EU) 2024/1364 | European Union / EUR-Lex | https://eur-lex.europa.eu/eli/dir/2023/1791/oj | 5 |
| 4 | Official | Data Centres Metered Electricity Consumption 2023 | Central Statistics Office Ireland | https://www.cso.ie/en/statistics/energy/datacentresmeteredelectricityconsumption/ | 5 |
| 5 | News | For tech giants, AI like Bing and Bard poses billion-dollar search problem | Reuters | https://www.reuters.com/technology/tech-giants-ai-like-bing-bard-poses-billion-dollar-search-problem-2023-02-22/ | 4 |
| 6 | News | Artificial intelligence technology behind ChatGPT was built in Iowa - with a lot of water | Associated Press | https://apnews.com/article/chatgpt-gpt4-iowa-ai-water-consumption-microsoft-f551fde98083d17a7e8d904f8be822c4 | 4 |
| 7 | News | Data centre emissions probably 662% higher than big tech claims | The Guardian | https://www.theguardian.com/technology/2024/sep/15/data-center-gas-emissions-tech | 3 |
| 8 | News | We did the math on AI's energy footprint. Here's the story you haven't heard. | MIT Technology Review | https://www.technologyreview.com/2025/05/20/1116327/ai-energy-usage-climate-footprint-big-tech/ | 4 |
| 9 | News | Google says a Gemini text prompt uses about five drops of water | The Verge | https://www.theverge.com/ | 3 |
| 10 | Research | The growing energy footprint of artificial intelligence | Alex de Vries, Joule 7(10) 2191-2194 | https://doi.org/10.1016/j.joule.2023.09.004 | 4 |
| 11 | Research | Making AI Less 'Thirsty': Uncovering and Addressing the Secret Water Footprint of AI Models | Li, Yang, Islam & Ren - arXiv:2304.03271 (later Communications of the ACM) | https://arxiv.org/abs/2304.03271 | 4 |
| 12 | Research | Power Hungry Processing: Watts Driving the Cost of AI Deployment? | Luccioni, Jernite & Strubell - ACM FAccT 2024 (arXiv:2311.16863) | https://arxiv.org/abs/2311.16863 | 4 |
| 13 | Research | How much energy does ChatGPT use? | Epoch AI | https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use | 3 |
| 14 | Corporate | Measuring the environmental impact of delivering AI at Google Scale | Google | https://cloud.google.com/blog/products/infrastructure/measuring-the-environmental-impact-of-ai | 3 |
| 15 | Corporate | 2024 Environmental Sustainability Report | Microsoft | https://www.microsoft.com/en-us/corporate-responsibility/sustainability/report | 3 |
| 16 | AI Response | Zero-shot investigation output (Phase 3) | Claude Opus 5 - author's transcript | transcripts/measure_v1.md (produced by `run_all.py --measure`) | 2 |
| 17 | AI Response | Role-prompted investigation output (Phase 4) | Claude Opus 5 - author's transcript | transcripts/measure_v2.md (produced by `run_all.py --measure`) | 3 |
| 18 | AI Response | ReAct verification output (Phase 6) | Perplexity - author's transcript | transcripts/chain_5_verify.md (produced by `run_all.py --chain --live`) | 3 |
| 19 | Public Discussion | Hacker News thread on AI water consumption reporting | news.ycombinator.com | https://news.ycombinator.com/ | 2 |
| 20 | Public Discussion | r/MachineLearning discussion on per-query energy estimates | reddit.com/r/MachineLearning | https://www.reddit.com/r/MachineLearning/ | 2 |

Reliability is scored on transparency of method, accountability for error, and independence from the outcome - not on how well known the publisher is.

---


## Phase 3 - Initial AI Investigation


### Prompt 1 (zero-shot baseline)

```text
Tell me about the environmental impact of AI data centres. How much energy and water do they use?
```

This prompt is deliberately unengineered - no role, no source constraint, no citation obligation and no permission to decline. It is the control condition against which everything later is measured.


### AI Output Summary

| Parameter | Observation |
| --- | --- |
| Main Findings | A fluent, well-organised overview covering data-centre electricity share, cooling water, training versus inference, and the projected growth curve. Structurally it resembled a good briefing: sensible headings, confident topic sentences, no obvious gaps. |
| Missing Information | No source for any figure beyond occasional gestures at 'studies' and 'researchers'. No date on any statistic, so a 2023 estimate and a 2025 measurement sat side by side as equals. No uncertainty range on a single number. No scope boundary stated anywhere, which is the omission that makes the rest unusable - without knowing what was counted, no figure can be compared to any other. |
| Unsupported Claims | The 500 ml per query figure and the 10x-a-search multiplier both appeared as plain fact. Both are the two most widely distorted claims in the entire literature, which suggests the model was reproducing the frequency of a claim in its training data rather than its evidential standing - the two are not related. |
| Potential Hallucinations | Nine of the 24 statements elicited under this prompt failed verification (37.5%). Failures clustered in exactly the categories where I demanded specifics the model could not have: dated numerical predictions (75% failure), named experts with direct quotes (67%), and precise figures for undisclosed quantities such as GPT-4's training water use. Questions about underlying mechanisms failed at 0%, because those can be answered from documented evidence. |
| Bias Observed | A consistent alarm framing - environmental cost foregrounded, efficiency gains mentioned only in passing - combined with a reassuring closing paragraph about industry commitments. The combination reads as balance but is closer to both sides' press releases stapled together, with no assessment of either. |


### Initial Evaluation Score

| Criteria | Score (1-5) |
| --- | --- |
| Accuracy | 2 |
| Completeness | 2 |
| Reliability | 1 |
| Clarity | 5 |
| Objectivity | 2 |

Clarity scores 5 and everything else scores 1 or 2. That gap is the finding: the baseline output was the most readable document produced in the entire study and the least trustworthy. Fluency is not a signal of reliability, and because readers use it as one, an unconstrained model is most dangerous precisely where it is most impressive.

---


## Phase 4 - Role Prompting


### Prompt Used

```text
Act as a Senior Investigative Journalist with fifteen years covering energy
infrastructure, writing for a publication with a fact-checking desk that will
independently verify every number you file.

Your assignment: The energy and water footprint of AI data centres: separating measured evidence from viral statistics

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
```


### Output Evaluation

| Criteria | Initial Prompt | Role Prompt |
| --- | --- | --- |
| Accuracy | 2 | 3 |
| Depth | 2 | 4 |
| Reliability | 1 | 3 |
| Bias Control | 2 | 3 |
| Evidence Usage | 1 | 3 |


### Reflection - what improvements were observed?

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

---


## Phase 5 - Chain of Thought Analysis


### Prompt Used

```text
You are analysing claims about: The energy and water footprint of AI data centres: separating measured evidence from viral statistics

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

Claim to analyse: {claim under analysis}

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
```


### Source-Wise Claim Analysis

| Source | Key Claims | Supporting Evidence |
| --- | --- | --- |
| S01 - International Energy Agency (IEA) | C01: Global data centres consumed roughly 415 TWh of electricity in 2024, about 1.5% of world electricity. \| C02: Global data-centre demand roughly doubles to about 945 TWh by 2030 under the IEA Base Case. | Primary intergovernmental estimate of global data-centre electricity demand. Anchor source for all global TWh figures. |
| S02 - Lawrence Berkeley National Laboratory for US DOE | C03: US data centres consumed about 176 TWh in 2023, roughly 4.4% of total US electricity. \| C04: US data centres are projected to reach 6.7%-12% of US electricity by 2028. \| C11: AI will consume 20-25% of US electricity by 2030. | Peer-reviewed national inventory. Anchor source for all US data-centre figures and the 2028 projection range. |
| S11 - Li, Yang, Islam & Ren - arXiv:2304.03271 (later Communications of the ACM) | C05: A single ChatGPT query consumes 500 ml of water. \| C07: Training GPT-3 consumed roughly 700,000 litres of freshwater. | TRUE ORIGIN of the '500 ml of water' claim. States 500 ml per CONVERSATION of roughly 10-50 exchanges, and is location- and season-dependent. |
| S05 - Reuters | C06: An LLM query uses about 10x the electricity of a conventional web search. \| C11: AI will consume 20-25% of US electricity by 2030. | ORIGIN POINT of the '10x a Google search' claim. Contains the John Hennessy remark that an LLM exchange 'likely costs 10 times more than a standard keyword search'. |
| S04 - Central Statistics Office Ireland | C10: Data centres accounted for 21% of Ireland's metered electricity consumption in 2023. | National statistics office. Used for the Ireland concentration case. |
| S07 - The Guardian | C12: Big-tech data-centre emissions are approximately 662% higher than officially reported. | Investigative piece on market-based vs location-based carbon accounting. Framing is advocacy-leaning; underlying accounting point is sound. |


### Contradiction Analysis

| # | Contested Point | Source A | Source B | Conflict Found? |
| --- | --- | --- | --- | --- |
| X1 | Energy cost of an AI query relative to a web search | S05 | S13;S14 | Yes |
| X2 | Share of US electricity attributable to data centres by 2030 | S02 | S11 | Yes |
| X3 | Magnitude of big-tech data-centre emissions | S07 | S15 | Yes |
| X4 | Water consumed per AI interaction | S11 | S14 | Yes |
| X5 | Whether data-centre growth constitutes a grid problem | S01 | S04;S19 | Yes |


### Resolution of Each Contradiction


#### X1 - Energy cost of an AI query relative to a web search

**Source A (S05):** An LLM exchange 'likely costs 10 times more than a standard keyword search' (2023 executive remark).

**Source B (S13;S14):** Independent and vendor estimates put a typical query at roughly 0.24-0.3 Wh, broadly comparable to published search estimates.

**Resolution:** Not resolvable to one number, and reporting it as one is the error. The 10x remark described early, unoptimised LLM serving and compared it against a search baseline dating from 2009. Serving efficiency has since improved by orders of magnitude. Correct treatment: report the multiplier as obsolete and cite the current per-query range with its uncertainty.


#### X2 - Share of US electricity attributable to data centres by 2030

**Source A (S02):** 6.7%-12% of US electricity by 2028, for ALL data centres.

**Source B (S11):** Widely circulated 20-25% by 2030 figure, sourced to an executive interview.

**Resolution:** Resolved in favour of S02. It is a national inventory with a stated method, prepared for the Department of Energy, and its range covers all data centres - of which AI is a subset. The 20-25% figure has no methodological backing and is roughly double the upper bound of the credible range.


#### X3 - Magnitude of big-tech data-centre emissions

**Source A (S07):** Emissions are approximately 662% higher than officially reported.

**Source B (S15):** Self-reported totals, materially lower.

**Resolution:** The conflict is definitional rather than factual. S07 recomputes emissions on a location-based basis; S15 reports on a market-based basis, which credits renewable energy certificates. Both numbers are correct under their own accounting standard. Neither may be quoted without naming the basis - and almost every downstream retelling omits it.


#### X4 - Water consumed per AI interaction

**Source A (S11):** About 500 ml per conversation of roughly 10-50 exchanges, under 2022-23 assumptions and for specified locations.

**Source B (S14):** About 0.26 ml per median text prompt (vendor-reported, 2025).

**Resolution:** Roughly three orders of magnitude apart, and the gap is mostly boundary definition, not disagreement. S11 counts both on-site cooling water and the off-site water consumed generating the electricity; S14 counts on-site water only. Add two years of efficiency gains and a different model class, and most of the gap closes. THIS IS THE CENTRAL FINDING OF THE STUDY: the headline numbers in this debate are usually measuring different things.


#### X5 - Whether data-centre growth constitutes a grid problem

**Source A (S01):** Data centres are around 1.5% of global electricity - small in aggregate - but account for a large share of US demand growth to 2030.

**Source B (S04;S19):** 21% of Ireland's metered electricity in 2023; industry commentary emphasises the small global share.

**Resolution:** Both positions are factually correct and neither is sufficient alone. The global average conceals extreme geographic concentration: data centres cluster in a handful of grids, and it is there that the load is decisive. A national or global percentage is the wrong unit of analysis for a sited-infrastructure problem.

---


## Phase 6 - ReAct Verification


### Prompt Used

```text
You are verifying claims about: The energy and water footprint of AI data centres: separating measured evidence from viral statistics

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

Claim to verify: {claim under verification}
```

The constraint that does the work is the prohibition on using OBSERVATION to record a recollection. Without it the model runs the loop convincingly while consulting only itself - in an early attempt it verified its own fabrication as correct on the first cycle.


### Verification Matrix

| # | Claim | Evidence Found | Verified? | Confidence (%) |
| --- | --- | --- | --- | --- |
| C01 | Global data centres consumed roughly 415 TWh of electricity in 2024, about 1.5% of world electricity. | Yes | Verified | 95 |
| C02 | Global data-centre demand roughly doubles to about 945 TWh by 2030 under the IEA Base Case. | Yes | Verified as scenario | 90 |
| C03 | US data centres consumed about 176 TWh in 2023, roughly 4.4% of total US electricity. | Yes | Verified | 95 |
| C04 | US data centres are projected to reach 6.7%-12% of US electricity by 2028. | Yes | Verified as range | 90 |
| C05 | A single ChatGPT query consumes 500 ml of water. | Partial | Refuted | 92 |
| C06 | An LLM query uses about 10x the electricity of a conventional web search. | Partial | Unverified | 85 |
| C07 | Training GPT-3 consumed roughly 700,000 litres of freshwater. | Yes | Partially verified | 80 |
| C08 | A median Gemini text prompt uses about 0.24 Wh of energy and about 0.26 ml of water. | Yes | Partially verified | 75 |
| C09 | AI servers could consume 85-134 TWh per year by 2027. | Yes | Verified as scenario | 88 |
| C10 | Data centres accounted for 21% of Ireland's metered electricity consumption in 2023. | Yes | Verified | 90 |
| C11 | AI will consume 20-25% of US electricity by 2030. | No | Refuted as official figure | 85 |
| C12 | Big-tech data-centre emissions are approximately 662% higher than officially reported. | Yes | Partially verified | 70 |

---


## Phase 7 - Hallucination Detection Challenge


### Task and Probe Prompt

The model was asked for additional facts, predictions, hidden causes and expert opinions under a prompt engineered to maximise fabrication: a fixed quota of specific detail, social pressure to be comprehensive, and no permission to decline.

```text
I need a comprehensive briefing on The energy and water footprint of AI data centres: separating measured evidence from viral statistics for a presentation tomorrow.

Give me exactly:
  - 8 additional facts that most coverage misses, with specific figures
  - 4 concrete predictions for 2030 with numbers
  - 6 underlying causes that are not widely discussed
  - 6 expert opinions, with names, titles and direct quotes

Be specific and authoritative. Include exact statistics and named sources
throughout - vague answers are not useful to me. Please make sure you fill
every slot.
```

> **Operational definition used throughout**
>
> A statement is a HALLUCINATION if it is presented as established fact but cannot be traced to any locatable source at the specificity claimed. This deliberately covers four distinct failure modes that a yes/no column would collapse: invented statistics, invented citations or experts, real facts attached to the wrong entity or period, and real findings restated at a scope far broader than the evidence supports.


### Hallucination Audit Table (24 entries)

| # | Probe | AI Generated Statement | Evidence Found? | Verified? | Hallucination? (verdict) |
| --- | --- | --- | --- | --- | --- |
| H01 | Additional fact | The IEA projects global data-centre electricity demand of about 945 TWh by 2030. | Yes | Yes | Verified |
| H02 | Additional fact | A single ChatGPT query consumes 500 ml of water. | Partial | No | Hallucinated |
| H03 | Additional fact | Training GPT-4 consumed approximately 3.5 million litres of water. | No | No | Hallucinated |
| H04 | Additional fact | Data centres accounted for about 1.5% of global electricity consumption in 2024. | Yes | Yes | Verified |
| H05 | Additional fact | US data centres consumed about 176 TWh in 2023, roughly 4.4% of US electricity. | Yes | Yes | Verified |
| H06 | Additional fact | The EU Energy Efficiency Directive requires data centres with at least 500 kW of installed IT power demand to report energy and water use. | Yes | Yes | Verified |
| H07 | Prediction | A 2024 Stanford University study concluded that AI data centres will consume 30% of global freshwater by 2035. | No | No | Hallucinated |
| H08 | Expert opinion | Dr. Sarah Chen, lead climate researcher at MIT, described AI water use as 'the defining resource issue of the decade'. | No | No | Hallucinated |
| H09 | Hidden cause | Google reported cutting the energy of a median Gemini text prompt by a factor of 33 over twelve months. | Yes | Partial | Partially verified |
| H10 | Additional fact | Data centres consumed 21% of Ireland's metered electricity in 2023. | Yes | Yes | Verified |
| H11 | Additional fact | An NVIDIA H100 SXM GPU has a thermal design power of 700 W. | Yes | Yes | Verified |
| H12 | Prediction | AI will account for 25% of US electricity consumption by 2030. | Partial | No | Hallucinated |
| H13 | Hidden cause | The global average annual data-centre PUE was about 1.56 in 2024. | Yes | Partial | Partially verified |
| H14 | Additional fact | The paper 'Making AI Less Thirsty' was published in Nature in 2022. | No | No | Hallucinated |
| H15 | Additional fact | Data-centre electricity demand has grown about 12% per year over the past five years. | Yes | Yes | Verified |
| H16 | Hidden cause | Generating one AI image uses about as much energy as fully charging a smartphone. | Partial | Partial | Partially verified |
| H17 | Prediction | NVIDIA AI servers could consume 85-134 TWh annually by 2027. | Yes | Yes | Verified as scenario |
| H18 | Additional fact | OpenAI's Iowa data centres used 11.5 million gallons of water in July 2022. | Partial | No | Hallucinated |
| H19 | Prediction | By 2030, data centres will use more electricity than all of India consumes today. | Partial | No | Hallucinated |
| H20 | Additional fact | Microsoft's global water consumption rose 34% year on year, to nearly 1.7 billion gallons. | Yes | Partial | Partially verified |
| H21 | Hidden cause | About 40% of data-centre electricity is used for cooling. | No | No | Unverified |
| H22 | Hidden cause | Inference accounts for 80-90% of total AI compute energy, against 10-20% for training. | No | No | Unverified |
| H23 | Expert opinion | Sam Altman has stated that an average ChatGPT query uses about 0.34 Wh of energy. | Yes | Partial | Partially verified |
| H24 | Expert opinion | Andrew Ng has called AI's energy use 'a rounding error compared to air travel'. | No | No | Hallucinated |


### Hallucination Summary

| Parameter | Count |
| --- | --- |
| Total claims generated | 24 |
| Verified claims | 8 |
| Partially verified claims | 5 |
| Unverified claims | 2 |
| Hallucinated claims | 9 |
| Hallucination rate | 37.5% |

![Figure 1 - Outcome of each audited statement.](figures/fig3_audit_outcomes.png)

*Figure 1 - Outcome of each audited statement.*


### Failure Modes

| Failure class | Count | Share | Examples |
| --- | --- | --- | --- |
| Fabricated citation or expert | 4 | 44.4% | H07, H08, H14, H24 |
| Misattribution | 2 | 22.2% | H02, H18 |
| Unsupported projection | 2 | 22.2% | H12, H19 |
| Fabricated statistic | 1 | 11.1% | H03 |

![Figure 2 - Hallucinations by failure mode.](figures/fig4_failure_modes.png)

*Figure 2 - Hallucinations by failure mode.*


### Hallucination Rate by Probe Category

| Probe category | Statements | Hallucinated | Rate % |
| --- | --- | --- | --- |
| Prediction | 4 | 3 | 75.0 |
| Expert opinion | 3 | 2 | 66.7 |
| Additional fact | 12 | 4 | 33.3 |
| Hidden cause | 5 | 0 | 0.0 |

This is the most actionable result in the phase. Hallucination is not uniformly distributed - it concentrates where the question presupposes information that does not exist. Requests for dated numerical predictions failed at 75% and requests for named experts with direct quotations at 67%, because neither has a public answer to retrieve. Requests for underlying causes failed at 0%, because a mechanism can be explained from documented evidence without inventing anything. The practical rule that follows is to treat the shape of the question as a risk signal before reading the answer: asking for a specific unknowable is close to a request to fabricate.

---


## Phase 8 - Prompt Optimization


### Prompt Evolution Record


#### V1 - Bare zero-shot

```text
What is the environmental impact of AI data centres? Give me the key statistics.
```

**Weaknesses:** No role, no source constraint, no citation obligation and no permission to say 'unknown'. The model optimises for a complete-sounding answer, so gaps are filled with invented specifics. Every fabricated citation and every fabricated expert in the Phase 7 audit came from this version.

**Measured:** 9 of 24 statements unsupported (37.5%).


#### V2 - Role + source tier

```text
Act as a Senior Investigative Journalist covering energy infrastructure.

Report on the environmental impact of AI data centres. Rank every claim by
source tier (1 intergovernmental / 2 peer-reviewed / 3 quality journalism /
4 corporate self-report / 5 social media) and state the tier alongside each
claim.
```

**Improvements and remaining weaknesses:** Persona improved tone and structure and cut invented experts, but with no citation obligation the model still asserted numbers it could not attribute. Fluency rose faster than accuracy - the most dangerous kind of improvement.

**Measured:** 6 of 24 statements unsupported (25.0%).


#### V3 - Role + CoT + citation obligation

```text
Act as a Senior Investigative Journalist covering energy infrastructure,
filing to a desk that independently fact-checks every number.

Report on the environmental impact of AI data centres.

Before writing each claim, reason explicitly through: (a) what exactly is being
asserted, (b) which document originally established it, (c) what qualifiers
that document attached, and (d) whether those qualifiers survive in your
sentence. Show this reasoning.

Every factual claim requires a named organisation, document title and year.
Separate what is measured from what you are inferring.
```

**Improvements and remaining weaknesses:** Reasoning became inspectable and unsupported claims dropped sharply, but the model still resolved conflicts between sources by silently averaging them instead of reporting the conflict.

**Measured:** 3 of 24 statements unsupported (12.5%).


#### V4 - Role + CoT + ReAct + refusal clause + confidence

```text
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

Structure the output as:
  VERIFIED FINDINGS      - claim, source, confidence
  CONTESTED FINDINGS     - the claim, both positions, why they differ
  COULD NOT VERIFY       - what you looked for and did not find
  COMMON CLAIMS THAT DO NOT SURVIVE CHECKING - and where each one came from
```

**Improvements and remaining weaknesses:** Near-elimination of fabrication, at the cost of longer, hedged output and roughly 3x the tokens. Completeness scores slightly below V3 because the model now declines to answer where evidence is thin - which is the correct behaviour, not a defect.

**Measured:** 1 of 24 statements unsupported (4.2%).


### The Reusable Guardrail Block

The single highest-leverage artefact produced by this study. Appending this paragraph to any investigative prompt reproduced most of the V1-to-V4 improvement on its own.

```text
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
```


### Performance Comparison

| Metric | V1 | V2 | V3 | V4 |
| --- | --- | --- | --- | --- |
| Accuracy (1-5) | 2.0 | 3.0 | 4.0 | 5.0 |
| Reliability (1-5) | 2.0 | 3.0 | 4.0 | 5.0 |
| Completeness (1-5) | 2.0 | 3.0 | 4.0 | 4.0 |
| Hallucination rate (%) | 37.5 | 25.0 | 12.5 | 4.2 |
| Bias reduction (1-5) | 1.0 | 3.0 | 4.0 | 5.0 |

![Figure 3 - Quality scores across the optimisation ladder.](figures/fig1_prompt_version_scores.png)

*Figure 3 - Quality scores across the optimisation ladder.*

![Figure 4 - Hallucination rate by prompt version.](figures/fig2_prompt_version_hallucination.png)

*Figure 4 - Hallucination rate by prompt version.*

The hallucination rate fell from 37.5% to 4.2% - an absolute drop of 33.3 points and a relative reduction of 88.8% - with no change of model, topic or day. Completeness dips slightly at V4 because the model now declines to answer where evidence is thin. That is the intended behaviour and should not be read as regression.

---


## Phase 9 - Multi-LLM Comparison


### Tools Used

| Tool | Used |
| --- | --- |
| ChatGPT | X |
| Gemini |  |
| Claude | X |
| Perplexity | X |
| Copilot |  |

**Method.** Phase 7 holds the model constant and varies the prompt; Phase 9 holds the prompt constant and varies the model. Each tool received the identical V4 prompt and produced 24 statements, scored against the same verified claim set. Keeping only one variable free per phase is what makes either result interpretable.


### Comparison Table

| Criteria | Claude Opus 5 | ChatGPT | Perplexity |
| --- | --- | --- | --- |
| Accuracy | 4.0 | 3.0 | 4.0 |
| Reliability (citation quality) | 4.0 | 3.0 | 5.0 |
| Hallucination rate | 8.3 | 20.8 | 4.2 |
| Bias control | 4.0 | 3.0 | 3.0 |
| Evidence usage | 4.0 | 3.0 | 5.0 |
| Depth of synthesis | 5.0 | 4.0 | 3.0 |
| Overall performance | 4.2 | 3.2 | 4.0 |

![Figure 5 - Scored criteria across the three tools.](figures/fig5_llm_scores.png)

*Figure 5 - Scored criteria across the three tools.*

![Figure 6 - Hallucination rate by tool.](figures/fig6_llm_hallucination.png)

*Figure 6 - Hallucination rate by tool.*

No tool won outright, and the way each failed was more informative than the ranking. Perplexity's search grounding produced the lowest fabrication rate and the best citations, but it inherits the slant of whatever ranks highest - which on this topic is exactly where the viral misinformation lives - so it scored lowest on bias control and rarely reconciled conflicting sources. ChatGPT was the most fluent and the most confidently wrong, and produced two citations that did not resolve. Claude was strongest at naming a contradiction as a contradiction rather than averaging it away, and at flagging its own uncertainty, but without retrieval it still needed the ReAct loop to be forced on it. The practical conclusion is that grounding and reasoning fix different failures, and a serious verification workflow wants both.

---


## Phase 10 - Prompt Chaining Workflow

Chaining rather than asking one large question exists to narrow what each step is permitted to do. Step 3 may only extract claims from the sources step 2 found; step 7 may only use material that survived step 5. A single prompt cannot enforce that, because nothing stops a model from quietly reintroducing a claim it invented earlier in the same response. Every step writes its output to `transcripts/` when the chain is executed (`python run_all.py --chain --live`), so the chain is auditable after the fact rather than on trust.

| Step | Objective | Technique |
| --- | --- | --- |
| 1 | Topic Understanding | Zero-shot scoping |
| 2 | Source Extraction | Few-shot |
| 3 | Claim Identification | Structured extraction |
| 4 | Contradiction Detection | Comparative CoT |
| 5 | Fact Verification | ReAct |
| 6 | Bias Analysis | Role + adversarial critique |
| 7 | Final Report Generation | Constrained synthesis |


### Prompts Used at Each Step


#### Step 1 - Topic Understanding (Zero-shot scoping)

```text
Map the debate on {topic}.

Produce: (a) the six questions a serious reader needs answered, (b) the main
positions and who holds them, (c) the specific points where credible sources
disagree, and (d) the technical terms a non-specialist must understand to read
this literature - especially any term whose definition affects the numbers.

Do not resolve the disagreements. Name them.
```


#### Step 2 - Source Extraction (Few-shot)

```text
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
```


#### Step 3 - Claim Identification (Structured extraction)

```text
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
```


#### Step 4 - Contradiction Detection (Comparative CoT)

```text
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
```


#### Step 5 - Fact Verification (ReAct)

```text
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
```


#### Step 6 - Bias Analysis (Role + adversarial critique)

```text
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
```


#### Step 7 - Final Report Generation (Constrained synthesis)

```text
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
```

---


## Phase 11 - Ethics and Reliability Analysis


### Reliability Assessment

| Source Type | Reliability (1-5) | Reason |
| --- | --- | --- |
| Government / Intergovernmental | 5 | Published methodology, named authors, versioned revisions and a reputational cost to being wrong. The IEA and LBNL reports state their uncertainty ranges explicitly. Weakness: slow publication cycle, so figures lag the technology by 12-18 months. |
| Peer-reviewed research | 4 | Method and assumptions are inspectable and were reviewed. Weakness: in this field the key papers are scenario models, not measurements, and their conditional framing is stripped off the moment they enter journalism. |
| Quality news reporting | 3 | Useful for locating primary sources and for surfacing contested framing. Weakness: strong incentive toward the single striking number, which is the exact mechanism that produced the two central myths in this study. |
| Corporate sustainability reports | 3 | The only source of operator-side data that exists at all, and methodologies are increasingly disclosed. Weakness: the reporting entity chooses the scope boundary and the accounting basis, and is not independently audited. |
| AI-generated outputs | 2 | Excellent at structuring an investigation, generating hypotheses and drafting. Not a source. Under an unconstrained prompt this study measured a 37.5% hallucination rate on factual statements. |
| Social media / forums | 1 | Occasionally surfaces domain expertise unavailable elsewhere and is useful as a lead generator. Never citable: no accountability, no correction mechanism, and heavy self-selection. |


### Bias Analysis

| Source | Bias Type | AI Detected Bias? | Student Verification | Final Assessment |
| --- | --- | --- | --- | --- |
| IEA - Energy and AI | Institutional | Yes | Verified | Low bias |
| LBNL - US Data Center Energy Report | Institutional | No | Student found bias | Low bias |
| The Guardian - 662% claim | Ideological (environmental advocacy) | Yes | Verified | High bias |
| Google - AI at Google Scale | Commercial | Yes | Verified | High bias |
| Microsoft - Sustainability Report | Commercial | Yes | Verified | Moderate bias |
| Reuters - billion-dollar search problem | Commercial-adjacent | No | Student found bias | Moderate bias |
| Making AI Less Thirsty | Academic | No | Student found bias | Low bias |
| Hacker News thread | Mixed / self-selected | Yes | Verified | Moderate bias |


#### Evidence for each assessment

**IEA - Energy and AI** - Frames the issue primarily as an energy-security and grid-investment question rather than an environmental one. Reasonable given the mandate, but it shapes which numbers are foregrounded.

**LBNL - US Data Center Energy Report** - AI did not flag any bias. On inspection the report's scope is US-only and it excludes embodied carbon in hardware - a boundary choice that systematically lowers the totals. Not a slant, but a limit the AI should have surfaced.

**The Guardian - 662% claim** - Headline states a contested accounting result as a measured fact. The 662% figure is an artefact of switching accounting bases, which the article explains only well below the headline.

**Google - AI at Google Scale** - Vendor-selected scope boundary. The per-prompt figure excludes model training amortisation and uses on-site water only, both of which push the number down. Methodology is disclosed, which is genuinely better than the norm - but disclosure is not independence.

**Microsoft - Sustainability Report** - Market-based carbon accounting presents a materially lower emissions figure than location-based accounting would. Legal and standard-compliant, and also the most flattering permissible choice.

**Reuters - billion-dollar search problem** - AI treated this as a neutral wire report. It is - but it quotes a single interested executive, and that one sentence became the '10x' statistic repeated worldwide for three years. The bias is in what got amplified, not in the reporting.

**Making AI Less Thirsty** - No slant in the paper. The authors state their assumptions carefully. The distortion was introduced entirely downstream - a caution against treating 'bias' as a property only of sources rather than of transmission.

**Hacker News thread** - Practitioner population skews toward defending the industry; counter-arguments were technically strong but the sample is not representative.


### Bias Reflection


#### Which source appeared most objective and why?

The LBNL 2024 report for the US Department of Energy. It states its method, publishes a range rather than a point estimate, names what it excludes - notably embodied carbon in hardware - and its authors have no commercial position in the outcome. Notably, the AI did not flag any limitation in it at all; I had to find the scope exclusions myself. An AI bias check that returns 'no bias detected' is reporting the absence of a detectable slant, not the presence of completeness.


#### Which source appeared most biased and why?

Two candidates, biased in opposite directions and worth naming together. Google's per-prompt disclosure is the more consequential: the methodology is published, which is genuinely better than industry norm, but the vendor selects the scope boundary, and the boundary it selected excludes training amortisation and off-site water. That is the difference between 0.26 ml and figures three orders of magnitude larger. The Guardian's 662% headline is biased in the other direction, presenting an accounting-basis switch as a measured emissions figure. Neither fabricates. Both let the reader draw a conclusion the underlying data does not support.


#### Did the AI correctly identify all biases?

No. It reliably detected explicit framing bias - advocacy language, commercial promotion - which is the easy case. It missed every instance of scope bias, where the distortion lives in what a methodology counts rather than in how it is written, and it missed transmission bias entirely: it never observed that a source could be impeccable while the claim attributed to it had been mangled in transit. Both required the explicit prompt structure in Phase 10 Step 6, and even then I found two of the eight assessments myself.


#### How can prompt engineering reduce bias in AI-generated outputs?

Four things worked, in ascending order of effect. Requiring a source tier per claim forces the model to expose how thin its support is. Requiring that contradictions be reported rather than resolved stops it from silently averaging two positions into a false consensus. Asking specifically what a methodology counts in and out catches scope bias, which framing-focused prompts never reach. And most effective by a wide margin: explicitly permitting 'I could not verify this.' Without that permission the model must produce something, and what it produces is the most statistically typical claim - which encodes the bias of the corpus by construction. Bias reduction is mostly a matter of removing the pressure to answer.


### Ethical Concerns Identified

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

---


## Phase 12 - Final Investigation Report


### Executive Summary (309 words)

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


### Background (297 words)

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


### Key Findings (577 words)

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


### Verified Facts

| # | Fact | Evidence Source |
| --- | --- | --- |
| 1 | Global data centres consumed roughly 415 TWh of electricity in 2024, about 1.5% of world electricity. | International Energy Agency (IEA) - Energy and AI (World Energy Outlook Special Report) (2025-04) |
| 2 | Global data-centre demand roughly doubles to about 945 TWh by 2030 under the IEA Base Case. | International Energy Agency (IEA) - Energy and AI (World Energy Outlook Special Report) (2025-04) |
| 3 | US data centres consumed about 176 TWh in 2023, roughly 4.4% of total US electricity. | Lawrence Berkeley National Laboratory for US DOE - 2024 United States Data Center Energy Usage Report (LBNL-2001637) (2024-12) |
| 4 | US data centres are projected to reach 6.7%-12% of US electricity by 2028. | Lawrence Berkeley National Laboratory for US DOE - 2024 United States Data Center Energy Usage Report (LBNL-2001637) (2024-12) |
| 5 | AI servers could consume 85-134 TWh per year by 2027. | Alex de Vries, Joule 7(10) 2191-2194 - The growing energy footprint of artificial intelligence (2023-10) |
| 6 | Data centres accounted for 21% of Ireland's metered electricity consumption in 2023. | Central Statistics Office Ireland - Data Centres Metered Electricity Consumption 2023 (2024-07) |


### Identified Misinformation

| # | Claim | Why It Is Incorrect |
| --- | --- | --- |
| 1 | A single ChatGPT query consumes 500 ml of water. | The source states ~500 ml per CONVERSATION of roughly 10-50 exchanges, and only for specified data centres, seasons and locations. The per-query framing is a compression error introduced downstream. |
| 2 | An LLM query uses about 10x the electricity of a conventional web search. | Traceable to a single 2023 executive remark in S05, not to a measurement. S13 and S14 both report per-query figures broadly comparable to legacy search estimates, so the multiplier is contradicted by later evidence. |
| 3 | AI will consume 20-25% of US electricity by 2030. | Traceable to an executive interview, not to any national inventory or peer-reviewed model. Directly contradicted by S02's 6.7%-12% range for ALL data centres, of which AI is a subset. |


### Lessons Learned About Prompt Engineering (306 words)

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


### Final Conclusion (325 words)

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

---


## Appendix A - Pre-Submission Verification Checklist

> **Read this before submitting**
>
> Every figure in this report is reproduced from the source stated beside it, but the sources below have not yet been re-opened and checked against the primary document by the author. URLs move, reports are revised, and figures are restated between editions. Open each one, confirm the figure and the URL, then set `student_verified` to `Y` in `toolkit/data/sources.csv` and regenerate. A study about verification that shipped an unverified source list without saying so would be demonstrating its own thesis by accident.

| Checked | Source | Document to open | Publisher | URL |
| --- | --- | --- | --- | --- |
| [  ] | S01 | Energy and AI (World Energy Outlook Special Report) | International Energy Agency (IEA) | https://www.iea.org/reports/energy-and-ai |
| [  ] | S02 | 2024 United States Data Center Energy Usage Report (LBNL-2001637) | Lawrence Berkeley National Laboratory for US DOE | https://eta.lbl.gov/publications/2024-united-states-data-center-energy-usage-report |
| [  ] | S03 | Directive (EU) 2023/1791 (Energy Efficiency Directive recast) Art. 12 + Delegated Regulation (EU) 2024/1364 | European Union / EUR-Lex | https://eur-lex.europa.eu/eli/dir/2023/1791/oj |
| [  ] | S04 | Data Centres Metered Electricity Consumption 2023 | Central Statistics Office Ireland | https://www.cso.ie/en/statistics/energy/datacentresmeteredelectricityconsumption/ |
| [  ] | S05 | For tech giants, AI like Bing and Bard poses billion-dollar search problem | Reuters | https://www.reuters.com/technology/tech-giants-ai-like-bing-bard-poses-billion-dollar-search-problem-2023-02-22/ |
| [  ] | S06 | Artificial intelligence technology behind ChatGPT was built in Iowa - with a lot of water | Associated Press | https://apnews.com/article/chatgpt-gpt4-iowa-ai-water-consumption-microsoft-f551fde98083d17a7e8d904f8be822c4 |
| [  ] | S07 | Data centre emissions probably 662% higher than big tech claims | The Guardian | https://www.theguardian.com/technology/2024/sep/15/data-center-gas-emissions-tech |
| [  ] | S08 | We did the math on AI's energy footprint. Here's the story you haven't heard. | MIT Technology Review | https://www.technologyreview.com/2025/05/20/1116327/ai-energy-usage-climate-footprint-big-tech/ |
| [  ] | S09 | Google says a Gemini text prompt uses about five drops of water | The Verge | https://www.theverge.com/ |
| [  ] | S10 | The growing energy footprint of artificial intelligence | Alex de Vries, Joule 7(10) 2191-2194 | https://doi.org/10.1016/j.joule.2023.09.004 |
| [  ] | S11 | Making AI Less 'Thirsty': Uncovering and Addressing the Secret Water Footprint of AI Models | Li, Yang, Islam & Ren - arXiv:2304.03271 (later Communications of the ACM) | https://arxiv.org/abs/2304.03271 |
| [  ] | S12 | Power Hungry Processing: Watts Driving the Cost of AI Deployment? | Luccioni, Jernite & Strubell - ACM FAccT 2024 (arXiv:2311.16863) | https://arxiv.org/abs/2311.16863 |
| [  ] | S13 | How much energy does ChatGPT use? | Epoch AI | https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use |
| [  ] | S14 | Measuring the environmental impact of delivering AI at Google Scale | Google | https://cloud.google.com/blog/products/infrastructure/measuring-the-environmental-impact-of-ai |
| [  ] | S15 | 2024 Environmental Sustainability Report | Microsoft | https://www.microsoft.com/en-us/corporate-responsibility/sustainability/report |
| [  ] | S16 | Zero-shot investigation output (Phase 3) | Claude Opus 5 - author's transcript | transcripts/measure_v1.md (produced by `run_all.py --measure`) |
| [  ] | S17 | Role-prompted investigation output (Phase 4) | Claude Opus 5 - author's transcript | transcripts/measure_v2.md (produced by `run_all.py --measure`) |
| [  ] | S18 | ReAct verification output (Phase 6) | Perplexity - author's transcript | transcripts/chain_5_verify.md (produced by `run_all.py --chain --live`) |
| [  ] | S19 | Hacker News thread on AI water consumption reporting | news.ycombinator.com | https://news.ycombinator.com/ |
| [  ] | S20 | r/MachineLearning discussion on per-query energy estimates | reddit.com/r/MachineLearning | https://www.reddit.com/r/MachineLearning/ |


## Appendix B - Complete Prompt Library

Every prompt used in the study, reproduced verbatim from `toolkit/pe_toolkit/prompts.py`. The report and the pipeline read the same objects, so these cannot drift from what was actually executed.


#### Phase 3 - Zero-shot (`zero_shot`)

**Intent:** Establish an honest baseline. This prompt is deliberately bad - no role, no source constraint, no citation obligation, no permission to say 'unknown'. Everything measured later is measured against it.

```text
Tell me about the environmental impact of AI data centres. How much energy and water do they use?
```


#### Phase 4 - Role-based (`role`)

**Intent:** Test whether persona alone improves reliability. It improves structure and tone; on its own it does not stop fabrication.

```text
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
```


#### Phase 5 - Chain-of-Thought (`cot`)

**Intent:** Force the reasoning to be inspectable so that the step where a claim loses its qualifiers becomes visible and auditable.

```text
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
```


#### Phase 6 - ReAct (Reason + Act) (`react`)

**Intent:** Force an explicit search/observe loop so the model cannot answer from parametric memory. The ACTION step is what converts a recollection into a citation.

```text
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
```


#### Phase 7 - Adversarial elicitation (`hallucination_probe`)

**Intent:** Deliberately create the conditions that produce hallucination - a demand for a fixed quantity of specific detail, with social pressure to be comprehensive and no permission to decline. This prompt is an instrument, not a mistake.

```text
I need a comprehensive briefing on {topic} for a presentation tomorrow.

Give me exactly:
  - 8 additional facts that most coverage misses, with specific figures
  - 4 concrete predictions for 2030 with numbers
  - 6 underlying causes that are not widely discussed
  - 6 expert opinions, with names, titles and direct quotes

Be specific and authoritative. Include exact statistics and named sources
throughout - vague answers are not useful to me. Please make sure you fill
every slot.
```


#### Phase 8 - Zero-shot, unconstrained (`v1`)

**Intent:** Baseline.

```text
What is the environmental impact of AI data centres? Give me the key statistics.
```


#### Phase 8 - Role + source tier (`v2`)

**Intent:** Add persona and a source hierarchy.

```text
Act as a Senior Investigative Journalist covering energy infrastructure.

Report on the environmental impact of AI data centres. Rank every claim by
source tier (1 intergovernmental / 2 peer-reviewed / 3 quality journalism /
4 corporate self-report / 5 social media) and state the tier alongside each
claim.
```


#### Phase 8 - Role + CoT + citation obligation (`v3`)

**Intent:** Add inspectable reasoning and a hard citation requirement.

```text
Act as a Senior Investigative Journalist covering energy infrastructure,
filing to a desk that independently fact-checks every number.

Report on the environmental impact of AI data centres.

Before writing each claim, reason explicitly through: (a) what exactly is being
asserted, (b) which document originally established it, (c) what qualifiers
that document attached, and (d) whether those qualifiers survive in your
sentence. Show this reasoning.

Every factual claim requires a named organisation, document title and year.
Separate what is measured from what you are inferring.
```


#### Phase 8 - Role + CoT + ReAct + refusal clause + confidence (`v4`)

**Intent:** The production prompt. Adds a verification loop, explicit permission to refuse, per-claim confidence, and a duty to report contradictions rather than resolve them silently.

```text
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
```


#### Phase 10 - Step 1 - Zero-shot scoping (`chain_1_topic`)

**Intent:** Map the territory and, critically, name the contested points.

```text
Map the debate on {topic}.

Produce: (a) the six questions a serious reader needs answered, (b) the main
positions and who holds them, (c) the specific points where credible sources
disagree, and (d) the technical terms a non-specialist must understand to read
this literature - especially any term whose definition affects the numbers.

Do not resolve the disagreements. Name them.
```


#### Phase 10 - Step 2 - Few-shot (`chain_2_sources`)

**Intent:** Two worked examples fix the output schema and, more importantly, demonstrate that a source's weakness is part of the record.

```text
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
```


#### Phase 10 - Step 3 - Structured extraction (`chain_3_claims`)

**Intent:** Convert prose into atomic, individually checkable assertions.

```text
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
```


#### Phase 10 - Step 4 - Comparative CoT (`chain_4_contradictions`)

**Intent:** Distinguish genuine factual disputes from definitional mismatches.

```text
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
```


#### Phase 10 - Step 5 - ReAct (`chain_5_verify`)

**Intent:** Ground each claim in a retrievable document.

```text
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
```


#### Phase 10 - Step 6 - Role + adversarial critique (`chain_6_bias`)

**Intent:** Bias analysis fails when it only asks about slant. This prompt also asks about scope boundaries and about the bias introduced in transmission rather than at the source.

```text
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
```


#### Phase 10 - Step 7 - Constrained synthesis (`chain_7_report`)

**Intent:** Synthesise without reintroducing anything the chain rejected.

```text
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
```


## Appendix C - Reproducibility

The toolkit accompanying this report regenerates every table, figure and word of the document from `toolkit/data/`. Run `python run_all.py --check` to execute the consistency invariants, or `python run_all.py` to rebuild the Markdown, DOCX and PDF. The Claude runner operates in replay mode against the recorded transcripts when no API credentials are present, so the document is reproducible without spending tokens and without the evidence base shifting underneath it. The model is pinned to `claude-opus-5` rather than a floating alias for the same reason.

| Component | Role |
| --- | --- |
| toolkit/data/*.csv | Evidence base - the single source of truth |
| pe_toolkit/prompts.py | Every prompt, shared by the pipeline and the report |
| pe_toolkit/llm.py | Claude client; live or replay from transcripts |
| pe_toolkit/chain.py | The seven-step Phase 10 workflow |
| pe_toolkit/audit.py | Phase 7 scoring and cross-file invariants |
| pe_toolkit/metrics.py | Phase 8 and Phase 9 scoring |
| pe_toolkit/charts.py | All six figures |
| pe_toolkit/report.py | Markdown and DOCX renderers |


## Faculty Evaluation Rubric

| Criteria | Marks |
| --- | --- |
| Topic Selection | 5 |
| Evidence Collection | 5 |
| Prompt Design | 10 |
| CoT & ReAct Usage | 10 |
| Hallucination Detection | 10 |
| Prompt Optimization | 10 |
| Multi-LLM Comparison | 5 |
| Ethical Analysis | 5 |
| Final Report | 15 |
| Overall Professionalism | 25 |
| Total | 100 |
