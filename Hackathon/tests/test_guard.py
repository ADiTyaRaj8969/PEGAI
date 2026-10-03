"""Unit tests for the Phase 4 leak guard.

The guard is pure Python, so these run without an API key — which is the point:
the answer-suppression guarantee does not depend on the model.

    python -m tests.test_guard
"""
from tutor.guard import leaks, redact, LeakVerdict, MASK
from tutor.solver import Solution

SOL = Solution(
    is_math_word_problem=True,
    topic="speed-distance-time",
    steps=[],
    final_answer="60 km/h",
    answer_numeric=60,
    answer_aliases=["60", "sixty", "60 km/h", "60 kmph"],
)

CASES = [
    # (hint text, should_leak, why)
    ("Use speed = distance / time.",          False, "method only, no value"),
    ("So you get 60 km/h.",                   True,  "alias match"),
    ("You should get sixty.",                 True,  "number word"),
    ("That gives 120 / 2 = 60",               True,  "equation RHS"),
    ("Check your answer is 60.0",             True,  "float tolerance"),
    ("The train travelled 120 km.",           False, "other number, no false fire"),
    ("",                                      False, "empty hint"),
    ("Think about what connects the three.",  False, "pure concept"),
]

SOL_BIG = Solution(True, "ratio-proportion", [], "Rs 1200", 1200, ["1200", "Rs 1200"])
CASES_BIG = [
    ("So B gets 1,200 rupees.",      True,  "comma-grouped number"),
    ("Total of 1,500 is split 2:3.", False, "other grouped number, no false fire"),
]


def main() -> int:
    failed = 0

    for text, expected, why in CASES:
        got = leaks(text, SOL).leaked
        ok = got == expected
        failed += not ok
        print(f"  {'PASS' if ok else 'FAIL'}  leaks({text!r:<42}) -> {got:<5}  ({why})")

    # Redaction must remove the answer in every form, including word form.
    for text in ("So you get 60 km/h.", "You should get sixty.", "120 / 2 = 60"):
        out = redact(text, SOL, LeakVerdict(True, "60", "test"))
        still = leaks(out, SOL).leaked
        failed += still
        print(f"  {'PASS' if not still else 'FAIL'}  redact({text!r:<26}) -> {out!r}")

    # A redacted hint must actually be marked.
    out = redact("So you get 60 km/h.", SOL, LeakVerdict(True, "60", "test"))
    marked = MASK in out
    failed += not marked
    print(f"  {'PASS' if marked else 'FAIL'}  redaction is visible to the student")

    for text, expected, why in CASES_BIG:
        got = leaks(text, SOL_BIG).leaked
        failed += got != expected
        print(f"  {'PASS' if got == expected else 'FAIL'}  leaks({text!r:<42}) -> {got:<5}  ({why})")

    # Redacting a float form must not leave a stray fragment like ".0".
    out = redact("you get 60.0 now", SOL, LeakVerdict(True, "60.0", "test"))
    clean = ".0" not in out and not leaks(out, SOL).leaked
    failed += not clean
    print(f"  {'PASS' if clean else 'FAIL'}  redact float form cleanly -> {out!r}")

    # safe_hint paths, with the model stubbed out (no API calls).
    import tutor.guard as G
    real = G.complete_json
    try:
        G.complete_json = lambda *a, **k: {"hint": "Think about distance divided by time."}
        shown, v = G.safe_hint(2, "So you get 60 km/h.", SOL)
        ok = v.leaked and not leaks(shown, SOL).leaked and MASK not in shown
        failed += not ok
        print(f"  {'PASS' if ok else 'FAIL'}  leak -> regenerated clean -> {shown!r}")

        G.complete_json = lambda *a, **k: {"hint": "Honestly it is 60 km/h."}
        shown, v = G.safe_hint(2, "So you get 60 km/h.", SOL)
        ok = MASK in shown and not leaks(shown, SOL).leaked
        failed += not ok
        print(f"  {'PASS' if ok else 'FAIL'}  two leaks in a row -> redacted -> {shown!r}")

        def boom(*a, **k):
            raise RuntimeError("api down")
        G.complete_json = boom
        shown, v = G.safe_hint(1, "So you get 60 km/h.", SOL)
        ok = not leaks(shown, SOL).leaked
        failed += not ok
        print(f"  {'PASS' if ok else 'FAIL'}  regeneration fails -> redacted -> {shown!r}")

        shown, v = G.safe_hint(3, "Now divide 120 by 2.", SOL)
        ok = shown == "Now divide 120 by 2." and not v.leaked
        failed += not ok
        print(f"  {'PASS' if ok else 'FAIL'}  level 3 exempt from the check")
    finally:
        G.complete_json = real

    print("\nAll guard tests passed." if not failed else f"\n{failed} test(s) FAILED.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
