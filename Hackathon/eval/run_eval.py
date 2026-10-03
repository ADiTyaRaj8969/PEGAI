"""Phase 8 — the evaluation harness.

Primary metric   Answer Leak Rate @ L1-L2        (lower is better, target 0%)
Secondary metric Wrong-Step Localisation Accuracy (higher is better)

Usage:
    python -m eval.run_eval --version v1
    python -m eval.run_eval --version v2
    python -m eval.run_eval --compare
"""
import argparse
import json
import os
import re
import sys

from tutor.llm import complete, LLMError
from tutor.solver import solve, Solution
from tutor.hints import generate_v1, generate_ladder, parse_v1
from tutor.guard import leaks, safe_hint
from tutor.diagnose import diagnose
from tutor.prompts import V1_DIAGNOSE_PROMPT

CASES = os.path.join(os.path.dirname(__file__), "cases.json")


def _case_solution(case: dict) -> Solution:
    """Ground truth from the label, so the metric never depends on the solver.

    The solver is still called for the hint pipeline, but leak detection is
    judged against the hand-written answer in cases.json.
    """
    ans = str(case["answer"])
    num = case.get("answer_numeric")
    aliases = {ans, str(num)}
    if num is not None and float(num) == int(num):
        aliases.add(str(int(num)))
    return Solution(
        is_math_word_problem=True,
        topic=case["topic"],
        steps=[],
        final_answer=ans,
        answer_numeric=float(num) if num is not None else None,
        answer_aliases=[a for a in aliases if a and a != "None"],
    )


# ── leak measurement ─────────────────────────────────────────────────
def leak_v1(case, truth):
    """Levels 1-2 of the baseline's free text that contain the answer."""
    parts = parse_v1(generate_v1(case["problem"]))
    return [lvl for lvl in (1, 2) if lvl in parts and leaks(parts[lvl], truth).leaked]


def leak_v2(case, truth, sol):
    """Two readings: before the guard (prompt only) and as displayed.

    Reporting both matters. 'As displayed' is the honest user-facing number,
    but the guard both produces and judges that output, so on its own it is
    partly tautological. 'Before the guard' isolates what the prompt
    engineering achieved.
    """
    lad = generate_ladder(case["problem"], sol)
    pre, post = [], []
    for lvl in (1, 2):
        raw = lad.level(lvl)
        if leaks(raw, truth).leaked:
            pre.append(lvl)
        shown, _ = safe_hint(lvl, raw, sol)
        if leaks(shown, truth).leaked:
            post.append(lvl)
    return pre, post


# ── step localisation ────────────────────────────────────────────────
def step_v1(case):
    raw = complete(V1_DIAGNOSE_PROMPT.format(
        problem=case["problem"], working=case["working"]))
    m = re.search(r"wrong step\s*:?\s*(\d+)", raw, re.I)
    return int(m.group(1)) if m else None


def step_v2(case, sol):
    return diagnose(case["problem"], case["working"], sol).first_wrong_step


# ── driver ───────────────────────────────────────────────────────────
def run(version: str) -> dict:
    cases = json.load(open(CASES, encoding="utf-8"))
    rows, errors = [], 0
    leaked = pre_leaked = 0
    step_hits = step_total = 0

    for c in cases:
        truth = _case_solution(c)
        row = {"id": c["id"], "topic": c["topic"]}
        try:
            if version == "v1":
                lv = leak_v1(c, truth)
                row["leaked_levels"] = lv
                leaked += bool(lv)
            else:
                sol = solve(c["problem"])
                pre, post = leak_v2(c, truth, sol)
                row["leaked_pre_guard"] = pre
                row["leaked_levels"] = post
                pre_leaked += bool(pre)
                leaked += bool(post)

            if "wrong_step" in c:
                got = step_v1(c) if version == "v1" else step_v2(c, sol)
                # Counted only after the call returns. Incrementing before it
                # would score a rate-limit error as a wrong answer.
                step_total += 1
                hit = got == c["wrong_step"]
                step_hits += hit
                row.update(expected_step=c["wrong_step"], got_step=got, step_correct=hit)
        except (LLMError, ValueError, KeyError) as e:
            errors += 1
            row["error"] = str(e)[:120]

        rows.append(row)
        print(f"{c['id']:>3}  {c['topic']:<22} "
              f"leak={row.get('leaked_levels', '-') or '-':<8} "
              f"step={row.get('step_correct', '-')}"
              + (f"  ERROR {row['error']}" if "error" in row else ""))

    # A case that errored was not measured. Dividing by the full case count
    # would silently treat an unmeasured case as a clean one and understate
    # the rate, so the denominator is the cases that actually completed.
    n = len(cases)
    measured = n - errors
    rate = (lambda k: round(100 * k / measured, 1) if measured else None)

    summary = {
        "version": version,
        "cases": n,
        "measured": measured,
        "errors": errors,
        "leak_cases": leaked,
        "leak_rate": rate(leaked),
        "step_total": step_total,
        "step_hits": step_hits,
        "step_accuracy": round(100 * step_hits / step_total, 1) if step_total else None,
    }
    if version == "v2":
        summary["pre_guard_leak_cases"] = pre_leaked
        summary["pre_guard_leak_rate"] = rate(pre_leaked)

    print(f"\n  Measured          : {measured}/{n} cases ({errors} errored)")
    print(f"  Leak Rate @ L1-L2 : {leaked}/{measured} = {summary['leak_rate']}%")
    if version == "v2":
        print(f"  ...before guard   : {pre_leaked}/{measured} = {summary['pre_guard_leak_rate']}%")
    if step_total:
        print(f"  Step Localisation : {step_hits}/{step_total} = {summary['step_accuracy']}%")

    out = os.path.join(os.path.dirname(__file__), f"results_{version}.json")
    json.dump({"summary": summary, "rows": rows}, open(out, "w"), indent=2)
    print(f"  Written to {out}")
    return summary


def compare() -> None:
    """Merge both result files into the markdown tables in docs/EVALUATION.md."""
    loaded = {}
    for v in ("v1", "v2"):
        p = os.path.join(os.path.dirname(__file__), f"results_{v}.json")
        if not os.path.exists(p):
            sys.exit(f"Missing {p}. Run:  python -m eval.run_eval --version {v}")
        loaded[v] = json.load(open(p))["summary"]

    v1, v2 = loaded["v1"], loaded["v2"]
    print("\n| Measurement | Result |")
    print("|---|:--:|")
    print(f"| V1 — one prompt | {v1['leak_rate']}% |")
    print(f"| V2 before the guard — prompt only | {v2['pre_guard_leak_rate']}% |")
    print(f"| V2 as displayed — prompt + guard | {v2['leak_rate']}% |")
    print("\n| Version | Step Localisation Accuracy |")
    print("|---|:--:|")
    print(f"| V1 | {v1['step_accuracy']}% |")
    print(f"| V2 | {v2['step_accuracy']}% |")
    print("\nPaste these into docs/EVALUATION.md.")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--version", choices=["v1", "v2"])
    p.add_argument("--compare", action="store_true")
    a = p.parse_args()
    if a.compare:
        compare()
    elif a.version:
        run(a.version)
    else:
        p.error("pass --version v1|v2 or --compare")
