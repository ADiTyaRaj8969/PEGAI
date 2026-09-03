"""Toolkit for the Prompt Engineering case study.

Regenerates every table, figure and page of the report from the evidence files
under `data/`, and executes the Phase 10 prompt chain against Claude.
"""

from . import audit, charts, chain, config, content, datastore, llm, metrics, prompts, report

__all__ = [
    "audit",
    "chain",
    "charts",
    "config",
    "content",
    "datastore",
    "llm",
    "metrics",
    "prompts",
    "report",
]
