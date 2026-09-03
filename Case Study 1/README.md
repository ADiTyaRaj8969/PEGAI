# Case Study 1 — Prompt Engineering for Generative AI

**Topic:** The energy and water footprint of AI data centres — separating measured evidence from viral statistics
**Category:** Technology & AI

---

## What is here

```
PE/
├── CASE STUDY 1 MANUAL.pdf          the assignment brief
├── report/
│   ├── CASE_STUDY_REPORT.docx       ← submit this (36 pages)
│   ├── CASE_STUDY_REPORT.pdf        ← or this
│   ├── CASE_STUDY_REPORT.md         editable master
│   └── figures/                     six generated charts
└── toolkit/                         the code that builds all of the above
    ├── run_all.py                   entry point
    ├── data/                        the evidence base — single source of truth
    ├── pe_toolkit/                  the modules
    └── tests/                       16 invariant tests
```

## Do this first

Cover details are already filled in (`toolkit/data/student.json`). To change
anything, edit that file and rebuild:

```
cd toolkit && python run_all.py
```

## Commands

| Command | What it does | Needs API key |
|---|---|---|
| `python run_all.py` | Checks invariants, renders figures, builds MD + DOCX + PDF | No |
| `python run_all.py --check` | Invariants and word counts only | No |
| `python run_all.py --measure` | Runs the Phase 8 V1–V4 ladder and the Phase 7 probe live, records transcripts, writes a verification worksheet | **Yes** |
| `python run_all.py --chain --live` | Runs the seven-step Phase 10 chain | **Yes** |
| `python tests/test_toolkit.py` | The test suite | No |

Install: `pip install -r requirements.txt`

## How it fits together

Everything in the report is generated from the CSVs in `toolkit/data/`. No
number is typed twice, and `pe_toolkit.audit.check_consistency()` enforces the
cross-file invariants — most importantly that the Phase 7 audit table and the
Phase 8 V1 row describe the same run, since Phase 7 *is* the V1 probe.

Edit a CSV, run `python run_all.py`, and the tables, figures, counts and
narrative statistics all move together.

| File | Feeds |
|---|---|
| `data/sources.csv` | Phase 2 repository, Phase 11 bias, Appendix A |
| `data/claims.csv` | Phase 5 claim analysis, Phase 6 verification matrix, Phase 12 facts |
| `data/hallucination_audit.csv` | Phase 7 audit, summary, failure classes, Figures 1–2 |
| `data/contradictions.csv` | Phase 5 contradiction analysis |
| `data/prompt_versions.csv` | Phase 8 ladder, Figures 3–4 |
| `data/llm_comparison.csv` | Phase 9 comparison, Figures 5–6 |
| `data/reliability.csv`, `data/bias.csv` | Phase 11 |
| `pe_toolkit/content.py` | All long-form prose |
| `pe_toolkit/prompts.py` | Every prompt, shared by the pipeline and Appendix B |

## Important — read before submitting

The **prompts, method, source list, analysis and written report are complete**.

The **numeric results are a worked template**: internally consistent and
realistic, but not yet measurements you have taken. The report prints a
"Provenance and Declaration" notice on page 1 listing exactly what is
outstanding, driven by `data/run_status.json`.

To convert the template into your own results:

1. Run the phase — `python run_all.py --measure` covers Phases 7 and 8.
2. Verify each generated statement by hand against a real source. This is the
   assignment; do not automate it. (The toolkit deliberately does not let the
   model grade itself — that failure is one of the study's own findings.)
3. Replace the values in the matching CSV with what you observed.
4. Set the flag in `data/run_status.json` to `true` and rebuild.

The notice shrinks as you go and disappears when nothing is outstanding.

Separately, **Appendix A** lists every source that has not yet been re-opened
and checked against its primary document. URLs move and reports get revised.
Open each one, confirm the figure and the link, then set `student_verified` to
`Y` in `data/sources.csv`.

## Design notes

- **Model** is pinned to `claude-opus-5` rather than a floating alias, so runs
  are reproducible.
- **Charts** follow one scale per axis (the 1–5 scores and the percentage rates
  are therefore always separate figures), with direct value labels. The palette
  was checked with a CVD validator: the three-tool categorical set passes
  all-pairs colour-blind separation, and V1–V4 uses a single-hue ordinal ramp
  because versions are an ordered progression, not four identities.
- **Verification outcomes** use a reserved status palette that is never reused
  as a series colour.
