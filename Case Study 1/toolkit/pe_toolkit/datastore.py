"""Loaders for the evidence base.

The CSVs under `data/` are the single source of truth. Every table, every
figure and every number in the generated report comes through this module, so
the document cannot disagree with the data.
"""

from __future__ import annotations

import pandas as pd

from .config import DATA

_EXPECTED = {
    "sources": {"id", "source_type", "title", "url", "reliability"},
    "claims": {"id", "claim", "verdict", "confidence"},
    "hallucination_audit": {
        "id",
        "ai_statement",
        "verdict",
        "failure_mode",
        "failure_class",
        "probe_category",
    },
    "prompt_versions": {"version", "statements_generated", "statements_hallucinated"},
    "llm_comparison": {"criterion", "claude_opus_5", "chatgpt", "perplexity"},
    "reliability": {"source_type", "reliability", "reason"},
    "bias": {"source_id", "bias_type", "ai_detected", "final_assessment"},
    "contradictions": {"id", "contested_point", "conflict_found", "resolution"},
}


def _load(name: str) -> pd.DataFrame:
    path = DATA / f"{name}.csv"
    if not path.exists():
        raise FileNotFoundError(f"missing evidence file: {path}")

    frame = pd.read_csv(path, keep_default_na=False)
    missing = _EXPECTED[name] - set(frame.columns)
    if missing:
        raise ValueError(f"{path.name} is missing columns: {sorted(missing)}")
    return frame


def sources() -> pd.DataFrame:
    return _load("sources")


def claims() -> pd.DataFrame:
    return _load("claims")


def audit() -> pd.DataFrame:
    return _load("hallucination_audit")


def prompt_versions() -> pd.DataFrame:
    return _load("prompt_versions")


def llm_comparison() -> pd.DataFrame:
    return _load("llm_comparison")


def reliability() -> pd.DataFrame:
    return _load("reliability")


def bias() -> pd.DataFrame:
    return _load("bias")


def contradictions() -> pd.DataFrame:
    return _load("contradictions")


def source_counts() -> pd.DataFrame:
    """Phase 2 collection table: required vs actually collected."""
    required = {
        "Official": 2,
        "News": 4,
        "Research": 2,
        "AI Response": 3,
        "Public Discussion": 2,
        "Corporate": 0,
    }
    collected = sources()["source_type"].value_counts().to_dict()
    return pd.DataFrame(
        [
            {
                "Source Type": kind,
                "Required": n,
                "Collected": collected.get(kind, 0),
                "Met": "Yes" if collected.get(kind, 0) >= n else "NO",
            }
            for kind, n in required.items()
        ]
    )


def unverified_sources() -> pd.DataFrame:
    """Sources the author has not yet re-checked against the primary document.

    This drives Appendix A. It is deliberately part of the deliverable: a study
    about verification that did not track its own verification state would be
    making the exact mistake it documents.
    """
    frame = sources()
    return frame[frame["student_verified"].str.strip().str.upper() != "Y"]
