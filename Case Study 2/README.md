# Case Study 2 — AI-Assisted Literature Review and Review Paper

**Topic:** Retrieval-Augmented Generation for Hallucination Mitigation in Large Language Models
**Domain:** Generative AI → LLMs → RAG → hallucination mitigation and grounding verification

---

## Submit these

```
output/
├── CASE_STUDY_2_WORKBOOK.docx    Phases 1–13, all tables  (26 pages)
├── CASE_STUDY_2_WORKBOOK.pdf
├── REVIEW_PAPER_IEEE.docx        5058 words, 45 refs, IEEE 2-column  (8 pages)
└── REVIEW_PAPER_IEEE.pdf
```

## Requirements check

| Requirement | Required | Delivered |
|---|---|---|
| Research papers | 30 min (40–50 preferred) | **45** (35 fully matrixed + 10 context refs) |
| Publication years | 2015–present | 2019–2026 |
| Publication sources | IEEE/Springer/ACM/Elsevier/MDPI/Wiley/arXiv | all represented (see Phase 2) |
| Review paper length | 4000–6000 words | **5058** |
| References | 30 min | **45**, all cited |
| Citation format | IEEE | numbered by first appearance |
| Similarity / AI detection / grammar | <10% / <10% / >90% | **you must run these** — see below |

## Rebuild

```
pip install pandas python-docx docx2pdf
python fetch_papers.py     # re-resolve all 45 records from CrossRef + arXiv (needs internet)
python seed_data.py        # regenerate the analysis tables
python build.py            # workbook + paper, DOCX and PDF
python build.py --check    # validation and word counts only
```

## How it fits together

| File | Role |
|---|---|
| `fetch_papers.py` | Resolves every record against the CrossRef and arXiv APIs. **No bibliographic data came from a language model.** |
| `seed_data.py` | The analysis — matrix, evolution, comparison, limitations, gaps, future work, prompt log |
| `content.py` | All prose plus the full review-paper text, with `[P01]`-style citation tokens |
| `build.py` | Renders both documents; renumbers citations to IEEE numerals and generates the reference list |
| `data/papers.csv` | Verified repository — never hand-edited |

Citations are written as `[P01]` tokens and renumbered at build time, so a
citation can never point at the wrong reference. Change the prose, rebuild, and
the numbering and reference list follow automatically.

## Two things you must do before submitting

**1. Run the originality scans (Phase 12).** Similarity, AI-detection, grammar
and readability scores are left blank on purpose. Only you can generate them,
using your institution's tools, against `output/REVIEW_PAPER_IEEE.docx`. A
fabricated originality score would be precisely the failure this course is
about. The table is ready to fill in.

**2. Re-check the flagged figures (Appendix B).** Every numeric result quoted
from a paper carries a `figure_confidence` flag in `data/comparison.csv`. Rows
marked `check` are recalled from reading rather than re-read during compilation;
they are listed in Appendix B of the workbook. Open those papers, confirm the
figure, and set the flag to `high`.

Everything else — the 45 records, their titles, authors, years, venues and DOIs
— was resolved from publisher metadata and needs no further verification.

## Notes on method

Two deliberate departures from the manual, both argued in the documents:

- **Phase 6 is architectural, not numeric.** The manual's AI/ML matrix asks for
  Accuracy/Precision/Recall/F1. Those columns are not populated, because the
  systems compared use different base models, retrievers and evaluation splits —
  a single ranking would compare experimental setups rather than methods.
  Section IV of the paper makes this argument explicitly.
- **Phase 8 gaps are derived, not requested.** Following the manual's own
  instruction not to ask AI to "find research gaps", all seven gaps come from the
  Phase 7 limitation frequency distribution (105 codings across 35 papers), each
  traceable to specific paper IDs.
