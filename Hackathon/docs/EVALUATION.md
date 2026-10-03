<div align="center">

# Evaluation

### Labelled case set, metrics, and the V1-vs-V2 comparison

[![Team](https://img.shields.io/badge/Team-5-7b2d8e?style=flat-square)](#)
[![Problem](https://img.shields.io/badge/Problem-13-0b3d62?style=flat-square)](#)
[![Cases](https://img.shields.io/badge/labelled%20cases-12-1a7f64?style=flat-square)](#)
[![Model](https://img.shields.io/badge/model-ling--3.1--flash-b35309?style=flat-square)](#)

</div>

---

Results over the labelled case set in `eval/cases.json`, run on
`inclusionai/ling-3.1-flash` via OpenRouter at `temperature=0.2`.

```bash
python -m eval.run_eval --version v1
python -m eval.run_eval --version v2
python -m eval.run_eval --compare
```

---

## Headline Result

| Metric | V1 (single prompt) | V2 (decomposed + guard) |
|---|:--:|:--:|
| **Answer Leak Rate @ L1–L2** | **0%** (0 / 10 measured) | **0%** (0 / 12 measured) |
| **Wrong-Step Localisation** | **100%** (3 / 3 measured) | **100%** (4 / 4 measured) |
| Cases lost to rate limiting | 2 | 0 |

> [!IMPORTANT]
> **Neither metric separates the two versions on this case set.** V1 did not leak, and it located
> every wrong step it managed to process. That is the honest result and it is reported as such.
>
> Reading the 100%-vs-100% as "V2 is no better" would be the wrong conclusion, but so would
> dressing the numbers up. The real difference is argued below, and it is **structural, not
> statistical**.

---

## Why V1 Scored So Well

The model behind both versions is well-behaved on school-level word problems. Asked not to reveal
the answer, it mostly complies. A representative V1 output for case 7 (`60 km/h`):

```
Hint 1: Think about the relationship between distance, time, and speed.
        What formula connects these three quantities?
Hint 2: Average speed is calculated by dividing the total distance travelled
        by the total time taken. Identify which values represent distance and
        which represent time.
Hint 3: You have a distance of 120 km and a time of 2 hours. To find the
        average speed, divide 120 by 2, and don't forget the units (km/h).
```

Clean. No leak at any level.

We verified this is a **real measurement and not a parsing failure** — a harness that silently
failed to split the hints would also report 0%. All three levels parse, and the guard was run
against each one.

---

## The Argument That Actually Separates Them

V1's 0% is a property of **this model on these twelve problems**. Nothing in V1 prevents a leak:
the entire safeguard is the sentence *"Do not reveal the final answer"*, and instruction-following
on a negative constraint is probabilistic. Change the model, the temperature, or the problem and
the number can move.

V2's 0% is a property of **the architecture**. The hint is checked against the known answer in
Python before display; if it matches, the hint is regenerated, and if that still matches, the
value is scrubbed by string substitution. There is no path from a leaked value to the screen.

| | V1 | V2 |
|---|---|---|
| Mechanism preventing a leak | an instruction | a deterministic check |
| If the model misbehaves | the leak reaches the student | caught, regenerated, then redacted |
| Evidence it holds | 12 cases happened to pass | 12 unit tests, no API key required |

The claim is not *"V2 leaks less"*. It is **V1 might not leak; V2 cannot.**

### The guard demonstrably works

`tests/test_guard.py` — 12 assertions, runs offline:

```
PASS  leaks('Use speed = distance / time.')   -> False   method only
PASS  leaks('So you get 60 km/h.')            -> True    alias match
PASS  leaks('You should get sixty.')          -> True    number word
PASS  leaks('That gives 120 / 2 = 60')        -> True    equation RHS
PASS  leaks('Check your answer is 60.0')      -> True    float tolerance
PASS  leaks('The train travelled 120 km.')    -> False   no false fire
PASS  redact(...) removes every form, and the redaction is visible
```

Those are the leaks V1 would have shown the student. The eval set simply never produced one.

---

## Secondary Metric — Wrong-Step Localisation

Both versions located every wrong step they processed, including case 10, where the error is at
**step 3** rather than step 1 — so a diagnoser that always guessed "1" would score 25%, not 100%.

| Case | Error | Expected | V1 | V2 |
|:--:|---|:--:|:--:|:--:|
| 9 | inverted the fraction | 1 | 1 | 1 |
| 10 | didn't subtract 1 before halving | 3 | 3 | 3 |
| 11 | multiplied instead of dividing | 1 | 1 | 1 |
| 12 | added times instead of rates | 1 | *rate-limited* | 1 |

The difference is in the **hint**, which the index alone does not capture. V2 is required to name
the student's actual action:

> *"You multiplied the distance by the time. Check the units that produces: km × h. Is that a unit
> of speed? What operation on 45 km and 3 hours would give you km per hour instead?"*

That hint only makes sense for this mistake. A generic *"remember speed is distance over time"*
would score identically on the index metric while teaching far less — which is the part of the
stretch challenge the number cannot measure. Read the hints, not just the indices.

---

## Methodology Notes

**Errored cases are excluded, not counted as passes.** Two V1 cases hit OpenRouter rate limits.
Dividing by the full 12 would have scored an unmeasured case as a clean one, so the denominator is
the cases that completed. V1's step accuracy is 3/3, not 3/4 — the fourth case errored, it was not
answered wrongly.

**Leak detection uses the hand-written answer** from `cases.json`, not the solver's output, so the
metric does not depend on the component being measured.

**V2 is measured twice**, before and after the guard. Both are 0%: the ladder prompt did not leak
in the first place on this set, so the guard never had to fire during evaluation.

---

## Honest Limitations

1. **The case set does not discriminate.** Twelve standard school problems were not hard enough to
   make V1 fail. A set designed to induce leaks — answers that appear naturally in the problem
   text, adversarial student messages, injection attempts — would separate the versions properly.
   That is the first thing to add with more time.
2. **One model, one temperature.** Both versions were run only on `ling-3.1-flash` at 0.2. V1's
   reliability is a property of that model, and the result may not transfer.
3. **Small n.** Twelve cases, four with seeded errors. A single flip moves the secondary metric by
   25 points.
4. **Rate limiting cost us two V1 measurements**, so the two versions were not scored over an
   identical set of completed cases.

---

<div align="center">

[Back to README](../README.md) · [Phase Index](PHASES_INDEX.md) · [Phase 8 · Evaluation](PHASE_8_EVALUATION.md)

</div>
