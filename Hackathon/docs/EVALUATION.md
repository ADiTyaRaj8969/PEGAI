<div align="center">

# Evaluation

### Labelled case set, metrics, and the V1-vs-V2 comparison

[![Team](https://img.shields.io/badge/Team-5-7b2d8e?style=flat-square)](#)
[![Problem](https://img.shields.io/badge/Problem-13-0b3d62?style=flat-square)](#)
[![Cases](https://img.shields.io/badge/labelled%20cases-12-1a7f64?style=flat-square)](#)
[![Metrics](https://img.shields.io/badge/metrics-2-b35309?style=flat-square)](#)

</div>

---

Results over the labelled case set in `eval/cases.json`. Regenerate with:

```bash
python -m eval.run_eval --version v1
python -m eval.run_eval --version v2
python -m eval.run_eval --compare      # rewrites the tables below
```

> [!NOTE]
> Runs use `temperature=0.2` and a fixed case order so the two versions are comparable
> ([SRS](SRS.md) NFR-7).

---

## Case Set

12 labelled cases. Each carries the problem text, ground-truth answer, topic, and — for the
diagnosis cases — a student working with the index of the first wrong step.

| # | Topic | Seeded wrong step | Wrong step index |
|:--:|---|:--:|:--:|
| 1 | arithmetic | | |
| 2 | percentage | | |
| 3 | ratio-proportion | | |
| 4 | linear-equation | | |
| 5 | age | | |
| 6 | work-rate | | |
| 7 | speed-distance-time | | |
| 8 | geometry-area | | |
| 9 | percentage | yes | |
| 10 | linear-equation | yes | |
| 11 | speed-distance-time | yes | |
| 12 | work-rate | yes | |

---

## Primary Metric — Answer Leak Rate @ L1–L2

Percentage of cases where the final answer appears in hint level 1 or level 2, judged by the
deterministic guard in `tutor/guard.py`.

**Lower is better. Target: 0%.**

| Version | Cases | Leaks @ L1 | Leaks @ L2 | **Leak Rate** |
|---|:--:|:--:|:--:|:--:|
| **V1** — single zero-shot prompt | 12 | _TBD_ | _TBD_ | _TBD_ |
| **V2** — decomposed + few-shot + guard | 12 | _TBD_ | _TBD_ | _TBD_ |

### The Three-Number Version

> [!IMPORTANT]
> Report **three** numbers, not two. Measuring V2 after the guard gives 0%, but that figure is
> partly tautological — the guard both produces and judges the output. The middle row isolates
> what the prompt engineering achieved on its own.

| Measurement | How it is obtained | Result |
|---|---|:--:|
| V1 — one prompt | `eval_v1` | _TBD_ |
| V2 **before** the guard — prompt only | `leaks()` on `lad.l1` / `lad.l2` directly | _TBD_ |
| V2 **as displayed** — prompt + guard | `eval_v2`, post-`safe_hint` | _TBD_ |

---

## Secondary Metric — Wrong-Step Localisation Accuracy

Percentage of the seeded-error cases where the reported first-wrong-step index matches the label.

**Higher is better.**

| Version | Seeded cases | Correct index | **Accuracy** |
|---|:--:|:--:|:--:|
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

> [!TIP]
> Record the concrete V1 leaks here — judges ask for them, and a verbatim example is far more
> persuasive than a percentage.

| Case | Version | Level | Leaked text | Ground-truth answer |
|:--:|:--:|:--:|---|---|
| | | | | |

---

<div align="center">

[Back to README](../README.md) · [Phase Index](PHASES_INDEX.md) · [Phase 8 · Evaluation](PHASE_8_EVALUATION.md)

</div>
