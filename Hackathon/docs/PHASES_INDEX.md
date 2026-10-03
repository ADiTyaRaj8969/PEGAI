<div align="center">

# Phase Index

### The build, divided into nine phases

[![Team](https://img.shields.io/badge/Team-5-7b2d8e?style=flat-square)](#)
[![Problem](https://img.shields.io/badge/Problem-13-0b3d62?style=flat-square)](#)
[![Window](https://img.shields.io/badge/Window-11%3A00%20–%2014%3A00-b35309?style=flat-square)](#)
[![Prompts](https://img.shields.io/badge/Prompts-6-1a7f64?style=flat-square)](#)

</div>

---

Each document below contains that phase's tasks, the **complete prompt text** to paste into
`tutor/prompts.py`, a line-by-line rationale for every prompt rule, the test that proves the
phase works, and its exit criteria.

| Phase | Time | Document | Prompts introduced |
|:--:|:--:|---|---|
| **0** | `11:00–11:15` | [Setup](PHASE_0_SETUP.md) | — |
| **1** | `11:15–11:30` | [V1 Baseline](PHASE_1_BASELINE.md) | `V1_SINGLE_PROMPT` |
| **2** | `11:30–11:45` | [Hidden Solver](PHASE_2_SOLVER.md) | `SOLVER_PROMPT`, `REPAIR_PROMPT` |
| **3** | `11:45–12:05` | [Hint Ladder](PHASE_3_HINT_LADDER.md) | `HINT_LADDER_PROMPT` |
| **4** | `12:05–12:25` | [Leak Guard](PHASE_4_LEAK_GUARD.md) | `LEAK_CRITIQUE_PROMPT` |
| **5** | `12:25–12:50` | [Streamlit UI](PHASE_5_UI.md) | — |
| **6** | `12:50–13:15` | [Wrong-Step Detection](PHASE_6_DIAGNOSE.md) | `DIAGNOSE_PROMPT` |
| **7** | `13:15–13:30` | [Guardrails](PHASE_7_GUARDRAILS.md) | `INJECTION_NOTICE`, static refusals |
| **8** | `13:30–14:00` | [Evaluation & Demo](PHASE_8_EVALUATION.md) | — |

---

## Prompt Inventory

Every prompt in the system, where it is defined, and the technique it demonstrates. The brief
requires **at least two** techniques combined — this system uses **five**.

| Prompt | Phase | Technique | Owner |
|---|:--:|---|---|
| `V1_SINGLE_PROMPT` | 1 | Zero-shot baseline *(deliberately weak)* | |
| `SOLVER_PROMPT` | 2 | Hidden chain-of-thought + structured output | |
| `REPAIR_PROMPT` | 2 | Output repair | |
| `HINT_LADDER_PROMPT` | 3 | Few-shot + role/persona prompting | |
| `LEAK_CRITIQUE_PROMPT` | 4 | Self-critique / targeted regeneration | |
| `DIAGNOSE_PROMPT` | 6 | Decomposition + comparative reasoning | |

> [!NOTE]
> Fill in the **Owner** column during Phase 0 and cross-quiz each other in
> [Phase 8.6](PHASE_8_EVALUATION.md). Every member must be able to explain every prompt.

---

## Why the Pipeline Is Split

The naive approach — one prompt saying *"give three hints, don't reveal the answer"* — fails
because **the model is the only thing standing between the student and the answer**. When it
slips, nothing catches it.

Splitting the work means the system knows the answer as a *value* before it writes any hint, so
the check for a leak becomes string and number comparison in Python rather than a matter of model
compliance.

```
Phase 2 solver ──► knows final_answer = "60 km/h"
                        │
Phase 3 ladder ──► writes L1, L2, L3 from that known solution
                        │
Phase 4 guard  ──► asserts "60" ∉ L1, L2     ← deterministic, not a prompt
```

That is the whole argument for this architecture, and it is what
[Phase 1](PHASE_1_BASELINE.md) exists to demonstrate by contrast.

---

## Reading Order for a New Team Member

| | Document | Why |
|:--:|---|---|
| **1** | [PROJECT_PLAN.md](PROJECT_PLAN.md) | The schedule and who builds what |
| **2** | [Phase 1 · V1 Baseline](PHASE_1_BASELINE.md) | What failure looks like |
| **3** | [Phase 4 · Leak Guard](PHASE_4_LEAK_GUARD.md) | The core idea |
| **4** | [SRS.md](SRS.md) | The formal requirements behind each phase |

---

<div align="center">

[Back to README](../README.md) · [Phase 0 · Setup →](PHASE_0_SETUP.md)

</div>
