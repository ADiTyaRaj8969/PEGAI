"""Tracks which parts of the study rest on executed runs.

A case study about verifying claims should be able to say where its own
numbers came from. This module reads `data/run_status.json` and produces the
notice that appears at the front of the report until every phase has actually
been run.
"""

from __future__ import annotations

import json

from .config import DATA

LABELS = {
    "phase3_baseline_executed": "Phase 3 - zero-shot baseline output",
    "phase4_role_executed": "Phase 4 - role-prompted output and its scores",
    "phase5_cot_executed": "Phase 5 - chain-of-thought claim analysis",
    "phase6_react_executed": "Phase 6 - ReAct verification matrix",
    "phase7_audit_executed": "Phase 7 - the 24-statement hallucination audit",
    "phase8_ladder_executed": "Phase 8 - V1 to V4 measurements",
    "phase9_multi_llm_executed": "Phase 9 - the three-tool comparison",
    "phase10_chain_executed": "Phase 10 - the seven-step chain transcripts",
    "sources_verified": "Appendix A - re-checking each source against its primary document",
}


def status() -> dict[str, bool]:
    raw = json.loads((DATA / "run_status.json").read_text(encoding="utf-8"))
    return {k: bool(v) for k, v in raw.items() if not k.startswith("_")}


def outstanding() -> list[str]:
    return [LABELS[k] for k, done in status().items() if not done and k in LABELS]


def is_complete() -> bool:
    return not outstanding()


def notice() -> tuple[str, str] | None:
    """The front-of-report declaration, or None once everything is executed."""
    pending = outstanding()
    if not pending:
        return None

    items = "\n".join(f"    - {item}" for item in pending)
    return (
        "Provenance and Declaration - READ BEFORE SUBMITTING",
        "The prompts, method, analysis and source list in this report are "
        "complete and ready to use. The numeric results in the phases listed "
        "below are a worked template: they are internally consistent and "
        "realistic, but they are not yet measurements you have taken.\n\n"
        "Outstanding:\n" + items + "\n\n"
        "Run each phase (`python run_all.py --measure` executes the Phase 8 "
        "ladder and the Phase 7 probe against the live API and records the "
        "transcripts; `--chain` runs Phase 10), replace the values in the "
        "matching CSV under `toolkit/data/` with what you actually observed, "
        "then set the corresponding flag in `data/run_status.json` to true and "
        "rebuild. This notice lists only what remains and disappears when "
        "nothing does. Submitting with this notice intact is honest; deleting "
        "it without doing the runs is not.",
    )
