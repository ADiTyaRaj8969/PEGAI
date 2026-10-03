# Problem 13 — Hint-Based Math Tutor

**Prompt Engineering for Generative AI · 3-Hour Hackathon · 3 October 2026**
Marwadi University (Marwadi Chandarana Group)

| | |
|---|---|
| **Problem No.** | 13 |
| **Theme** | C — Reasoning, Decomposition and Multi-Step Workflows |
| **Team No.** | 5 |
| **Venue** | MB306 |
| **Date** | 3 October 2026 |

---

## The Problem

> Guide a student through a word problem with progressive hints without revealing the
> final answer early.

## Your Prototype Must Show

> A 3-level hint ladder and a check that the answer is never leaked at levels 1–2.

## Stretch Challenge (mandatory)

> Detect the specific wrong step in a student's working and give a targeted hint instead of
> a generic one.

## Every Team Must Also

- Deliver a **working prototype** that runs on a new, unseen input.
- Measure results: a labelled set of 10+ cases and one metric, **first version vs final version**.
- Combine **at least two prompting techniques** and show a side-by-side comparison in the demo.
- Build **guardrails into the app** (invalid output, off-topic input, refusals).
- Keep **timestamped prompt history** (Git or doc) from 11:00 AM onward.

> Every member must be able to explain every prompt.

---

## Solution Overview

A tutor that **solves the problem privately first**, then generates a 3-step hint ladder from
that hidden solution, and only releases a hint after a **deterministic leak check** confirms the
final answer is not present.

```
Student word problem
        │
        ▼
┌───────────────────┐   hidden scratchpad, never shown to the student
│  1. Solver pass   │──► { final_answer, steps[], method }
└───────────────────┘
        │
        ▼
┌───────────────────┐   few-shot + role prompting over the known solution
│  2. Hint ladder   │──► L1 concept nudge · L2 setup/method · L3 guided walkthrough
└───────────────────┘
        │
        ▼
┌───────────────────┐   programmatic, not LLM-trusted
│  3. Leak guard    │──► L1/L2 must NOT contain the final answer → else regenerate
└───────────────────┘
        │
        ▼
    Hint shown to student

Student submits their own working
        │
        ▼
┌───────────────────┐   stretch challenge
│  4. Step diagnose │──► first wrong step index + targeted hint for that step
└───────────────────┘
```

The leak check is **code, not a prompt** — the model is never the final authority on whether it
leaked the answer. See [docs/SRS.md](docs/SRS.md) §4.3.

## Prompting Techniques Combined

| # | Technique | Where it is used |
|---|---|---|
| 1 | **Decomposition** (solve → hint → verify as separate calls) | Whole pipeline |
| 2 | **Few-shot exemplars** | Hint ladder prompt |
| 3 | **Role / persona prompting** ("patient tutor who never gives answers") | Hint ladder prompt |
| 4 | **Hidden chain-of-thought + structured JSON output** | Solver pass |
| 5 | **Self-critique pass** | Regeneration after a leak is caught |

The demo shows **V1 (single zero-shot prompt)** beside **V2 (decomposed + few-shot + guard)**.

## Metric

**Primary — Answer Leak Rate @ L1–L2:** percentage of the 12 labelled cases where the final
answer appears in hint level 1 or 2. Lower is better; target 0%.

**Secondary — Wrong-Step Localisation Accuracy:** percentage of cases with a seeded error
where the tutor names the correct step index.

Results table: [docs/EVALUATION.md](docs/EVALUATION.md) (filled in during the run).

## Documents

- [docs/PHASES_INDEX.md](docs/PHASES_INDEX.md) — **start here**: every phase, with the complete
  prompt text and a line-by-line rationale for each rule
- [docs/SRS.md](docs/SRS.md) — Software Requirements Specification
- [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md) — the build broken into 8 phases with a time budget
- [docs/PROMPT_HISTORY.md](docs/PROMPT_HISTORY.md) — timestamped prompt log from 11:00 AM

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env        # add your API key
streamlit run app.py
```

Run the evaluation harness:

```bash
python -m eval.run_eval --version v1
python -m eval.run_eval --version v2
python -m eval.run_eval --compare
```
