<div align="center">

# Hint-Based Math Tutor

### Guiding students to the answer — never handing it over

[![Problem](https://img.shields.io/badge/Problem-13-0b3d62?style=for-the-badge)](docs/PHASES_INDEX.md)
[![Theme](https://img.shields.io/badge/Theme-C%20·%20Reasoning%20%26%20Multi--Step-1a7f64?style=for-the-badge)](docs/SRS.md)
[![Team](https://img.shields.io/badge/Team-5-7b2d8e?style=for-the-badge)](#)
[![Venue](https://img.shields.io/badge/Venue-MB306-b35309?style=for-the-badge)](#)

**Prompt Engineering for Generative AI** · 3-Hour Hackathon · 3 October 2026
Marwadi University — Marwadi Chandarana Group

</div>

---

## The Brief

> ### The Problem
> Guide a student through a word problem with progressive hints without revealing the
> final answer early.

> ### Your Prototype Must Show
> A 3-level hint ladder and a check that the answer is never leaked at levels 1–2.

> ### Stretch Challenge *(mandatory)*
> Detect the specific wrong step in a student's working and give a targeted hint instead of
> a generic one.

<details>
<summary><b>Every Team Must Also…</b> <i>(click to expand)</i></summary>

<br>

- Deliver a **working prototype** that runs on a new, unseen input.
- Measure results: a labelled set of 10+ cases and one metric, **first version vs final version**.
- Combine **at least two prompting techniques** and show a side-by-side comparison in the demo.
- Build **guardrails into the app** (invalid output, off-topic input, refusals).
- Keep **timestamped prompt history** (Git or doc) from 11:00 AM onward.

> Every member must be able to explain every prompt.

</details>

---

## How It Works

The tutor **solves the problem privately first**, generates a 3-step hint ladder from that hidden
solution, and only releases a hint after a **deterministic leak check** confirms the final answer
is not present.

```
                    Student word problem
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │  1 · SOLVER PASS                      │  hidden scratchpad,
        │     → { final_answer, steps[] }       │  never shown
        └───────────────────┬───────────────────┘
                            ▼
        ┌───────────────────────────────────────┐
        │  2 · HINT LADDER                      │  few-shot + role
        │     L1 concept → L2 setup → L3 walk   │  prompting
        └───────────────────┬───────────────────┘
                            ▼
        ┌───────────────────────────────────────┐
        │  3 · LEAK GUARD                       │  programmatic,
        │     L1/L2 must not contain the answer │  not LLM-trusted
        └───────────────────┬───────────────────┘
                            ▼
                     Hint shown to student


                 Student submits their working
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │  4 · STEP DIAGNOSIS                   │  stretch
        │     → first wrong step, targeted hint │  challenge
        └───────────────────────────────────────┘
```

> [!IMPORTANT]
> The leak check is **code, not a prompt**. The model is never the final authority on whether it
> leaked the answer — a model that leaks is also a model that can wrongly report it didn't.
> See [SRS §4.3](docs/SRS.md).

---

## Prompting Techniques Combined

The brief requires **at least two**. This system combines **five**.

| # | Technique | Where it is used |
|:--:|---|---|
| 1 | **Decomposition** — solve → hint → verify as separate calls | Whole pipeline |
| 2 | **Few-shot exemplars** | Hint ladder prompt |
| 3 | **Role / persona prompting** — *"patient tutor who never gives answers"* | Hint ladder prompt |
| 4 | **Hidden chain-of-thought + structured JSON** | Solver pass |
| 5 | **Self-critique pass** | Regeneration after a leak is caught |

The demo shows **V1** *(single zero-shot prompt)* beside **V2** *(decomposed + few-shot + guard)*.

---

## Metric

<table>
<tr>
<td width="50%" valign="top">

**PRIMARY**
**Answer Leak Rate @ L1–L2**

Percentage of the 12 labelled cases where the final answer appears in hint level 1 or 2.

*Lower is better · Target: 0%*

</td>
<td width="50%" valign="top">

**SECONDARY**
**Wrong-Step Localisation Accuracy**

Percentage of seeded-error cases where the tutor names the correct step index.

*Higher is better*

</td>
</tr>
</table>

Results table → [docs/EVALUATION.md](docs/EVALUATION.md)

---

## Documents

| Document | What it covers |
|---|---|
| **[PHASES_INDEX.md](docs/PHASES_INDEX.md)** | **Start here** — every phase with complete prompt text and line-by-line rationale |
| [SRS.md](docs/SRS.md) | Software Requirements Specification *(also as [PDF](docs/SRS_Hint_Based_Math_Tutor.pdf))* |
| [PROJECT_PLAN.md](docs/PROJECT_PLAN.md) | The build broken into 8 phases with a time budget |
| [PROMPT_HISTORY.md](docs/PROMPT_HISTORY.md) | Timestamped prompt log from 11:00 AM |
| [EVALUATION.md](docs/EVALUATION.md) | Labelled case set and V1-vs-V2 results |

---

## Quick Start

> [!NOTE]
> The code is scaffolded across the phase documents — see
> [Phase 0 · Setup](docs/PHASE_0_SETUP.md) to build it.

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

---

<div align="center">

**Team 5** · Problem 13 · Theme C
*Prompt Engineering for Generative AI · Marwadi University*

</div>
