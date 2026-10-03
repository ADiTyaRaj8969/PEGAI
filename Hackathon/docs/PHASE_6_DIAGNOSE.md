<div align="center">

# Phase 6 · Wrong-Step Detection

[![Time](https://img.shields.io/badge/12%3A50%20–%2013%3A15-0b3d62?style=flat-square)](#)
[![Prompt](https://img.shields.io/badge/prompt-DIAGNOSE__PROMPT-1a7f64?style=flat-square)](#)
[![Technique](https://img.shields.io/badge/technique-decomposition%20%2B%20comparison-7b2d8e?style=flat-square)](#)
[![Scope](https://img.shields.io/badge/stretch%20challenge-MANDATORY-b30000?style=flat-square)](#)

</div>

---

> [!IMPORTANT]
> This is the **stretch challenge**, and the brief marks it mandatory — not optional.

## Goal

> Detect the specific wrong step in a student's working and give a targeted hint instead of a
> generic one.

Both halves are graded. Finding the step is the easier half; the targeted hint is where most
implementations quietly fall back to restating the method.

## Why This Is Harder Than It Looks

Three traps:

**1. Error propagation.** A student who errs at step 2 will have steps 3, 4 and 5 all "wrong" as
consequences. Reporting three errors is unhelpful and inaccurate — they made *one* mistake. Only
the first matters (FR-5.3).

**2. Alternative valid methods.** The private solution uses one method; the student may use
another that works. Marking a correct alternative as an error destroys trust in the tutor
instantly.

**3. Generic hints disguised as targeted ones.** "Remember that speed is distance over time" is
generic. "You multiplied where you should have divided — check what unit km × h gives you" is
targeted. The difference is whether the hint names *what the student actually did*.

---

## The Prompt

```python
# ─────────────────────────────────────────────────────────────────────
# DIAGNOSE.  Techniques: decomposition + comparative reasoning.
# Compares student working against the Phase 2 hidden solution.
# Output is routed through the Phase 4 leak guard before display.
# ─────────────────────────────────────────────────────────────────────
DIAGNOSE_SYSTEM = """You are a patient mathematics tutor reading a student's \
written work. You look for the one place their reasoning first goes wrong, and \
you help them see it themselves rather than correcting it for them."""

DIAGNOSE_PROMPT = """A student has attempted the problem below. Find the FIRST line
where their reasoning goes wrong.

PROBLEM
{problem}

CORRECT SOLUTION (private — the student must not see this)
{solution_steps}
CORRECT FINAL ANSWER (private): {final_answer}

THE STUDENT'S WORKING, one step per line
{working}

HOW TO JUDGE

1. Read the lines in order. For each, ask two questions: is the mathematics
   itself correct, and does it follow from the student's own earlier lines?
   A line can be arithmetically right and still wrong because it applies the
   wrong method.

2. Stop at the first line that fails. Lines after it that are wrong only
   because they inherit this mistake are NOT separate errors. The student
   made one mistake, not three. Report only the first.

3. A different valid method is not an error. If the student is solving this a
   way that works but differs from the private solution above, follow their
   method and judge them against it. Only call it wrong if it cannot reach a
   correct answer.

4. If every line is correct but the work stops before the answer, set status
   to "incomplete" and first_wrong_step to null.

5. If every line is correct and the answer is reached, set status to
   "correct" and first_wrong_step to null.

WRITING THE TARGETED HINT

Name what the student actually did. A hint that could be pasted under any
wrong answer is a failure — this one must only make sense for this mistake.

  Generic (wrong):  "Remember that speed is distance divided by time."
  Targeted (right): "You multiplied the distance by the time. Look at the
                     units that gives you — km x h. Is that a speed? What
                     operation would give you km per hour instead?"

Do not give them the corrected line. Do not state the final answer or any
part of it. Ask a question that leads them to spot it themselves.

Return ONLY this JSON object:
{{
  "status": "error" | "incomplete" | "correct",
  "first_wrong_step": integer or null,
  "what_they_did": string,
  "why_wrong": string,
  "targeted_hint": string
}}"""
```

---

## Line-by-Line Rationale

| Rule | Why it is there |
|---|---|
| "is the mathematics correct, **and** does it follow from their earlier lines" | Two distinct failure modes. Without both, method errors with clean arithmetic slip through. |
| "A line can be arithmetically right and still wrong" | Names the case explicitly; models over-weight arithmetic checking. |
| **"Stop at the first line that fails"** | FR-5.2. Models list every discrepancy unless told to stop. |
| **"one mistake, not three"** | FR-5.3 in plain words. This phrasing works better than "ignore propagated errors" — it frames it from the student's side. |
| **"A different valid method is not an error"** | Trap 2. The model anchors hard on the private solution without this. |
| "judge them against **their** method" | Tells it what to do instead, not just what to avoid. |
| `status` with three values | Separates the three outcomes (FR-5.2, 5.5, 5.6) so the UI branches cleanly. |
| `what_they_did` as its own field | Forces the model to *articulate* the student's action before critiquing it — a small chain-of-thought that measurably improves hint specificity. |
| **The generic/targeted example pair** | Few-shot on the quality bar. Describing "targeted" does not work; showing the contrast does. |
| "could be pasted under any wrong answer is a failure" | A test the model can apply to its own draft. |
| "Do not state the final answer" | The output still goes through the leak guard (FR-5.7) — belt and braces. |

### On `what_they_did`

Worth a sentence in the demo. Asking for a plain-language restatement of the student's action
*before* the critique makes the model commit to an interpretation first. Hints get noticeably more
specific — it cannot write "remember the formula" after writing "they multiplied distance by time."

---

## Implementation

```python
# tutor/diagnose.py
from dataclasses import dataclass
from tutor.llm import complete_json
from tutor.prompts import DIAGNOSE_SYSTEM, DIAGNOSE_PROMPT
from tutor.guard import leaks, redact

@dataclass
class Diagnosis:
    status: str                    # "error" | "incomplete" | "correct"
    first_wrong_step: int | None
    what_they_did: str
    why_wrong: str
    targeted_hint: str

def diagnose(problem: str, working: str, sol) -> Diagnosis:
    lines = [l.strip() for l in working.splitlines() if l.strip()]
    numbered = "\n".join(f"{i}. {l}" for i, l in enumerate(lines, 1))
    steps = "; ".join(f"{s['n']}. {s['action']} -> {s['result']}" for s in sol.steps)

    d = complete_json(DIAGNOSE_PROMPT.format(
        problem=problem, solution_steps=steps,
        final_answer=sol.final_answer, working=numbered,
    ), system=DIAGNOSE_SYSTEM)

    hint = d["targeted_hint"]
    v = leaks(hint, sol)                      # FR-5.7
    if v.leaked:
        hint = redact(hint, v)
    return Diagnosis(d["status"], d.get("first_wrong_step"),
                     d.get("what_they_did", ""), d.get("why_wrong", ""), hint)
```

Renumbering the student's lines server-side matters: students number inconsistently or not at all,
and `first_wrong_step` has to index something the UI can highlight.

---

## Tests

```python
sol = solve("A train covers 120 km in 2 hours. What is its average speed?")

# Trap 1 - error at step 1, propagated into step 2
d = diagnose(problem, "speed = distance x time\nspeed = 120 x 2 = 240", sol)
assert d.status == "error" and d.first_wrong_step == 1      # not 2, not both

# Trap 2 - a valid alternative method
d = diagnose(problem, "in 1 hour it goes half of 120\nthat is 60 km", sol)
assert d.status == "correct"

# Correct but unfinished
d = diagnose(problem, "speed = distance / time", sol)
assert d.status == "incomplete"

# Trap 3 - hint specificity, checked by eye
d = diagnose(problem, "speed = 120 x 2 = 240", sol)
assert "multipl" in d.targeted_hint.lower()                 # names the actual action
```

The last check is crude but catches the common regression: the hint drifting back to a generic
restatement of the formula.

---

## Exit Criteria

- [ ] A working with an error at line 2 reports **2**, not 1 or 3
- [ ] Propagated errors are not double-reported
- [ ] A valid alternative method returns `status: "correct"`
- [ ] Incomplete and fully-correct cases both handled
- [ ] The targeted hint names the student's actual action, not the general method
- [ ] Hint passes the leak guard
- [ ] Logged in [PROMPT_HISTORY.md](PROMPT_HISTORY.md) at 12:50

<div align="center">

[← Phase 5 · Streamlit UI](PHASE_5_UI.md) · [Index](PHASES_INDEX.md) · [Phase 7 · Guardrails →](PHASE_7_GUARDRAILS.md)

</div>
