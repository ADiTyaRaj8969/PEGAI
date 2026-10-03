# Prompt History — Hint-Based Math Tutor

**Team 5 · Problem 13 · 3 October 2026**

Timestamped log of every prompt written or changed, from 11:00 AM onward, as required by the
problem statement. Each entry records **what changed**, **why**, and **what effect it had**.

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

| Prompt constant | File | Technique(s) | Version | Explained by |
|---|---|---|---|---|
| `V1_SINGLE_PROMPT` | `tutor/prompts.py` | zero-shot baseline | v1 | |
| `SOLVER_PROMPT` | `tutor/prompts.py` | hidden CoT + structured output | | |
| `HINT_LADDER_PROMPT` | `tutor/prompts.py` | few-shot + role | | |
| `LEAK_CRITIQUE_PROMPT` | `tutor/prompts.py` | self-critique | | |
| `DIAGNOSE_PROMPT` | `tutor/prompts.py` | decomposition + structured output | | |
| `OFF_TOPIC_GUARD` | `tutor/prompts.py` | classification | | |
