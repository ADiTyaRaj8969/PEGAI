"""Paths, model identifiers and the validated colour palette."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
TRANSCRIPTS = ROOT / "transcripts"
REPORT_DIR = ROOT.parent / "report"
FIGURES = REPORT_DIR / "figures"

# Model used for every Claude call in this study. Pinned so the results are
# reproducible - a floating alias would silently change the measurements.
CLAUDE_MODEL = "claude-opus-5"

# The other two tools in the Phase 9 comparison are consumer products without
# a comparable API surface, so their runs were performed manually and their
# outputs recorded under transcripts/. They are listed here so the report and
# the pipeline agree on what was compared.
COMPARED_TOOLS = ("Claude Opus 5", "ChatGPT", "Perplexity")


# --- Palette -----------------------------------------------------------------
# Validated with the dataviz skill's checker against the light chart surface
# (#fcfcfb). The three-slot categorical set passes all-pairs CVD and
# normal-vision separation; the four-step blue ramp passes the ordinal checks
# (monotone lightness, >=0.06 adjacent lightness gaps, light end above 2:1).

SURFACE = "#fcfcfb"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"

# Categorical - identity. Fixed order, never cycled.
CATEGORICAL = ("#2a78d6", "#eb6834", "#1baf7a")

# Ordinal - V1..V4 is an ordered progression, not four identities, so it takes
# a single-hue ramp rather than four categorical slots.
ORDINAL_BLUE = ("#86b6ef", "#5598e7", "#2a78d6", "#184f95")

# Status - reserved for verification outcomes, never reused as a series colour.
STATUS = {
    "Verified": "#0ca30c",
    "Verified as scenario": "#0ca30c",
    "Partially verified": "#fab219",
    "Unverified": "#ec835a",
    "Hallucinated": "#d03b3b",
}


def load_student() -> dict[str, str]:
    """Read the cover-page fields."""
    return json.loads((DATA / "student.json").read_text(encoding="utf-8"))
