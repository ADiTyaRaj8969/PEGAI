"""Tests for the invariants the report depends on.

Run with:  python -m pytest tests -q      (from the toolkit directory)
       or:  python tests/test_toolkit.py  (no pytest needed)
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pe_toolkit import audit, blocks, content, datastore, document, metrics, prompts


def test_consistency_invariants_hold():
    assert audit.check_consistency() == []


def test_audit_verdicts_are_from_the_known_set():
    allowed = {
        "Verified",
        "Verified as scenario",
        "Partially verified",
        "Unverified",
        "Hallucinated",
    }
    found = set(datastore.audit()["verdict"].str.strip())
    assert found <= allowed, f"unexpected verdicts: {found - allowed}"


def test_every_hallucination_has_a_failure_class():
    frame = datastore.audit()
    bad = frame[frame["verdict"].str.strip() == "Hallucinated"]
    assert not bad.empty
    assert (bad["failure_class"].str.strip() != "").all()


def test_non_hallucinations_have_no_failure_class():
    frame = datastore.audit()
    ok = frame[frame["verdict"].str.strip() != "Hallucinated"]
    assert (ok["failure_class"].str.strip() == "").all()


def test_audit_counts_partition_the_table():
    summary = audit.summarise()
    assert (
        summary.verified
        + summary.partially_verified
        + summary.unverified
        + summary.hallucinated
        == summary.total
    )


def test_failure_classes_sum_to_the_hallucination_count():
    assert int(audit.failure_modes()["Count"].sum()) == audit.summarise().hallucinated


def test_hallucination_rate_falls_monotonically():
    rates = metrics.version_metrics()["hallucination_rate"].tolist()
    assert rates == sorted(rates, reverse=True)
    assert rates[0] > rates[-1]


def test_source_collection_requirements_are_met():
    counts = datastore.source_counts()
    assert (counts["Met"] == "Yes").all(), counts[counts["Met"] != "Yes"].to_string()


def test_reliability_scores_are_in_range():
    for frame, column in (
        (datastore.sources(), "reliability"),
        (datastore.reliability(), "reliability"),
    ):
        values = frame[column].astype(int)
        assert values.between(1, 5).all()


def test_claim_confidence_is_a_percentage():
    values = datastore.claims()["confidence"].astype(int)
    assert values.between(0, 100).all()


def test_word_counts_are_near_the_manual_targets():
    targets = {
        "executive summary": (content.EXECUTIVE_SUMMARY, 300),
        "background": (content.BACKGROUND, 300),
        "key findings": (content.KEY_FINDINGS, 500),
        "lessons learned": (content.LESSONS_LEARNED, 300),
        "final conclusion": (content.FINAL_CONCLUSION, 300),
    }
    for name, (text, target) in targets.items():
        count = content.word_count(text)
        # The manual states a target, not a hard limit. Allow +/-25%.
        assert 0.75 * target <= count <= 1.25 * target, f"{name}: {count} vs {target}"


def test_every_prompt_renders_without_unfilled_placeholders():
    substitutions = {
        "claim": "sample claim",
        "guardrail": prompts.GUARDRAIL,
        "sources": "sample sources",
        "claims": "sample claims",
        "verified": "sample verified material",
    }
    for key, spec in prompts.ALL_PROMPTS.items():
        needed = {
            name
            for name in substitutions
            if "{" + name + "}" in spec.text
        }
        rendered = spec.rendered(**{k: substitutions[k] for k in needed})
        assert "{" not in rendered.replace("{topic}", ""), f"{key} left a placeholder"
        assert rendered.strip()


def test_chain_covers_all_seven_workflow_steps():
    from pe_toolkit import chain

    rows = chain.workflow_table()
    assert len(rows) == 7
    assert [r["Step"] for r in rows] == [str(i) for i in range(1, 8)]
    assert all(r["Prompt used"].strip() for r in rows)


def test_document_builds_and_contains_every_phase():
    doc = document.build()
    headings = [b.text for b in doc.blocks if isinstance(b, blocks.Heading)]
    for phase in range(1, 13):
        assert any(f"Phase {phase} " in h for h in headings), f"missing Phase {phase}"
    assert any("Appendix A" in h for h in headings)
    assert any("Appendix B" in h for h in headings)
    assert any("Rubric" in h for h in headings)


def test_no_table_in_the_document_is_empty():
    for block in document.build().blocks:
        if isinstance(block, blocks.Table):
            assert not block.frame.empty
        if isinstance(block, blocks.KeyValue):
            assert block.pairs


def test_bold_splitter_round_trips():
    parts = blocks.split_bold("a **b** c")
    assert parts == [("a ", False), ("b", True), (" c", False)]
    assert "".join(text for text, _ in parts) == "a b c"


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS  {name}")
            except AssertionError as exc:
                failures += 1
                print(f"FAIL  {name}: {exc}")
    print(f"\n{failures} failure(s)")
    sys.exit(1 if failures else 0)
