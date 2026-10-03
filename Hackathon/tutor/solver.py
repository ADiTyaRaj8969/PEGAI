"""Phase 2 — hidden solver pass.

Solves the problem privately so that downstream code knows the answer as a
*value*. Never rendered to the student (SRS FR-2.3).
"""
from dataclasses import dataclass, field

from tutor.llm import complete, complete_json
from tutor.prompts import SOLVER_SYSTEM, SOLVER_PROMPT, REPAIR_PROMPT

REQUIRED = ["is_math_word_problem", "topic", "steps", "final_answer", "answer_aliases"]


@dataclass
class Solution:
    is_math_word_problem: bool = False
    topic: str | None = None
    steps: list[dict] = field(default_factory=list)
    final_answer: str | None = None
    answer_numeric: float | None = None
    answer_aliases: list[str] = field(default_factory=list)
    reject_reason: str | None = None


def _validate(d: dict) -> None:
    missing = [k for k in REQUIRED if k not in d]
    if missing:
        raise ValueError(f"missing fields: {missing}")
    if d["is_math_word_problem"] and not d.get("steps"):
        raise ValueError("math problem returned with no steps")


def _coerce(data: dict) -> Solution:
    """Build a Solution, tolerating nulls and wrong-typed scalars."""
    num = data.get("answer_numeric")
    try:
        num = float(num) if num is not None else None
    except (TypeError, ValueError):
        num = None

    aliases = data.get("answer_aliases") or []
    if isinstance(aliases, str):                       # model sent a string
        aliases = [aliases]

    return Solution(
        is_math_word_problem=bool(data.get("is_math_word_problem")),
        topic=data.get("topic"),
        steps=data.get("steps") or [],
        final_answer=data.get("final_answer"),
        answer_numeric=num,
        answer_aliases=[str(a) for a in aliases if a],
        reject_reason=data.get("reject_reason"),
    )


_CACHE: dict[str, Solution] = {}      # per-problem, so repeat Starts never re-solve (NFR-1)


def solve(problem: str) -> Solution:
    """Solve privately. Never render the result (FR-2.3).

    One repair retry on malformed output before giving up (FR-2.4). Successful
    solutions are cached by problem text.
    """
    key = " ".join(problem.split())
    if key not in _CACHE:
        _CACHE[key] = _solve_uncached(problem)
    return _CACHE[key]


def _solve_uncached(problem: str) -> Solution:
    prompt = SOLVER_PROMPT.format(problem=problem)
    try:
        data = complete_json(prompt, system=SOLVER_SYSTEM)
        _validate(data)
    except (ValueError, KeyError) as e:
        raw = complete(prompt, system=SOLVER_SYSTEM)
        data = complete_json(
            REPAIR_PROMPT.format(error=str(e), bad_output=raw)
        )
        _validate(data)
    return _coerce(data)


def steps_text(sol: Solution) -> str:
    """Flatten the hidden solution for inclusion in a later prompt."""
    return "; ".join(
        f"{s.get('n', i)}. {s.get('action', '')} -> {s.get('result', '')}"
        for i, s in enumerate(sol.steps, 1)
    )
