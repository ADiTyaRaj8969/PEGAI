# Phase 3 — Hint Ladder

**11:45 – 12:05 · Prompt: `HINT_LADDER_PROMPT` · Techniques: few-shot exemplars + role/persona prompting**

## Goal

Three hints that are genuinely different in specificity — not one hint restated three times.

## The Hard Part

V1's instruction "progressively more helpful" is unmeasurable, so levels collapse into each other.
The fix is a **level contract**: each level gets an explicit rule for what it may contain and what
it must withhold. Then two worked exemplars show the contract applied, because a demonstrated
boundary binds far better than a described one.

| Level | May contain | Must withhold |
|---|---|---|
| **L1 — Orient** | the concept, the relationship, the question to ask | any equation, any arithmetic |
| **L2 — Set up** | the formula, which value goes where | the computed result |
| **L3 — Walk through** | every step with real numbers | the last computation |

L3 is the delicate one. It must be genuinely useful — a student who reads all three hints and
still cannot finish has been failed — while leaving the final operation to them. "Show the
substitution, stop before the evaluation."

---

## The Prompt

```python
# ─────────────────────────────────────────────────────────────────────
# HINT LADDER.  Techniques: role/persona prompting + few-shot exemplars.
# Receives the hidden solution from Phase 2 and hints *from* it.
# ─────────────────────────────────────────────────────────────────────
LADDER_SYSTEM = """You are a patient mathematics tutor. You believe a student \
who is handed the answer learns nothing, so you never state it. You ask \
questions and point at methods instead. You are warm and brief — never \
more than a few sentences, never condescending."""

HINT_LADDER_PROMPT = """A student is stuck on the problem below. You have been given
the correct solution privately. Use it to understand the problem — but the
student must never see the final answer in hints 1 or 2.

THE LEVEL CONTRACT — follow it exactly.

LEVEL 1 — ORIENT
  Name the concept, relationship, or the question the student should ask
  themselves. Mention no equation and no arithmetic result. You may refer to
  quantities by name ("the total distance") but perform no calculation.
  One or two sentences.

LEVEL 2 — SET UP
  Give the formula or equation to write, and say which value from the problem
  goes where. Do not evaluate it. After reading this the student should know
  exactly what to compute, but not what it comes to.
  Two or three sentences.

LEVEL 3 — WALK THROUGH
  Go through the method with the real numbers and stop immediately before the
  final computation. Leave that last step for the student. End by naming the
  operation they should now carry out.
  Three or four sentences.

ABSOLUTE RULE
The final answer is: {final_answer}
This value — and every equivalent form of it, including {aliases} — must not
appear in level 1 or level 2. Not as a number, not in words, not as the
result of an equation you write out, not rounded, not as a check for the
student to verify against.
In level 3 you may show the numbers that lead to it, but never the result.

─────────────────────── WORKED EXAMPLE 1 ───────────────────────
PROBLEM: A train covers 120 km in 2 hours. What is its average speed?
PRIVATE SOLUTION: distance = 120 km; time = 2 h; speed = 120 / 2; answer 60 km/h

{{"l1": "This problem ties together three quantities: how far the train goes, how long it takes, and how fast it travels. Which relationship connects those three?",
  "l2": "Use speed = distance divided by time. The distance is the 120 km the train covers, and the time is the 2 hours it takes. Write that division down.",
  "l3": "You have distance = 120 km and time = 2 hours. Substituting into the formula gives speed = 120 divided by 2. Carry out that division and attach the unit km/h to what you get."}}

─────────────────────── WORKED EXAMPLE 2 ───────────────────────
PROBLEM: A shirt costs Rs 800. The shopkeeper gives a 15% discount. What is the selling price?
PRIVATE SOLUTION: discount = 15% of 800 = 120; selling price = 800 - 120; answer Rs 680

{{"l1": "A discount lowers the price the customer actually pays. Before you can find that price, what do you need to work out about the Rs 800?",
  "l2": "There are two routes. Either find 15% of 800 and subtract it from 800, or notice the customer pays 100% - 15% = 85% of the original. Set up whichever you prefer on the Rs 800.",
  "l3": "Take the second route. The customer pays 85% of the original price, so the calculation is 0.85 multiplied by 800. Work out that multiplication and the result is the selling price in rupees."}}

─────────────────── COUNTER-EXAMPLE (never do this) ───────────────────
For the train problem, these would all be violations:
  l2: "speed = 120 / 2 = 60 km/h"        <- states the answer
  l2: "You should get 60."               <- states the answer
  l1: "The speed works out to sixty."    <- states it in words
  l3: "So the speed is 60 km/h."         <- l3 must stop before this
  l2: "Check that your answer is 60."    <- a check still reveals it

─────────────────────────── YOUR TURN ───────────────────────────
PROBLEM: {problem}
PRIVATE SOLUTION: {solution_steps}
FINAL ANSWER (never show in l1 or l2): {final_answer}

Return ONLY this JSON object:
{{"l1": "...", "l2": "...", "l3": "..."}}"""
```

---

## Line-by-Line Rationale

| Element | Why it is there |
|---|---|
| **Persona in the system message** | Role prompting. "A student handed the answer learns nothing" gives the model a *reason* to withhold, which holds up better than a bare prohibition. |
| "warm and brief… never condescending" | Without it, hint text drifts long and lecturing. |
| **Level contract before the examples** | Rule first, demonstration second — the examples then read as instances of a stated rule, not as patterns to copy loosely. |
| Explicit sentence counts per level | The only lever that reliably keeps L1 shorter than L3 and preserves the sense of a ladder. |
| "You may refer to quantities by name" | Prevents over-correction — L1 would otherwise become uselessly vague. |
| **`{aliases}` injected into the rule** | The model is told the specific strings to avoid, from Phase 2's `answer_aliases`. Concrete beats abstract. |
| "not rounded, not as a check" | Closes the two leak routes seen most often in V1 testing. |
| **Two positive exemplars** | Few-shot. One is a pattern; two is a rule. They cover different topics and different L2 shapes (single formula vs. a choice of methods). |
| Example 2 offers two routes | Teaches that L2 may present alternatives, so the tutor doesn't force its own method. |
| **Counter-example block** | Negative few-shot. Showing five *specific* violations works where "don't reveal the answer" does not — each line maps to an observed V1 failure. |
| "Return ONLY this JSON object" | Parseability, consistent with Phase 2. |

> **Note on `{{` and `}}`:** the prompt is a Python `.format()` template, so every literal brace in
> the JSON examples is doubled. Only `{problem}`, `{final_answer}`, `{aliases}` and
> `{solution_steps}` are real placeholders. Getting this wrong throws `KeyError` at runtime — it is
> the most common bug in this phase.

---

## Implementation

```python
# tutor/hints.py
from dataclasses import dataclass
from tutor.llm import complete_json
from tutor.prompts import LADDER_SYSTEM, HINT_LADDER_PROMPT
from tutor.solver import Solution

@dataclass
class Ladder:
    l1: str
    l2: str
    l3: str

def generate_ladder(problem: str, sol: Solution) -> Ladder:
    steps = "; ".join(f"{s['n']}. {s['action']} -> {s['result']}" for s in sol.steps)
    data = complete_json(
        HINT_LADDER_PROMPT.format(
            problem=problem,
            solution_steps=steps,
            final_answer=sol.final_answer,
            aliases=", ".join(f'"{a}"' for a in sol.answer_aliases),
        ),
        system=LADDER_SYSTEM,
    )
    return Ladder(l1=data["l1"], l2=data["l2"], l3=data["l3"])
```

The hints are **not yet safe to display** — Phase 4 adds the guard. Do not wire this to the UI
until that exists.

---

## Tests

Run on an unseen problem and check by eye:

```python
sol = solve("Ravi is 3 times as old as his son. In 10 years he will be twice as old. How old is Ravi now?")
lad = generate_ladder("Ravi is 3 times as old as his son...", sol)
```

| Check | Looking for |
|---|---|
| L1 has no digits from the arithmetic | Concept only |
| L2 names the equation but no result | Setup only |
| L3 shows the substitution, stops before evaluating | Walkthrough minus last step |
| L1 is shorter than L3 | The ladder actually ascends |
| None of L1/L2 contains `sol.final_answer` | Manual pre-check of what Phase 4 automates |

---

## Exit Criteria

- [ ] Three hints returned as valid JSON on all 5 samples
- [ ] Levels visibly differ in specificity — read them aloud to each other
- [ ] L3 is useful but stops short of the final computation
- [ ] `{{`/`}}` escaping verified — no `KeyError`
- [ ] Logged in [PROMPT_HISTORY.md](PROMPT_HISTORY.md) at 11:45

**Next:** [Phase 4 — Leak Guard](PHASE_4_LEAK_GUARD.md)
