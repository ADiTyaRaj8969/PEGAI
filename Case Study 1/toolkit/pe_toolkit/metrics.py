"""Phase 8 and Phase 9 scoring."""

from __future__ import annotations

import pandas as pd

from . import datastore

SCORED = ("accuracy", "reliability", "completeness", "bias_reduction")


def version_metrics() -> pd.DataFrame:
    """Phase 8 performance comparison, with the rate computed not typed."""
    frame = datastore.prompt_versions().copy()
    frame["hallucination_rate"] = (
        100.0
        * frame["statements_hallucinated"].astype(int)
        / frame["statements_generated"].astype(int)
    ).round(1)
    return frame


def version_comparison_table() -> pd.DataFrame:
    """The manual's Metric x V1..V4 grid."""
    frame = version_metrics().set_index("version")
    rows = {
        "Accuracy (1-5)": frame["accuracy"],
        "Reliability (1-5)": frame["reliability"],
        "Completeness (1-5)": frame["completeness"],
        "Hallucination rate (%)": frame["hallucination_rate"],
        "Bias reduction (1-5)": frame["bias_reduction"],
    }
    return (
        pd.DataFrame(rows)
        .T.reset_index()
        .rename(columns={"index": "Metric"})
    )


def improvement_summary() -> dict[str, float]:
    frame = version_metrics()
    first, last = frame.iloc[0], frame.iloc[-1]
    v1_rate = float(first["hallucination_rate"])
    v4_rate = float(last["hallucination_rate"])
    return {
        "v1_rate": v1_rate,
        "v4_rate": v4_rate,
        "absolute_drop": round(v1_rate - v4_rate, 1),
        "relative_drop": round(100.0 * (v1_rate - v4_rate) / v1_rate, 1),
        "accuracy_gain": int(last["accuracy"]) - int(first["accuracy"]),
    }


def llm_table() -> pd.DataFrame:
    """Phase 9 grid, relabelled for the report."""
    frame = datastore.llm_comparison().copy()
    return frame.rename(
        columns={
            "criterion": "Criteria",
            "claude_opus_5": "Claude Opus 5",
            "chatgpt": "ChatGPT",
            "perplexity": "Perplexity",
        }
    )[["Criteria", "Claude Opus 5", "ChatGPT", "Perplexity"]]


def llm_scored_criteria() -> pd.DataFrame:
    """Only the 1-5 rows, for charting. The percentage row has a different
    scale and must not share an axis with them."""
    frame = datastore.llm_comparison()
    scored = frame[frame["unit"] == "score_1_5"]
    return scored[scored["criterion"] != "Overall performance"]
