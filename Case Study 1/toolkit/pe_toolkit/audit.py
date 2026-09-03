"""Phase 7 scoring, plus the cross-file consistency checks.

The operational definition used throughout this study:

    A statement is a HALLUCINATION if it is presented as established fact but
    cannot be traced to any locatable source at the specificity claimed.

That covers four failure modes the manual's binary yes/no column would
otherwise collapse together: wholly invented statistics, invented citations or
experts, real facts attached to the wrong entity or period, and real findings
restated at a scope far broader than the evidence supports. The last two are
the hard ones - they survive a casual check precisely because a real document
sits somewhere behind them.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from . import datastore

HALLUCINATED = "Hallucinated"
UNVERIFIED = "Unverified"
VERIFIED_PREFIX = "Verified"
PARTIAL = "Partially verified"


@dataclass(frozen=True)
class AuditSummary:
    total: int
    verified: int
    partially_verified: int
    unverified: int
    hallucinated: int

    @property
    def hallucination_rate(self) -> float:
        return 100.0 * self.hallucinated / self.total if self.total else 0.0

    @property
    def fully_supported_rate(self) -> float:
        return 100.0 * self.verified / self.total if self.total else 0.0

    def as_table(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                ("Total claims generated", self.total),
                ("Verified claims", self.verified),
                ("Partially verified claims", self.partially_verified),
                ("Unverified claims", self.unverified),
                ("Hallucinated claims", self.hallucinated),
                ("Hallucination rate", f"{self.hallucination_rate:.1f}%"),
            ],
            columns=["Parameter", "Count"],
        )


def summarise(frame: pd.DataFrame | None = None) -> AuditSummary:
    frame = datastore.audit() if frame is None else frame
    verdict = frame["verdict"].str.strip()

    return AuditSummary(
        total=len(frame),
        # "Verified" and "Verified as scenario" both mean the claim stood up;
        # the scenario tag records that its framing survived, not that it is
        # weaker evidence.
        verified=int(verdict.str.startswith(VERIFIED_PREFIX).sum()),
        partially_verified=int((verdict == PARTIAL).sum()),
        unverified=int((verdict == UNVERIFIED).sum()),
        hallucinated=int((verdict == HALLUCINATED).sum()),
    )


def failure_modes(frame: pd.DataFrame | None = None) -> pd.DataFrame:
    """Which classes of failure occurred, most frequent first.

    Grouped by `failure_class` rather than the per-row `failure_mode`, which is
    a free-text description unique to each statement and therefore useless as a
    distribution.
    """
    frame = datastore.audit() if frame is None else frame
    hallucinations = frame[frame["verdict"].str.strip() == HALLUCINATED]
    counts = hallucinations["failure_class"].value_counts()
    return (
        counts.rename_axis("Failure class")
        .reset_index(name="Count")
        .assign(
            Share=lambda d: (100 * d["Count"] / len(hallucinations))
            .round(1)
            .map(lambda v: f"{v}%"),
            Examples=lambda d: d["Failure class"].map(
                lambda cls: ", ".join(
                    hallucinations.loc[
                        hallucinations["failure_class"] == cls, "id"
                    ].tolist()
                )
            ),
        )
    )


def by_probe_category(frame: pd.DataFrame | None = None) -> pd.DataFrame:
    """Hallucination rate per probe type.

    This is the most actionable output in Phase 7: it shows *which kind of
    question* is dangerous to ask, not merely that hallucination happens.
    """
    frame = datastore.audit() if frame is None else frame
    rows = []
    for category, group in frame.groupby("probe_category", sort=False):
        bad = int((group["verdict"].str.strip() == HALLUCINATED).sum())
        rows.append(
            {
                "Probe category": category,
                "Statements": len(group),
                "Hallucinated": bad,
                "Rate %": round(100.0 * bad / len(group), 1),
            }
        )
    return pd.DataFrame(rows).sort_values("Rate %", ascending=False, ignore_index=True)


def check_consistency() -> list[str]:
    """Cross-file invariants. Returns a list of problems (empty means clean).

    Phase 7's probe is the V1 prompt, so the audit table and the V1 row of the
    optimisation table must describe the same run. Keeping this as an
    executable check rather than a proofreading habit is the only reason the
    two agree.
    """
    problems: list[str] = []

    summary = summarise()
    versions = datastore.prompt_versions()
    v1 = versions[versions["version"] == "V1"].iloc[0]

    if int(v1["statements_generated"]) != summary.total:
        problems.append(
            f"V1 statements_generated={v1['statements_generated']} but the "
            f"audit table holds {summary.total} rows."
        )
    if int(v1["statements_hallucinated"]) != summary.hallucinated:
        problems.append(
            f"V1 statements_hallucinated={v1['statements_hallucinated']} but "
            f"the audit table marks {summary.hallucinated} as hallucinated."
        )

    # Every source id referenced by a claim must exist.
    known = set(datastore.sources()["id"])
    for _, row in datastore.claims().iterrows():
        for sid in str(row["source_ids"]).split(";"):
            sid = sid.strip()
            if sid and sid not in known:
                problems.append(f"claim {row['id']} cites unknown source {sid}")

    for _, row in datastore.bias().iterrows():
        if row["source_id"] not in known:
            problems.append(f"bias row cites unknown source {row['source_id']}")

    # The hallucination rate must fall monotonically across the ladder,
    # otherwise the Phase 8 narrative does not hold.
    rates = [
        100.0 * int(r["statements_hallucinated"]) / int(r["statements_generated"])
        for _, r in versions.iterrows()
    ]
    if rates != sorted(rates, reverse=True):
        problems.append(f"hallucination rate is not monotonically falling: {rates}")

    return problems
