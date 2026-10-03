<div align="center">

# Phase 1 · V1 Baseline

[![Time](https://img.shields.io/badge/11%3A15%20–%2011%3A30-0b3d62?style=flat-square)](#)
[![Prompt](https://img.shields.io/badge/prompt-V1__SINGLE__PROMPT-1a7f64?style=flat-square)](#)
[![Technique](https://img.shields.io/badge/technique-zero--shot%20baseline-7b2d8e?style=flat-square)](#)

</div>

---

## Goal

Build the naive version *on purpose*, and record where it fails. The brief asks for a
**first version vs final version** comparison — this is the first version, and it only counts as
evidence if it was built honestly rather than sabotaged.

## Why Build Something You Know Is Broken

Judges ask "how do you know your engineering helped?" The answer has to be a number from a real
baseline, not an assertion. V1 is a reasonable, good-faith attempt at the problem using one
prompt — the kind most teams will submit. Its leak rate is the bar V2 must clear.

> [!WARNING]
> **Do not weaken this prompt to make V2 look better.** If V1 happens to score well, that is a
> finding worth reporting, and V2 still wins on the guarantee: V1 *might* not leak, V2 *cannot*.

---

## The Prompt

Paste into `tutor/prompts.py`:

```python
# ─────────────────────────────────────────────────────────────────────
# V1 — BASELINE.  Technique: zero-shot, single call, no verification.
# Kept permanently for the V1-vs-V2 comparison required by the brief.
# Do not improve this prompt. Its weaknesses are the measurement.
# ─────────────────────────────────────────────────────────────────────
V1_SINGLE_PROMPT = """You are a helpful math tutor. A student is stuck on this problem:

{problem}

Give the student three hints that get progressively more helpful.
Hint 1 should be a small nudge, hint 2 should be more helpful, and hint 3
should be the most helpful.

Do not reveal the final answer.

Format your reply as:
Hint 1: ...
Hint 2: ...
Hint 3: ..."""
```

## Why This Prompt Fails

| Weakness | Consequence |
|---|---|
| "Do not reveal the final answer" is the **only** safeguard | If the model ignores it, nothing catches the leak |
| The model never computes the answer separately | It cannot reliably avoid stating a value it derived mid-sentence |
| "More helpful" is undefined | Levels blur; L2 often reads like L3 |
| Free text output | No field to check programmatically |
| One call does classify + solve + teach + suppress | Four jobs, no step has full attention |

The decisive one is the first. Instruction-following on a negative constraint
("do **not** say X") is probabilistic. A requirement stated as a guarantee needs an enforcement
mechanism that is not the same component being constrained.

---

## Implementation

```python
# tutor/hints.py
from tutor.llm import complete
from tutor.prompts import V1_SINGLE_PROMPT

def generate_v1(problem: str) -> str:
    """Baseline: one call, raw text out, no guard. Kept for comparison."""
    return complete(V1_SINGLE_PROMPT.format(problem=problem), temperature=0.2)
```

---

## Required Task — Capture the Failures

Run V1 on these three problems and **write down every leak verbatim**. This table is demo material;
judges consistently ask to see a concrete failure.

```python
for p in [
    "A train covers 120 km in 2 hours. What is its average speed?",
    "A shirt costs Rs 800. The shopkeeper gives a 15% discount. What is the selling price?",
    "Ravi is 3 times as old as his son. In 10 years he will be twice as old. How old is Ravi now?",
]:
    print(p, "\n", generate_v1(p), "\n" + "─" * 60)
```

Record results here and in [PROMPT_HISTORY.md](PROMPT_HISTORY.md):

| Problem | Correct answer | Leaked at | Exact leaked text |
|---|---|---|---|
| Train / speed | 60 km/h | | |
| Shirt / discount | Rs 680 | | |
| Ravi / ages | 30 years | | |

Watch for the subtle forms, not just the bare number:

- **Worked arithmetic** — "so 120 ÷ 2 = 60 km/h" in hint 2
- **Restated as a check** — "verify that your answer is 60"
- **In words** — "you should get sixty"
- **Rounded or unit-shifted** — "about 60", "1 km per minute"

All four count as leaks. The Phase 4 guard is built to catch exactly these.

---

## Exit Criteria

- [ ] `generate_v1()` runs and returns three hints
- [ ] All three problems tested, output saved
- [ ] At least one leak captured verbatim — if none leaked, test three more problems
- [ ] Findings logged in [PROMPT_HISTORY.md](PROMPT_HISTORY.md) with the 11:15 timestamp
- [ ] `V1_SINGLE_PROMPT` committed and **not edited again**

---

## What to Say in the Demo

> "This is the version most teams would write — one prompt, told not to reveal the answer. Here it
> is leaking at hint 2 on a problem we did not cherry-pick. The instruction is there; the model
> just didn't follow it. We measured it at _N_% across twelve cases. Everything we built after
> this exists to turn that instruction into a guarantee."

<div align="center">

[← Phase 0 · Setup](PHASE_0_SETUP.md) · [Index](PHASES_INDEX.md) · [Phase 2 · Hidden Solver →](PHASE_2_SOLVER.md)

</div>
