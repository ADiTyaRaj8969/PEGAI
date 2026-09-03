#!/usr/bin/env python
"""Build the case study.

    python run_all.py            # check, render figures, build md + docx + pdf
    python run_all.py --check    # run the consistency invariants only
    python run_all.py --chain    # execute the Phase 10 prompt chain
    python run_all.py --chain --live   # ...against the live API (spends tokens)
    python run_all.py --measure  # run the Phase 8 ladder + Phase 7 probe live
"""

from __future__ import annotations

import argparse
import sys

from pe_toolkit import (
    audit,
    chain,
    charts,
    content,
    llm,
    measure,
    metrics,
    provenance,
    report,
)


def check() -> int:
    problems = audit.check_consistency()
    if problems:
        print("CONSISTENCY CHECK FAILED")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    summary = audit.summarise()
    improvement = metrics.improvement_summary()
    print("Consistency check passed.")
    print(f"  audit          : {summary.total} statements, "
          f"{summary.hallucinated} hallucinated "
          f"({summary.hallucination_rate:.1f}%)")
    print(f"  optimisation   : {improvement['v1_rate']}% -> "
          f"{improvement['v4_rate']}% "
          f"({improvement['relative_drop']}% relative reduction)")

    for name, text in [
        ("executive summary", content.EXECUTIVE_SUMMARY),
        ("background", content.BACKGROUND),
        ("key findings", content.KEY_FINDINGS),
        ("lessons learned", content.LESSONS_LEARNED),
        ("final conclusion", content.FINAL_CONCLUSION),
    ]:
        print(f"  {name:<15}: {content.word_count(text)} words")

    pending = provenance.outstanding()
    if pending:
        print(f"\n  {len(pending)} phase(s) still on the worked template:")
        for item in pending:
            print(f"    - {item}")
        print("  The report prints a Provenance notice until these are run.")
    else:
        print("\n  All phases executed - no provenance notice will be printed.")
    return 0


def run_measure() -> int:
    if not llm.credentials_available():
        print(
            "No credentials found. Export ANTHROPIC_API_KEY (or run "
            "`ant auth login`) first - --measure has to call the live API, "
            "because the whole point is to produce your own measurements."
        )
        return 1

    runner = llm.Runner(mode="live")
    print("Running the Phase 8 prompt ladder...")
    measure.run_ladder(runner)
    print("\nRunning the Phase 7 adversarial probe...")
    measure.run_probe(runner)
    return 0


def run_chain(live: bool) -> int:
    runner = llm.Runner(mode="live" if live else "auto")
    print(f"Running the Phase 10 chain in {runner.mode} mode...")
    try:
        result = chain.run(runner)
    except llm.ReplayMissing as exc:
        print(f"  {exc}")
        return 1
    for turn in result.turns:
        print(f"  {turn.key:<24} {len(turn.response):>6} chars  [{turn.mode}]")
    tokens_in, tokens_out = result.total_tokens
    if tokens_in or tokens_out:
        print(f"  tokens: {tokens_in} in / {tokens_out} out")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="run invariants only")
    parser.add_argument("--chain", action="store_true", help="execute the prompt chain")
    parser.add_argument("--measure", action="store_true", help="run the live experiments")
    parser.add_argument("--live", action="store_true", help="use the live API")
    args = parser.parse_args()

    if args.measure:
        return run_measure()
    if args.chain:
        return run_chain(args.live)

    status = check()
    if status or args.check:
        return status

    print("\nRendering figures...")
    for path in charts.render_all():
        print(f"  {path.name}")

    print("\nBuilding the report...")
    outputs = report.build_all()
    for kind, path in outputs.items():
        print(f"  {kind:<9}: {path if path else 'SKIPPED (no converter found)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
