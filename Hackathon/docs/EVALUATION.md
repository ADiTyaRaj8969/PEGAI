# Evaluation — Hint-Based Math Tutor

**Team 5 · Problem 13 · 3 October 2026**

Results over the labelled case set in `eval/cases.json`. Regenerate with:

```bash
python -m eval.run_eval --version v1
python -m eval.run_eval --version v2
python -m eval.run_eval --compare      # rewrites the table below
```

Runs use temperature 0.2 and a fixed case order so the two versions are comparable (NFR-7).

---

## Case Set

12 labelled cases. Each carries the problem text, ground-truth answer, topic, and — for the
diagnosis cases — a student working with the index of the first wrong step.

| # | Topic | Has seeded wrong step | Wrong step index |
|---|---|---|---|
| 1 | arithmetic | | |
| 2 | percentage | | |
| 3 | ratio-proportion | | |
| 4 | linear-equation | | |
| 5 | age | | |
| 6 | work-rate | | |
| 7 | speed-distance-time | | |
| 8 | geometry-area | | |
| 9 | percentage | ✓ | |
| 10 | linear-equation | ✓ | |
| 11 | speed-distance-time | ✓ | |
| 12 | work-rate | ✓ | |

---

## Primary Metric — Answer Leak Rate @ L1–L2

Percentage of cases where the final answer appears in hint level 1 or level 2, judged by the
deterministic guard in `tutor/guard.py`. **Lower is better. Target: 0%.**

| Version | Cases | Leaks @ L1 | Leaks @ L2 | **Leak Rate** |
|---|---|---|---|---|
| **V1** — single zero-shot prompt | 12 | _TBD_ | _TBD_ | _TBD_ |
| **V2** — decomposed + few-shot + guard | 12 | _TBD_ | _TBD_ | _TBD_ |

---

## Secondary Metric — Wrong-Step Localisation Accuracy

Percentage of the seeded-error cases where the reported first-wrong-step index matches the label.
**Higher is better.**

| Version | Seeded cases | Correct index | **Accuracy** |
|---|---|---|---|
| **V1** | 4 | _TBD_ | _TBD_ |
| **V2** | 4 | _TBD_ | _TBD_ |

---

## What Changed Between V1 and V2

| Change | Technique | Expected effect |
|---|---|---|
| Split one prompt into solve → hint → verify | Decomposition | Answer is known before hinting, so suppression is checkable |
| Added 2 exemplars to the ladder prompt | Few-shot | Levels become distinct in specificity |
| Added the tutor persona | Role prompting | Fewer direct answers, more Socratic phrasing |
| Added the deterministic guard + regenerate | Self-critique | Leaks caught in code, not left to model compliance |

---

## Observed Failure Examples

Record the concrete V1 leaks here — judges ask for them.

| Case | Version | Level | Leaked text | Ground-truth answer |
|---|---|---|---|---|
| | | | | |
