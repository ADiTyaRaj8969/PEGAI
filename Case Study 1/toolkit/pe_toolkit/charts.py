"""Figures for the report.

Design rules applied throughout: one scale per axis (never a dual axis - the
1-5 scores and the percentage rates are therefore always separate figures),
recessive grid and axes, direct value labels so nothing depends on reading a
colour against a gridline, and a surface-coloured gap between adjacent bars.

Colour assignment follows the job the colour does. V1..V4 is an ordered
progression, so it takes a single-hue ramp; the three tools are identities, so
they take categorical slots; verification outcomes are states, so they take the
reserved status palette and are never reused as series colours.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from . import audit, config, metrics  # noqa: E402

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Segoe UI", "DejaVu Sans", "sans-serif"],
        "font.size": 9,
        "figure.dpi": 200,
        "savefig.dpi": 200,
        "axes.titlesize": 11,
        "axes.titleweight": "600",
        "axes.labelsize": 9,
    }
)

_GAP = 1.4  # surface-coloured separator drawn as a bar edge


def _frame(ax, *, xgrid: bool = False) -> None:
    """Recessive chrome: no box, hairline grid on the value axis only."""
    fig = ax.get_figure()
    fig.patch.set_facecolor(config.SURFACE)
    ax.set_facecolor(config.SURFACE)

    for side in ("top", "right", "left" if not xgrid else "bottom"):
        ax.spines[side].set_visible(False)
    keep = "bottom" if not xgrid else "left"
    ax.spines[keep].set_color(config.BASELINE)
    ax.spines[keep].set_linewidth(1.0)

    ax.grid(
        axis="x" if xgrid else "y",
        color=config.GRIDLINE,
        linewidth=0.8,
        zorder=0,
    )
    ax.set_axisbelow(True)
    ax.tick_params(colors=config.INK_MUTED, length=0, labelsize=8.5)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_color(config.INK_SECONDARY)


def _title(ax, title: str, subtitle: str | None = None) -> None:
    ax.set_title(title, color=config.INK_PRIMARY, loc="left", pad=14 if subtitle else 8)
    if subtitle:
        ax.text(
            0,
            1.02,
            subtitle,
            transform=ax.transAxes,
            color=config.INK_SECONDARY,
            fontsize=8.5,
            va="bottom",
        )


def _legend(ax, **kw) -> None:
    legend = ax.legend(
        frameon=False,
        fontsize=8.5,
        labelcolor=config.INK_SECONDARY,
        handlelength=1.1,
        handleheight=0.9,
        **kw,
    )
    legend.set_zorder(5)


def prompt_version_scores(out: Path) -> Path:
    """Phase 8 - the four 1-5 metrics across the optimisation ladder."""
    frame = metrics.version_metrics()
    labels = ["Accuracy", "Reliability", "Completeness", "Bias reduction"]
    columns = ["accuracy", "reliability", "completeness", "bias_reduction"]

    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    n = len(frame)
    width = 0.78 / n

    for i, (_, row) in enumerate(frame.iterrows()):
        xs = [j + (i - (n - 1) / 2) * width for j in range(len(columns))]
        values = [int(row[c]) for c in columns]
        ax.bar(
            xs,
            values,
            width=width,
            color=config.ORDINAL_BLUE[i],
            edgecolor=config.SURFACE,
            linewidth=_GAP,
            label=f"{row['version']} - {row['name']}",
            zorder=3,
        )
        for x, v in zip(xs, values):
            ax.text(
                x,
                v + 0.08,
                str(v),
                ha="center",
                va="bottom",
                fontsize=7.5,
                color=config.INK_SECONDARY,
            )

    ax.set_xticks(range(len(columns)))
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 5.8)
    ax.set_yticks([0, 1, 2, 3, 4, 5])
    ax.set_ylabel("Score (1-5)")
    _frame(ax)
    _title(
        ax,
        "Prompt quality rises with every constraint added",
        "Self-assessed against the verified claim set, scored 1-5",
    )
    _legend(ax, loc="upper left", bbox_to_anchor=(0, -0.16), ncol=2)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight", facecolor=config.SURFACE)
    plt.close(fig)
    return out


def prompt_version_hallucination(out: Path) -> Path:
    """Phase 8 - the headline result, on its own scale."""
    frame = metrics.version_metrics()

    fig, ax = plt.subplots(figsize=(5.6, 3.0))
    xs = range(len(frame))
    rates = frame["hallucination_rate"].tolist()

    ax.bar(
        xs,
        rates,
        width=0.62,
        color=list(config.ORDINAL_BLUE),
        edgecolor=config.SURFACE,
        linewidth=_GAP,
        zorder=3,
    )
    for x, v in zip(xs, rates):
        ax.text(
            x,
            v + 0.9,
            f"{v:.1f}%",
            ha="center",
            va="bottom",
            fontsize=9,
            color=config.INK_PRIMARY,
            fontweight="600",
        )

    ax.set_xticks(list(xs))
    ax.set_xticklabels(frame["version"].tolist())
    ax.set_ylim(0, max(rates) * 1.25)
    ax.set_ylabel("Hallucination rate (%)")
    _frame(ax)
    drop = metrics.improvement_summary()["relative_drop"]
    _title(
        ax,
        f"Hallucination rate fell {drop:.0f}% across four prompt revisions",
        "Same model, same question, same day - only the prompt changed",
    )
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight", facecolor=config.SURFACE)
    plt.close(fig)
    return out


def audit_outcomes(out: Path) -> Path:
    """Phase 7 - how the 24 probed statements resolved."""
    summary = audit.summarise()
    rows = [
        ("Verified", summary.verified, config.STATUS["Verified"]),
        ("Partially verified", summary.partially_verified, config.STATUS["Partially verified"]),
        ("Unverified", summary.unverified, config.STATUS["Unverified"]),
        ("Hallucinated", summary.hallucinated, config.STATUS["Hallucinated"]),
    ]

    fig, ax = plt.subplots(figsize=(6.0, 2.6))
    ys = range(len(rows))
    ax.barh(
        ys,
        [r[1] for r in rows],
        height=0.6,
        color=[r[2] for r in rows],
        edgecolor=config.SURFACE,
        linewidth=_GAP,
        zorder=3,
    )
    for y, (_, count, _) in zip(ys, rows):
        ax.text(
            count + 0.15,
            y,
            f"{count}  ({100 * count / summary.total:.0f}%)",
            va="center",
            fontsize=8.5,
            color=config.INK_SECONDARY,
        )

    ax.set_yticks(list(ys))
    ax.set_yticklabels([r[0] for r in rows])
    ax.invert_yaxis()
    ax.set_xlim(0, summary.total * 0.55)
    ax.set_xlabel("Statements")
    _frame(ax, xgrid=True)
    _title(
        ax,
        f"{summary.hallucinated} of {summary.total} statements did not survive checking",
        "Unconstrained prompt (V1), Claude Opus 5, Phase 7 probe",
    )
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight", facecolor=config.SURFACE)
    plt.close(fig)
    return out


def failure_modes(out: Path) -> Path:
    """Phase 7 - what kind of wrong, ranked."""
    frame = audit.failure_modes()
    total = int(frame["Count"].sum())
    top = frame.iloc[0]

    fig, ax = plt.subplots(figsize=(6.6, 2.7))
    ys = range(len(frame))
    ax.barh(
        ys,
        frame["Count"],
        height=0.62,
        color=config.CATEGORICAL[0],
        edgecolor=config.SURFACE,
        linewidth=_GAP,
        zorder=3,
    )
    for y, count in zip(ys, frame["Count"]):
        ax.text(
            count + 0.08,
            y,
            f"{count} of {total}",
            va="center",
            fontsize=8.5,
            color=config.INK_SECONDARY,
        )

    ax.set_yticks(list(ys))
    ax.set_yticklabels(frame["Failure class"])
    ax.invert_yaxis()
    ax.set_xlim(0, float(frame["Count"].max()) * 1.45)
    ax.set_xticks(range(0, int(frame["Count"].max()) + 1))
    ax.set_xlabel("Statements")
    _frame(ax, xgrid=True)
    _title(
        ax,
        f"Invented sources are the largest failure class "
        f"({top['Count']} of {total})",
        "The hardest to catch are the ones with a real document behind them",
    )
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight", facecolor=config.SURFACE)
    plt.close(fig)
    return out


def llm_scores(out: Path) -> Path:
    """Phase 9 - the 1-5 criteria across the three tools."""
    frame = metrics.llm_scored_criteria()
    tools = [
        ("Claude Opus 5", "claude_opus_5"),
        ("ChatGPT", "chatgpt"),
        ("Perplexity", "perplexity"),
    ]

    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    n = len(tools)
    width = 0.76 / n
    criteria = frame["criterion"].tolist()

    for i, (label, column) in enumerate(tools):
        xs = [j + (i - (n - 1) / 2) * width for j in range(len(criteria))]
        values = frame[column].astype(float).tolist()
        ax.bar(
            xs,
            values,
            width=width,
            color=config.CATEGORICAL[i],
            edgecolor=config.SURFACE,
            linewidth=_GAP,
            label=label,
            zorder=3,
        )
        for x, v in zip(xs, values):
            ax.text(
                x,
                v + 0.08,
                f"{v:.0f}",
                ha="center",
                va="bottom",
                fontsize=7.5,
                color=config.INK_SECONDARY,
            )

    ax.set_xticks(range(len(criteria)))
    ax.set_xticklabels(
        [c.replace(" (citation quality)", "\n(citation quality)") for c in criteria],
        fontsize=8,
    )
    ax.set_ylim(0, 5.8)
    ax.set_yticks([0, 1, 2, 3, 4, 5])
    ax.set_ylabel("Score (1-5)")
    _frame(ax)
    _title(
        ax,
        "No tool wins outright - they fail in different directions",
        "Identical V4 prompt issued to all three tools",
    )
    _legend(ax, loc="upper left", bbox_to_anchor=(0, -0.18), ncol=3)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight", facecolor=config.SURFACE)
    plt.close(fig)
    return out


def llm_hallucination(out: Path) -> Path:
    """Phase 9 - hallucination rate, kept off the 1-5 axis."""
    frame = metrics.llm_table()
    row = frame[frame["Criteria"] == "Hallucination rate"].iloc[0]
    tools = ["Claude Opus 5", "ChatGPT", "Perplexity"]
    rates = [float(row[t]) for t in tools]

    fig, ax = plt.subplots(figsize=(5.2, 2.9))
    xs = range(len(tools))
    ax.bar(
        xs,
        rates,
        width=0.55,
        color=list(config.CATEGORICAL),
        edgecolor=config.SURFACE,
        linewidth=_GAP,
        zorder=3,
    )
    for x, v in zip(xs, rates):
        ax.text(
            x,
            v + 0.5,
            f"{v:.1f}%",
            ha="center",
            va="bottom",
            fontsize=9,
            color=config.INK_PRIMARY,
            fontweight="600",
        )

    ax.set_xticks(list(xs))
    ax.set_xticklabels(tools)
    ax.set_ylim(0, max(rates) * 1.3)
    ax.set_ylabel("Hallucination rate (%)")
    _frame(ax)
    _title(
        ax,
        "Search grounding cut fabrication, but not bias",
        "24 generated statements per tool, identical prompt",
    )
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight", facecolor=config.SURFACE)
    plt.close(fig)
    return out


FIGURES = {
    "fig1_prompt_version_scores.png": prompt_version_scores,
    "fig2_prompt_version_hallucination.png": prompt_version_hallucination,
    "fig3_audit_outcomes.png": audit_outcomes,
    "fig4_failure_modes.png": failure_modes,
    "fig5_llm_scores.png": llm_scores,
    "fig6_llm_hallucination.png": llm_hallucination,
}


def render_all(directory: Path | None = None) -> list[Path]:
    directory = directory or config.FIGURES
    directory.mkdir(parents=True, exist_ok=True)
    return [fn(directory / name) for name, fn in FIGURES.items()]
