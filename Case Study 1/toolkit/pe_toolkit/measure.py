"""Execute the experiments so the numbers become your own measurements.

`report.build_all()` renders the study from whatever is in `data/`. This module
is what replaces the worked template with real runs: it executes the Phase 8
prompt ladder and the Phase 7 probe against the live API, records every
transcript, and writes a worksheet with one row per generated statement for you
to verify by hand.

Verification is deliberately not automated. Asking the model to mark its own
statements is the failure this study documents - in an early attempt it
confirmed its own fabrication on the first try. The worksheet exists to make
the manual pass fast, not to replace it.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

from . import prompts
from .config import DATA
from .llm import Runner

# A generated "statement" is a bullet, a numbered item, or a sentence carrying
# a figure. Splitting is approximate on purpose - you edit the worksheet.
_ITEM = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+(.{25,})$", re.M)


def _statements(text: str) -> list[str]:
    items = [m.group(1).strip() for m in _ITEM.finditer(text)]
    if items:
        return items
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 40]


def run_ladder(runner: Runner | None = None) -> dict[str, int]:
    """Run V1..V4 and record each transcript."""
    runner = runner or Runner(mode="live")
    counts: dict[str, int] = {}

    for spec in prompts.VERSIONS:
        text = (
            spec.rendered(guardrail=prompts.GUARDRAIL)
            if "{guardrail}" in spec.text
            else spec.rendered()
        )
        turn = runner.run(f"measure_{spec.key}", text)
        found = _statements(turn.response)
        counts[spec.key] = len(found)
        print(f"  {spec.key.upper():<4} {len(found):>3} statements  -> "
              f"transcripts/measure_{spec.key}.md")

    print(
        "\nNext: verify each statement by hand, count the unsupported ones, and "
        "put the totals in data/prompt_versions.csv "
        "(statements_generated / statements_hallucinated)."
    )
    return counts


def run_probe(runner: Runner | None = None, out: Path | None = None) -> Path:
    """Run the Phase 7 adversarial probe and write a verification worksheet."""
    runner = runner or Runner(mode="live")
    out = out or DATA / "hallucination_audit_worksheet.csv"

    turn = runner.run("measure_probe", prompts.P_HALLUCINATION_PROBE.rendered())
    found = _statements(turn.response)

    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "id", "probe_category", "ai_statement", "model",
                "evidence_found", "verified", "verdict", "failure_mode",
                "failure_class", "notes",
            ]
        )
        for i, statement in enumerate(found, start=1):
            writer.writerow(
                [f"H{i:02d}", "", statement, runner and "claude-opus-5",
                 "", "", "", "", "", ""]
            )

    print(f"  {len(found)} statements -> {out}")
    print(
        "\nNext: for each row search for the underlying source, fill in\n"
        "  evidence_found  Yes / Partial / No\n"
        "  verified        Yes / Partial / No\n"
        "  verdict         Verified | Verified as scenario | Partially verified\n"
        "                  | Unverified | Hallucinated\n"
        "  failure_class   Fabricated citation or expert | Misattribution\n"
        "                  | Fabricated statistic | Unsupported projection\n"
        "then replace data/hallucination_audit.csv with the finished worksheet."
    )
    return out
