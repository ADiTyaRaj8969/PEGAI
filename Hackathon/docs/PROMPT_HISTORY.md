<div align="center">

# Prompt History

### Timestamped log of every prompt written or changed

[![Team](https://img.shields.io/badge/Team-5-7b2d8e?style=flat-square)](#)
[![Problem](https://img.shields.io/badge/Problem-13-0b3d62?style=flat-square)](#)
[![From](https://img.shields.io/badge/from-11%3A00%20AM-b35309?style=flat-square)](#)
[![Required](https://img.shields.io/badge/rubric-required-b30000?style=flat-square)](#)

</div>

---

Required by the brief: *keep timestamped prompt history (Git or doc) from 11:00 AM onward.*
Each entry records **what changed**, **why**, and **what effect it had**.

> [!IMPORTANT]
> Keep this file open while building. Add an entry at the moment of the change, not afterwards.
> Commit after each entry so the Git timestamps corroborate the log.

---

## Entry Template

```
### HH:MM — <prompt name> v<N>

**Change:** what was added, removed, or reworded.
**Technique:** decomposition / few-shot / role / hidden CoT / structured output / self-critique.
**Why:** the failure or gap that motivated it.
**Effect:** what the behaviour or metric did afterwards.
**Author:** name.
```

---

## Log

### 11:00 — Project start

**Change:** Repository initialised; README, SRS and project plan committed before any code.
**Why:** Fix the leak-check contract and the JSON schemas up front so three tracks can build in
parallel without re-negotiating interfaces.
**Effect:** Baseline established.
**Author:** —

---

<!--
Add entries below this line as you work. Suggested checkpoints — delete the ones you do not hit
and add the ones you do:

### 11:15 — V1_SINGLE_PROMPT v1
### 11:30 — SOLVER_PROMPT v1
### 11:45 — HINT_LADDER_PROMPT v1
### 12:00 — HINT_LADDER_PROMPT v2  (added few-shot exemplars)
### 12:10 — LEAK_CRITIQUE_PROMPT v1
### 12:55 — DIAGNOSE_PROMPT v1
### 01:20 — OFF_TOPIC / injection hardening
### 01:40 — final V2 freeze before evaluation run
-->

---

## Prompt Inventory

Fill in as each prompt lands. Every member must be able to explain every row.

| Prompt constant | File | Technique | Version | Explained by |
|---|---|---|:--:|---|
| `V1_SINGLE_PROMPT` | `tutor/prompts.py` | Zero-shot baseline | v1 | |
| `SOLVER_PROMPT` | `tutor/prompts.py` | Hidden CoT + structured output | | |
| `REPAIR_PROMPT` | `tutor/prompts.py` | Output repair | | |
| `HINT_LADDER_PROMPT` | `tutor/prompts.py` | Few-shot + role | | |
| `LEAK_CRITIQUE_PROMPT` | `tutor/prompts.py` | Self-critique | | |
| `DIAGNOSE_PROMPT` | `tutor/prompts.py` | Decomposition + structured output | | |
| `OFF_TOPIC_GUARD` | `tutor/prompts.py` | Classification | | |

> [!TIP]
> If the log runs thin under time pressure, reconstruct it from the commit times:
> `git log --format='%ad %s' --date=format:'%H:%M'`

---

<div align="center">

[Back to README](../README.md) · [Phase Index](PHASES_INDEX.md) · [Evaluation](EVALUATION.md)

</div>
