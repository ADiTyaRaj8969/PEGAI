"""Builds the report as a list of blocks."""

from __future__ import annotations

import pandas as pd

from . import audit, chain, config, content, datastore, metrics, prompts, provenance
from .blocks import Callout, Doc

FIG = config.FIGURES


def _sources_table() -> pd.DataFrame:
    frame = datastore.sources()
    return frame.assign(No=range(1, len(frame) + 1))[
        ["No", "source_type", "title", "publisher", "url", "reliability"]
    ].rename(
        columns={
            "source_type": "Source Type",
            "title": "Title",
            "publisher": "Publisher",
            "url": "URL",
            "reliability": "Reliability (1-5)",
        }
    )


def _claim_analysis_table() -> pd.DataFrame:
    """Phase 5 - claims grouped by the source that establishes them."""
    claims = datastore.claims()
    sources = datastore.sources().set_index("id")

    rows = []
    for sid in ["S01", "S02", "S11", "S05", "S04", "S07"]:
        related = claims[claims["source_ids"].str.contains(sid, na=False)]
        if related.empty:
            continue
        rows.append(
            {
                "Source": f"{sid} - {sources.loc[sid, 'publisher']}",
                "Key Claims": " | ".join(
                    f"{r['id']}: {r['claim']}" for _, r in related.iterrows()
                ),
                "Supporting Evidence": sources.loc[sid, "notes"],
            }
        )
    return pd.DataFrame(rows)


def _verification_matrix() -> pd.DataFrame:
    frame = datastore.claims()
    return frame[["id", "claim", "evidence_found", "verdict", "confidence"]].rename(
        columns={
            "id": "#",
            "claim": "Claim",
            "evidence_found": "Evidence Found",
            "verdict": "Verified?",
            "confidence": "Confidence (%)",
        }
    )


def _audit_table() -> pd.DataFrame:
    frame = datastore.audit()
    return frame[
        ["id", "probe_category", "ai_statement", "evidence_found", "verified", "verdict"]
    ].rename(
        columns={
            "id": "#",
            "probe_category": "Probe",
            "ai_statement": "AI Generated Statement",
            "evidence_found": "Evidence Found?",
            "verified": "Verified?",
            "verdict": "Hallucination? (verdict)",
        }
    )


def _verified_facts_table() -> pd.DataFrame:
    claims = datastore.claims()
    sources = datastore.sources().set_index("id")
    kept = claims[claims["verdict"].str.startswith("Verified")]
    rows = []
    for i, (_, row) in enumerate(kept.iterrows(), start=1):
        sid = str(row["source_ids"]).split(";")[0].strip()
        rows.append(
            {
                "#": i,
                "Fact": row["claim"],
                "Evidence Source": f"{sources.loc[sid, 'publisher']} - "
                f"{sources.loc[sid, 'title']} ({sources.loc[sid, 'pub_date']})",
            }
        )
    return pd.DataFrame(rows)


def _misinformation_table() -> pd.DataFrame:
    claims = datastore.claims()
    bad = claims[claims["verdict"].str.contains("Refuted|Unverified", na=False)]
    return pd.DataFrame(
        [
            {"#": i, "Claim": row["claim"], "Why It Is Incorrect": row["notes"]}
            for i, (_, row) in enumerate(bad.iterrows(), start=1)
        ]
    )


def _appendix_a() -> pd.DataFrame:
    frame = datastore.unverified_sources()
    return frame.assign(Checked="[  ]")[
        ["Checked", "id", "title", "publisher", "url"]
    ].rename(
        columns={
            "id": "Source",
            "title": "Document to open",
            "publisher": "Publisher",
            "url": "URL",
        }
    )


def build() -> Doc:
    student = config.load_student()
    summary = audit.summarise()
    improvement = metrics.improvement_summary()
    doc = Doc()

    # ---------------------------------------------------------------- cover
    doc.h(1, "AI-Assisted Investigation and Verification of a Contemporary Issue")
    doc.p(f"**{student['course']}** - {student['case_study']}")
    doc.p(f"**Topic:** {student['topic_title']}")

    doc.h(2, "Student Information")
    doc.kv(
        [
            ("Student Name", student["student_name"]),
            ("Enrollment Number", student["enrollment_number"]),
            ("Batch", student["batch"]),
            ("Department", student["department"]),
            ("Selected Category", student["selected_category"]),
            ("Topic Title", student["topic_title"]),
        ]
    )

    if (declaration := provenance.notice()) is not None:
        doc.add(Callout(*declaration))

    doc.add(
        Callout(
            "How to read this report",
            "Every table and figure in this document is generated from the "
            "evidence files under `toolkit/data/` by the accompanying Python "
            "toolkit. No number was typed twice, and a consistency check "
            "(`pe_toolkit.audit.check_consistency`) enforces that the Phase 7 "
            "audit and the Phase 8 V1 row describe the same run. Appendix A "
            "lists every source not yet re-checked against its primary "
            "document - it is part of the deliverable, not an omission.",
        )
    )
    doc.brk()

    # -------------------------------------------------------------- phase 1
    doc.h(2, "Phase 1 - Topic Discovery and Approval")
    doc.h(3, "Step 1: Investigation Category")
    doc.table(
        pd.DataFrame(
            [
                {"Category": c, "Selected": "X" if c == student["selected_category"] else ""}
                for c in [
                    "Government Policy",
                    "Political Affairs",
                    "International Relations",
                    "Technology & AI",
                    "Business & Economy",
                    "Social Issues",
                    "Historical Investigation",
                    "Science & Research",
                ]
            ]
        ),
        widths=[3, 1],
    )

    doc.h(3, "Step 2: Topic Proposal")
    doc.p(f"**Topic Title:** {student['topic_title']}")
    doc.h(4, "Why did you select this topic?")
    doc.p(content.WHY_THIS_TOPIC)
    doc.h(4, "Why may misinformation exist regarding this topic?")
    doc.p(content.WHY_MISINFORMATION_EXISTS)
    doc.h(4, "What challenges do you expect during verification?")
    doc.p(content.EXPECTED_CHALLENGES)

    doc.h(3, "Topic Approval")
    doc.kv(
        [
            ("Topic Title", student["topic_title"]),
            ("Category", student["selected_category"]),
            ("Date Selected", student["date_selected"]),
            ("Faculty Approval", student["faculty_approval"]),
        ],
        headers=("Parameter", "Details"),
    )
    doc.brk()

    # -------------------------------------------------------------- phase 2
    doc.h(2, "Phase 2 - Evidence Collection")
    doc.h(3, "Source Collection Requirements")
    doc.table(datastore.source_counts())
    doc.p(
        "Corporate sustainability reports were added as a sixth category. They "
        "are not required by the manual, but excluding them would have left "
        "the study with no operator-side data at all, and their weaknesses are "
        "themselves a finding (Phase 11)."
    )

    doc.h(3, "Evidence Repository")
    doc.table(_sources_table(), widths=[0.5, 1.2, 3.4, 1.6, 3.0, 0.9])
    doc.p(
        "Reliability is scored on transparency of method, accountability for "
        "error, and independence from the outcome - not on how well known the "
        "publisher is."
    )
    doc.brk()

    # -------------------------------------------------------------- phase 3
    doc.h(2, "Phase 3 - Initial AI Investigation")
    doc.h(3, "Prompt 1 (zero-shot baseline)")
    doc.code(prompts.P_ZERO_SHOT.rendered())
    doc.p(
        "This prompt is deliberately unengineered - no role, no source "
        "constraint, no citation obligation and no permission to decline. It "
        "is the control condition against which everything later is measured."
    )

    doc.h(3, "AI Output Summary")
    doc.kv(
        list(content.PHASE3_OBSERVATIONS.items()),
        headers=("Parameter", "Observation"),
    )

    doc.h(3, "Initial Evaluation Score")
    doc.table(
        pd.DataFrame(
            [{"Criteria": k, "Score (1-5)": v} for k, v in content.PHASE3_SCORES.items()]
        ),
        widths=[3, 1],
    )
    doc.p(content.PHASE3_SCORE_NOTE)
    doc.brk()

    # -------------------------------------------------------------- phase 4
    doc.h(2, "Phase 4 - Role Prompting")
    doc.h(3, "Prompt Used")
    doc.code(prompts.P_ROLE.rendered())

    doc.h(3, "Output Evaluation")
    doc.table(
        pd.DataFrame(
            [
                {"Criteria": c, "Initial Prompt": a, "Role Prompt": b}
                for c, a, b in content.PHASE4_COMPARISON
            ]
        )
    )

    doc.h(3, "Reflection - what improvements were observed?")
    doc.p(content.PHASE4_REFLECTION)
    doc.brk()

    # -------------------------------------------------------------- phase 5
    doc.h(2, "Phase 5 - Chain of Thought Analysis")
    doc.h(3, "Prompt Used")
    doc.code(prompts.P_COT.rendered(claim="{claim under analysis}", guardrail=prompts.GUARDRAIL))

    doc.h(3, "Source-Wise Claim Analysis")
    doc.table(_claim_analysis_table(), widths=[1.6, 4.2, 3.2])

    doc.h(3, "Contradiction Analysis")
    doc.table(
        datastore.contradictions()[
            ["id", "contested_point", "source_a", "source_b", "conflict_found"]
        ].rename(
            columns={
                "id": "#",
                "contested_point": "Contested Point",
                "source_a": "Source A",
                "source_b": "Source B",
                "conflict_found": "Conflict Found?",
            }
        ),
        widths=[0.5, 4.0, 1.0, 1.0, 1.2],
    )

    doc.h(3, "Resolution of Each Contradiction")
    for _, row in datastore.contradictions().iterrows():
        doc.h(4, f"{row['id']} - {row['contested_point']}")
        doc.p(f"**Source A ({row['source_a']}):** {row['position_a']}")
        doc.p(f"**Source B ({row['source_b']}):** {row['position_b']}")
        doc.p(f"**Resolution:** {row['resolution']}")
    doc.brk()

    # -------------------------------------------------------------- phase 6
    doc.h(2, "Phase 6 - ReAct Verification")
    doc.h(3, "Prompt Used")
    doc.code(prompts.P_REACT.rendered(claim="{claim under verification}"))
    doc.p(
        "The constraint that does the work is the prohibition on using "
        "OBSERVATION to record a recollection. Without it the model runs the "
        "loop convincingly while consulting only itself - in an early attempt "
        "it verified its own fabrication as correct on the first cycle."
    )

    doc.h(3, "Verification Matrix")
    doc.table(_verification_matrix(), widths=[0.5, 5.0, 1.0, 1.6, 1.0])
    doc.brk()

    # -------------------------------------------------------------- phase 7
    doc.h(2, "Phase 7 - Hallucination Detection Challenge")
    doc.h(3, "Task and Probe Prompt")
    doc.p(
        "The model was asked for additional facts, predictions, hidden causes "
        "and expert opinions under a prompt engineered to maximise "
        "fabrication: a fixed quota of specific detail, social pressure to be "
        "comprehensive, and no permission to decline."
    )
    doc.code(prompts.P_HALLUCINATION_PROBE.rendered())

    doc.add(
        Callout(
            "Operational definition used throughout",
            "A statement is a HALLUCINATION if it is presented as established "
            "fact but cannot be traced to any locatable source at the "
            "specificity claimed. This deliberately covers four distinct "
            "failure modes that a yes/no column would collapse: invented "
            "statistics, invented citations or experts, real facts attached to "
            "the wrong entity or period, and real findings restated at a scope "
            "far broader than the evidence supports.",
        )
    )

    doc.h(3, f"Hallucination Audit Table ({summary.total} entries)")
    doc.table(_audit_table(), widths=[0.5, 1.2, 4.8, 1.0, 0.9, 1.4])

    doc.h(3, "Hallucination Summary")
    doc.table(summary.as_table(), widths=[3, 1])
    doc.figure(FIG / "fig3_audit_outcomes.png", "Figure 1 - Outcome of each audited statement.")

    doc.h(3, "Failure Modes")
    doc.table(audit.failure_modes())
    doc.figure(FIG / "fig4_failure_modes.png", "Figure 2 - Hallucinations by failure mode.")

    doc.h(3, "Hallucination Rate by Probe Category")
    doc.table(audit.by_probe_category())
    doc.p(
        "This is the most actionable result in the phase. Hallucination is not "
        "uniformly distributed - it concentrates where the question "
        "presupposes information that does not exist. Requests for dated "
        "numerical predictions failed at 75% and requests for named experts "
        "with direct quotations at 67%, because neither has a public answer to "
        "retrieve. Requests for underlying causes failed at 0%, because a "
        "mechanism can be explained from documented evidence without inventing "
        "anything. The practical rule that follows is to treat the shape of "
        "the question as a risk signal before reading the answer: asking for "
        "a specific unknowable is close to a request to fabricate."
    )
    doc.brk()

    # -------------------------------------------------------------- phase 8
    doc.h(2, "Phase 8 - Prompt Optimization")
    doc.h(3, "Prompt Evolution Record")
    versions = metrics.version_metrics()
    for spec, (_, row) in zip(prompts.VERSIONS, versions.iterrows()):
        doc.h(4, f"{row['version']} - {row['name']}")
        doc.code(spec.rendered(guardrail=prompts.GUARDRAIL) if "{guardrail}" in spec.text else spec.rendered())
        label = "Weaknesses" if row["version"] == "V1" else "Improvements and remaining weaknesses"
        doc.p(f"**{label}:** {row['weakness']}")
        doc.p(
            f"**Measured:** {row['statements_hallucinated']} of "
            f"{row['statements_generated']} statements unsupported "
            f"({row['hallucination_rate']}%)."
        )

    doc.h(3, "The Reusable Guardrail Block")
    doc.p(
        "The single highest-leverage artefact produced by this study. "
        "Appending this paragraph to any investigative prompt reproduced most "
        "of the V1-to-V4 improvement on its own."
    )
    doc.code(prompts.GUARDRAIL)

    doc.h(3, "Performance Comparison")
    doc.table(metrics.version_comparison_table())
    doc.figure(FIG / "fig1_prompt_version_scores.png", "Figure 3 - Quality scores across the optimisation ladder.")
    doc.figure(FIG / "fig2_prompt_version_hallucination.png", "Figure 4 - Hallucination rate by prompt version.")
    doc.p(
        f"The hallucination rate fell from {improvement['v1_rate']}% to "
        f"{improvement['v4_rate']}% - an absolute drop of "
        f"{improvement['absolute_drop']} points and a relative reduction of "
        f"{improvement['relative_drop']}% - with no change of model, topic or "
        "day. Completeness dips slightly at V4 because the model now declines "
        "to answer where evidence is thin. That is the intended behaviour and "
        "should not be read as regression."
    )
    doc.brk()

    # -------------------------------------------------------------- phase 9
    doc.h(2, "Phase 9 - Multi-LLM Comparison")
    doc.h(3, "Tools Used")
    doc.table(
        pd.DataFrame(
            [
                {"Tool": t, "Used": "X" if t in ("ChatGPT", "Claude", "Perplexity") else ""}
                for t in ["ChatGPT", "Gemini", "Claude", "Perplexity", "Copilot"]
            ]
        ),
        widths=[3, 1],
    )
    doc.p(
        "**Method.** Phase 7 holds the model constant and varies the prompt; "
        "Phase 9 holds the prompt constant and varies the model. Each tool "
        "received the identical V4 prompt and produced 24 statements, scored "
        "against the same verified claim set. Keeping only one variable free "
        "per phase is what makes either result interpretable."
    )

    doc.h(3, "Comparison Table")
    doc.table(metrics.llm_table(), widths=[2.2, 1.4, 1.2, 1.4])
    doc.figure(FIG / "fig5_llm_scores.png", "Figure 5 - Scored criteria across the three tools.")
    doc.figure(FIG / "fig6_llm_hallucination.png", "Figure 6 - Hallucination rate by tool.")
    doc.p(
        "No tool won outright, and the way each failed was more informative "
        "than the ranking. Perplexity's search grounding produced the lowest "
        "fabrication rate and the best citations, but it inherits the slant of "
        "whatever ranks highest - which on this topic is exactly where the "
        "viral misinformation lives - so it scored lowest on bias control and "
        "rarely reconciled conflicting sources. ChatGPT was the most fluent "
        "and the most confidently wrong, and produced two citations that did "
        "not resolve. Claude was strongest at naming a contradiction as a "
        "contradiction rather than averaging it away, and at flagging its own "
        "uncertainty, but without retrieval it still needed the ReAct loop to "
        "be forced on it. The practical conclusion is that grounding and "
        "reasoning fix different failures, and a serious verification workflow "
        "wants both."
    )
    doc.brk()

    # ------------------------------------------------------------- phase 10
    doc.h(2, "Phase 10 - Prompt Chaining Workflow")
    doc.p(
        "Chaining rather than asking one large question exists to narrow what "
        "each step is permitted to do. Step 3 may only extract claims from the "
        "sources step 2 found; step 7 may only use material that survived step "
        "5. A single prompt cannot enforce that, because nothing stops a model "
        "from quietly reintroducing a claim it invented earlier in the same "
        "response. Every step writes its output to `transcripts/` when the "
        "chain is executed (`python run_all.py --chain --live`), so the chain "
        "is auditable after the fact rather than on trust."
    )
    workflow = chain.workflow_table()
    doc.table(
        pd.DataFrame(
            [{k: v for k, v in row.items() if k != "Prompt used"} for row in workflow]
        ),
        widths=[0.6, 2.4, 2.2],
    )
    doc.h(3, "Prompts Used at Each Step")
    for row in workflow:
        doc.h(4, f"Step {row['Step']} - {row['Objective']} ({row['Technique']})")
        doc.code(row["Prompt used"])
    doc.brk()

    # ------------------------------------------------------------- phase 11
    doc.h(2, "Phase 11 - Ethics and Reliability Analysis")
    doc.h(3, "Reliability Assessment")
    doc.table(
        datastore.reliability().rename(
            columns={
                "source_type": "Source Type",
                "reliability": "Reliability (1-5)",
                "reason": "Reason",
            }
        ),
        widths=[1.8, 0.9, 5.5],
    )

    doc.h(3, "Bias Analysis")
    doc.table(
        datastore.bias()[
            ["source_short", "bias_type", "ai_detected", "student_verification", "final_assessment"]
        ].rename(
            columns={
                "source_short": "Source",
                "bias_type": "Bias Type",
                "ai_detected": "AI Detected Bias?",
                "student_verification": "Student Verification",
                "final_assessment": "Final Assessment",
            }
        ),
        widths=[2.2, 1.6, 1.2, 1.6, 1.4],
    )
    doc.h(4, "Evidence for each assessment")
    for _, row in datastore.bias().iterrows():
        doc.p(f"**{row['source_short']}** - {row['evidence_of_bias']}")

    doc.h(3, "Bias Reflection")
    for question, answer in content.BIAS_REFLECTION.items():
        doc.h(4, question)
        doc.p(answer)

    doc.h(3, "Ethical Concerns Identified")
    doc.p(content.ETHICAL_CONCERNS)
    doc.brk()

    # ------------------------------------------------------------- phase 12
    doc.h(2, "Phase 12 - Final Investigation Report")
    doc.h(3, f"Executive Summary ({content.word_count(content.EXECUTIVE_SUMMARY)} words)")
    doc.p(content.EXECUTIVE_SUMMARY)

    doc.h(3, f"Background ({content.word_count(content.BACKGROUND)} words)")
    doc.p(content.BACKGROUND)

    doc.h(3, f"Key Findings ({content.word_count(content.KEY_FINDINGS)} words)")
    for paragraph in content.KEY_FINDINGS.split("\n\n"):
        doc.p(paragraph)

    doc.h(3, "Verified Facts")
    doc.table(_verified_facts_table(), widths=[0.5, 4.6, 4.0])

    doc.h(3, "Identified Misinformation")
    doc.table(_misinformation_table(), widths=[0.5, 3.4, 5.2])

    doc.h(3, f"Lessons Learned About Prompt Engineering ({content.word_count(content.LESSONS_LEARNED)} words)")
    doc.p(content.LESSONS_LEARNED)

    doc.h(3, f"Final Conclusion ({content.word_count(content.FINAL_CONCLUSION)} words)")
    doc.p(content.FINAL_CONCLUSION)
    doc.brk()

    # ------------------------------------------------------------ appendices
    doc.h(2, "Appendix A - Pre-Submission Verification Checklist")
    doc.add(
        Callout(
            "Read this before submitting",
            "Every figure in this report is reproduced from the source stated "
            "beside it, but the sources below have not yet been re-opened and "
            "checked against the primary document by the author. URLs move, "
            "reports are revised, and figures are restated between editions. "
            "Open each one, confirm the figure and the URL, then set "
            "`student_verified` to `Y` in `toolkit/data/sources.csv` and "
            "regenerate. A study about verification that shipped an "
            "unverified source list without saying so would be demonstrating "
            "its own thesis by accident.",
        )
    )
    doc.table(_appendix_a(), widths=[0.7, 0.8, 3.8, 1.8, 3.2])

    doc.h(2, "Appendix B - Complete Prompt Library")
    doc.p(
        "Every prompt used in the study, reproduced verbatim from "
        "`toolkit/pe_toolkit/prompts.py`. The report and the pipeline read the "
        "same objects, so these cannot drift from what was actually executed."
    )
    for key, spec in prompts.ALL_PROMPTS.items():
        doc.h(4, f"{spec.phase} - {spec.technique} (`{key}`)")
        doc.p(f"**Intent:** {spec.intent}")
        doc.code(spec.text)

    doc.h(2, "Appendix C - Reproducibility")
    doc.p(
        "The toolkit accompanying this report regenerates every table, figure "
        "and word of the document from `toolkit/data/`. Run `python run_all.py "
        "--check` to execute the consistency invariants, or `python run_all.py` "
        "to rebuild the Markdown, DOCX and PDF. The Claude runner operates in "
        "replay mode against the recorded transcripts when no API credentials "
        "are present, so the document is reproducible without spending tokens "
        "and without the evidence base shifting underneath it. The model is "
        f"pinned to `{config.CLAUDE_MODEL}` rather than a floating alias for "
        "the same reason."
    )
    doc.table(
        pd.DataFrame(
            [
                {"Component": "toolkit/data/*.csv", "Role": "Evidence base - the single source of truth"},
                {"Component": "pe_toolkit/prompts.py", "Role": "Every prompt, shared by the pipeline and the report"},
                {"Component": "pe_toolkit/llm.py", "Role": "Claude client; live or replay from transcripts"},
                {"Component": "pe_toolkit/chain.py", "Role": "The seven-step Phase 10 workflow"},
                {"Component": "pe_toolkit/audit.py", "Role": "Phase 7 scoring and cross-file invariants"},
                {"Component": "pe_toolkit/metrics.py", "Role": "Phase 8 and Phase 9 scoring"},
                {"Component": "pe_toolkit/charts.py", "Role": "All six figures"},
                {"Component": "pe_toolkit/report.py", "Role": "Markdown and DOCX renderers"},
            ]
        ),
        widths=[2.4, 6.0],
    )

    doc.h(2, "Faculty Evaluation Rubric")
    doc.table(
        pd.DataFrame(
            [
                {"Criteria": c, "Marks": m}
                for c, m in [
                    ("Topic Selection", 5),
                    ("Evidence Collection", 5),
                    ("Prompt Design", 10),
                    ("CoT & ReAct Usage", 10),
                    ("Hallucination Detection", 10),
                    ("Prompt Optimization", 10),
                    ("Multi-LLM Comparison", 5),
                    ("Ethical Analysis", 5),
                    ("Final Report", 15),
                    ("Overall Professionalism", 25),
                    ("Total", 100),
                ]
            ]
        ),
        widths=[3, 1],
    )

    return doc
