"""Adversarial comparison — the conditions where V1 and V2 actually differ.

The 12-case set in cases.json did not separate the versions: V1 never leaked
on ordinary school problems. These four inputs probe the places where an
instruction-only safeguard and a deterministic one come apart.

    python -m eval.run_adversarial
"""
import json
import os

from tutor.llm import LLMError
from tutor.solver import solve, Solution
from tutor.hints import generate_v1, generate_ladder, parse_v1
from tutor.guard import leaks, safe_hint

CASES = os.path.join(os.path.dirname(__file__), "adversarial.json")


def _truth(case: dict) -> Solution:
    if case["answer"] is None:
        return Solution(is_math_word_problem=False)
    num = case["answer_numeric"]
    return Solution(
        is_math_word_problem=True,
        final_answer=str(case["answer"]),
        answer_numeric=float(num) if num is not None else None,
        answer_aliases=[str(case["answer"]), str(num), str(int(num))],
    )


def main() -> None:
    cases = json.load(open(CASES, encoding="utf-8"))
    print(f"{'id':<4}{'kind':<18}{'V1':<28}{'V2':<28}")
    print("-" * 78)

    for c in cases:
        truth = _truth(c)

        # ── V1 ───────────────────────────────────────────────────────
        try:
            parts = parse_v1(generate_v1(c["problem"]))
            if c["answer"] is None:
                v1 = "produced hints anyway" if parts else "no hints"
            else:
                bad = [l for l in (1, 2) if l in parts and leaks(parts[l], truth).leaked]
                v1 = f"LEAKED at L{bad}" if bad else "no leak"
        except LLMError as e:
            v1 = f"error: {str(e)[:18]}"

        # ── V2 ───────────────────────────────────────────────────────
        try:
            sol = solve(c["problem"])
            if not sol.is_math_word_problem:
                v2 = "declined (off-topic)"
            else:
                lad = generate_ladder(c["problem"], sol)
                bad, fired = [], []
                for lvl in (1, 2):
                    raw = lad.level(lvl)
                    if leaks(raw, truth).leaked:
                        fired.append(lvl)
                    shown, _ = safe_hint(lvl, raw, sol)
                    if leaks(shown, truth).leaked:
                        bad.append(lvl)
                v2 = f"LEAKED at L{bad}" if bad else "no leak"
                if fired:
                    v2 += f" (guard fired L{fired})"
        except LLMError as e:
            v2 = f"error: {str(e)[:18]}"

        print(f"{c['id']:<4}{c['kind']:<18}{v1:<28}{v2:<28}")

    print("\nExpectations:")
    for c in cases:
        print(f"  {c['id']}  {c['expect']}")


if __name__ == "__main__":
    main()
