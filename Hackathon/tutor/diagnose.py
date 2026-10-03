"""Phase 6 — wrong-step detection (the stretch challenge).

Finds the FIRST line where the student's reasoning fails and returns a hint
aimed at that specific mistake, not a restatement of the method.
"""
from dataclasses import dataclass

from tutor.llm import complete_json
from tutor.prompts import DIAGNOSE_SYSTEM, DIAGNOSE_PROMPT
from tutor.solver import Solution, steps_text
from tutor.guard import leaks, redact


@dataclass
class Diagnosis:
    status: str                      # "error" | "incomplete" | "correct"
    first_wrong_step: int | None
    what_they_did: str
    why_wrong: str
    targeted_hint: str


def diagnose(problem: str, working: str, sol: Solution) -> Diagnosis:
    lines = [l.strip() for l in working.splitlines() if l.strip()]
    numbered = "\n".join(f"{i}. {l}" for i, l in enumerate(lines, 1))

    d = complete_json(
        DIAGNOSE_PROMPT.format(
            problem=problem,
            solution_steps=steps_text(sol),
            final_answer=sol.final_answer,
            working=numbered,
        ),
        system=DIAGNOSE_SYSTEM,
    )

    step = d.get("first_wrong_step")
    try:
        step = int(step) if step is not None else None
    except (TypeError, ValueError):
        step = None

    # `.get(k, "")` is not enough: the model sends explicit nulls for fields it
    # considers inapplicable (e.g. targeted_hint when the work is correct),
    # and `.get` only substitutes the default when the key is absent.
    hint = d.get("targeted_hint") or ""
    v = leaks(hint, sol)                              # FR-5.7
    if v.leaked:
        hint = redact(hint, sol, v)

    status = d.get("status") or "error"
    if status not in ("error", "incomplete", "correct"):
        status = "error"

    return Diagnosis(
        status=status,
        first_wrong_step=step,
        what_they_did=d.get("what_they_did") or "",
        why_wrong=d.get("why_wrong") or "",
        targeted_hint=hint,
    )
