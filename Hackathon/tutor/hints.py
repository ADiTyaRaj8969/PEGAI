"""Phases 1 and 3 — the baseline and the hint ladder."""
from dataclasses import dataclass

from tutor.llm import complete, complete_json
from tutor.prompts import (
    V1_SINGLE_PROMPT, LADDER_SYSTEM, HINT_LADDER_PROMPT,
)
from tutor.solver import Solution, steps_text


@dataclass
class Ladder:
    l1: str
    l2: str
    l3: str

    def level(self, n: int) -> str:
        return getattr(self, f"l{n}")


# ── Phase 1 ──────────────────────────────────────────────────────────
def generate_v1(problem: str) -> str:
    """Baseline: one call, raw text out, no guard. Kept for comparison."""
    return complete(V1_SINGLE_PROMPT.format(problem=problem), temperature=0.2)


def parse_v1(text: str) -> dict[int, str]:
    """Split the baseline's free text into levels so it can be measured."""
    parts: dict[int, str] = {}
    for lvl in (1, 2, 3):
        marker = f"Hint {lvl}:"
        if marker not in text:
            continue
        rest = text.split(marker, 1)[1]
        nxt = f"Hint {lvl + 1}:"
        parts[lvl] = (rest.split(nxt)[0] if nxt in rest else rest).strip()
    return parts


# ── Phase 3 ──────────────────────────────────────────────────────────
def generate_ladder(problem: str, sol: Solution) -> Ladder:
    """Three hints of increasing specificity, written from the hidden solution.

    NOT yet safe to display — route each level through guard.safe_hint first.
    """
    data = complete_json(
        HINT_LADDER_PROMPT.format(
            problem=problem,
            solution_steps=steps_text(sol),
            final_answer=sol.final_answer,
            aliases=", ".join(f'"{a}"' for a in sol.answer_aliases),
        ),
        system=LADDER_SYSTEM,
    )
    return Ladder(l1=data["l1"], l2=data["l2"], l3=data["l3"])
