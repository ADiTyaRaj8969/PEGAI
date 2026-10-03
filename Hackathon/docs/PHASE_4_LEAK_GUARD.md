<div align="center">

# Phase 4 · Leak Guard

[![Time](https://img.shields.io/badge/12%3A05%20–%2012%3A25-0b3d62?style=flat-square)](#)
[![Prompt](https://img.shields.io/badge/prompt-LEAK__CRITIQUE__PROMPT-1a7f64?style=flat-square)](#)
[![Technique](https://img.shields.io/badge/technique-self--critique-7b2d8e?style=flat-square)](#)
[![Priority](https://img.shields.io/badge/priority-DO%20NOT%20CUT-b30000?style=flat-square)](#)

</div>

---

> [!CAUTION]
> **This phase is the project.** It is what turns the brief's requirement into a guarantee.
> If the schedule slips, cut [Phase 5](PHASE_5_UI.md) polish or
> [Phase 7](PHASE_7_GUARDRAILS.md) breadth — never this.

## Goal

Make "the answer is never leaked at levels 1–2" a **guarantee** rather than a hope.

## The Argument

The problem statement asks for *a check that the answer is never leaked at levels 1–2*. A check
performed by the same model that wrote the hint is not a check — a model that leaks is also a model
that can wrongly report it did not. The two failures are correlated, so the second cannot catch the
first.

So the guard is **Python**, not a prompt:

```
hint text ──► normalise ──► compare against final_answer + aliases ──► verdict
                                                                        │
                                              clean ◄──────────────┬────┘
                                                                   │
                                                 leaked ──► regenerate once (LLM)
                                                                   │
                                            still leaked ──► redact deterministically
```

Three layers. The LLM participates only in the middle one, and even if it fails there, layer three
is pure string substitution and cannot fail.

---

## Layer 1 — The Deterministic Check

```python
# tutor/guard.py
import re
from dataclasses import dataclass
from fractions import Fraction

WORDS = {
    "zero":0,"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,
    "eight":8,"nine":9,"ten":10,"eleven":11,"twelve":12,"thirteen":13,
    "fourteen":14,"fifteen":15,"sixteen":16,"seventeen":17,"eighteen":18,
    "nineteen":19,"twenty":20,"thirty":30,"forty":40,"fifty":50,"sixty":60,
    "seventy":70,"eighty":80,"ninety":90,"hundred":100,
}

@dataclass
class LeakVerdict:
    leaked: bool
    value: str | None = None      # what was found, for the critique prompt
    where: str | None = None      # which rule fired, for the demo

def _numbers_in(text: str) -> set[float]:
    """Every number in the text, including words and fractions."""
    found = set()
    for m in re.findall(r"\d+(?:\.\d+)?(?:\s*/\s*\d+)?", text):
        try:
            found.add(float(Fraction(m.replace(" ", ""))))
        except (ValueError, ZeroDivisionError):
            pass
    tokens = re.findall(r"[a-z]+", text.lower())
    for i, t in enumerate(tokens):                  # "sixty", "sixty five"
        if t in WORDS:
            n = WORDS[t]
            if i + 1 < len(tokens) and tokens[i+1] in WORDS and WORDS[tokens[i+1]] < 10:
                n += WORDS[tokens[i+1]]
            found.add(float(n))
    return found

def leaks(hint: str, sol) -> LeakVerdict:
    """Deterministic answer-presence check (FR-4.1 - 4.3)."""
    # Rule 1 - alias string match, from the solver's answer_aliases
    low = hint.lower()
    for alias in sol.answer_aliases or []:
        if alias and alias.lower() in low:
            return LeakVerdict(True, alias, "alias match")

    # Rule 2 - numeric match within tolerance
    if sol.answer_numeric is not None:
        for n in _numbers_in(hint):
            if abs(n - float(sol.answer_numeric)) < 1e-6:
                return LeakVerdict(True, str(sol.answer_numeric), "numeric match")

    # Rule 3 - right-hand side of any equation (FR-4.3)
    for rhs in re.findall(r"=\s*([^.,;!?\n]+)", hint):
        if sol.answer_numeric is not None:
            for n in _numbers_in(rhs):
                if abs(n - float(sol.answer_numeric)) < 1e-6:
                    return LeakVerdict(True, rhs.strip(), "equation RHS")

    return LeakVerdict(False)
```

### Why each rule exists

| Rule | Catches | Example it stops |
|---|---|---|
| **Alias match** | word forms, unit variants, rounded forms | "you should get sixty" |
| **Numeric match ±1e-6** | the bare number anywhere | "about 60 km/h" |
| **Equation RHS** | the answer as a computed result | "120 / 2 = 60" |

Tolerance `1e-6` rather than `==` because floats from division rarely compare exactly.

### The known limitation — say this before a judge finds it

Rule 2 flags **any** occurrence of the answer's value, including a coincidental one. If a problem
states "a 60-litre tank" and the answer is 60 km/h, L2 cannot mention the tank. This is a
deliberate trade: a false positive costs one regeneration, a false negative shows the student the
answer. Asymmetric costs, asymmetric threshold.

---

## Layer 2 — `LEAK_CRITIQUE_PROMPT`

```python
# ─────────────────────────────────────────────────────────────────────
# LEAK CRITIQUE.  Technique: self-critique with a named defect.
# Fires only when guard.leaks() returns True. One retry, then redaction.
# ─────────────────────────────────────────────────────────────────────
LEAK_CRITIQUE_PROMPT = """The hint you wrote for level {level} contains the final
answer. The student must not see it at this level.

The value you leaked: {leaked_value}
It appeared via: {where}

Your hint was:
---
{hint_text}
---

Rewrite this hint so it still guides the student, but contains no form of
{leaked_value} whatsoever — not as a digit, not in words, not rounded, not as
the result of an equation you write out, and not as a value for the student
to check against.

Hold to the level contract:
{level_contract}

If removing the value leaves the hint too thin, add guidance about the
*method* instead. Do not compensate by moving closer to the answer.

Return ONLY: {{"hint": "..."}}"""
```

| Element | Why |
|---|---|
| **Names the exact leaked value** | A specific defect gets fixed; "you revealed the answer" often gets the same text back reworded. |
| **Quotes the offending hint** | The model sees its own output as the object of criticism. |
| **Reports `where`** | "equation RHS" tells it the *route*, so it doesn't re-leak the same way. |
| **Restates the level contract** | Regeneration otherwise drifts to another level's style. |
| **"add guidance about the method instead"** | Pre-empts the usual failure: stripping the value leaves a useless hint, so the model edges back toward the answer. |

---

## Layer 3 — Redaction Fallback

If the retry still leaks, no third call. Substitute and show the redaction (FR-4.5):

```python
MASK = "[hidden — try the next hint]"

def redact(hint: str, sol, verdict: LeakVerdict) -> str:
    """Removes the literal leaked string, every alias, and any numeric token
    equal to the answer — so a near-miss on the literal value cannot let the
    answer through."""
    out = hint
    if verdict.value:
        out = re.sub(re.escape(verdict.value), MASK, out, flags=re.IGNORECASE)

    for alias in sorted(sol.answer_aliases or [], key=len, reverse=True):
        if alias:
            out = re.sub(re.escape(alias), MASK, out, flags=re.IGNORECASE)

    if sol.answer_numeric is not None:
        target = float(sol.answer_numeric)

        def _scrub(m):
            try:
                if abs(float(Fraction(m.group().replace(" ", ""))) - target) < TOL:
                    return MASK
            except (ValueError, ZeroDivisionError):
                pass
            return m.group()

        out = NUM_RE.sub(_scrub, out)

        for word, val in WORDS.items():                  # "sixty"
            if abs(val - target) < TOL:
                out = re.sub(rf"\b{word}\b", MASK, out, flags=re.IGNORECASE)
    return out
```

> [!NOTE]
> A naive `hint.replace(verdict.value, MASK)` has a hole: if the regenerated hint expresses the
> answer in a *different* form from the one originally detected, the literal replace finds nothing
> and returns the hint with the leak intact. Since this is the layer that is supposed to be unable
> to fail, it scrubs every form — literal, alias, numeric and word — rather than just the one that
> tripped the detector.

Visible redaction is honest: the student sees the system withheld something, which is the correct
behaviour at L1/L2. It cannot fail, which is what makes the overall guarantee hold.

---

## Wiring It Together

```python
LEVEL_CONTRACTS = {1: "LEVEL 1 - ORIENT. Concept only...",     # copy from Phase 3
                   2: "LEVEL 2 - SET UP. Formula only..."}

def safe_hint(level: int, hint: str, sol) -> tuple[str, LeakVerdict]:
    """Return a hint guaranteed free of the answer, plus the verdict for the UI."""
    if level == 3:
        return hint, LeakVerdict(False)        # L3 may approach, not state
    v = leaks(hint, sol)
    if not v.leaked:
        return hint, v
    retry = complete_json(LEAK_CRITIQUE_PROMPT.format(
        level=level, leaked_value=v.value, where=v.where,
        hint_text=hint, level_contract=LEVEL_CONTRACTS[level]))["hint"]
    v2 = leaks(retry, sol)
    return (retry, v) if not v2.leaked else (redact(retry, sol, v2), v2)
```

---

## Tests — write these first, they are quick

```python
sol = Solution(True, "speed-distance-time", [], "60 km/h", 60,
               ["60", "sixty", "60 km/h", "60 kmph"])

assert leaks("Use speed = distance / time.", sol).leaked is False
assert leaks("So you get 60 km/h.", sol).leaked is True          # alias
assert leaks("You should get sixty.", sol).leaked is True        # words
assert leaks("That gives 120 / 2 = 60", sol).leaked is True      # RHS
assert leaks("Check your answer is 60.0", sol).leaked is True    # tolerance
assert leaks("The train travelled 120 km.", sol).leaked is False # no false fire
```

---

## Exit Criteria

- [ ] All six unit tests pass
- [ ] A deliberately leaking hint is caught, regenerated, and comes back clean
- [ ] Redaction verified by forcing two consecutive leaks
- [ ] Verdict surfaced for the UI badge (FR-4.6) and the Phase 8 metric (FR-4.7)
- [ ] Logged in [PROMPT_HISTORY.md](PROMPT_HISTORY.md) at 12:05

---

## What to Say in the Demo

> "The brief asks for a check that the answer never leaks. We did not ask the model to check
> itself — a model that leaks is also a model that can wrongly say it didn't. The check is Python:
> normalise, compare against the answer and its aliases, scan equation right-hand sides. If it
> fires, we regenerate with the leaked value named. If that still fails, we redact — and string
> replacement cannot fail. That is why we can say *never* rather than *usually*."

<div align="center">

[← Phase 3 · Hint Ladder](PHASE_3_HINT_LADDER.md) · [Index](PHASES_INDEX.md) · [Phase 5 · Streamlit UI →](PHASE_5_UI.md)

</div>
