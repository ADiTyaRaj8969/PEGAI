#!/usr/bin/env python
"""Build the verified paper repository.

Every entry is resolved live against CrossRef (for DOIs) or the arXiv API, so
the title, author list, year and venue in `data/papers.csv` come from the
publisher's own record rather than from anyone's recollection. Nothing in this
review is cited on trust.

Run:  python fetch_papers.py
"""

from __future__ import annotations

import csv
import json
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

DATA = Path(__file__).parent / "data"
UA = {"User-Agent": "case-study-2/1.0 (mailto:student@example.edu)"}
ARXIV_NS = {"a": "http://www.w3.org/2005/Atom", "ar": "http://arxiv.org/schemas/atom"}

# (id, theme, doi_or_None, arxiv_or_None, venue_override, relevance)
# venue_override is used only where the canonical venue is not in CrossRef
# (NeurIPS / ICLR / ICML / AAAI proceedings are largely absent from it).
PAPERS = [
    # A - Retrieval foundations and RAG architectures
    ("P01", "RAG architecture", None, "2005.11401", "Adv. Neural Inf. Process. Syst. (NeurIPS)", 5),
    ("P02", "Retrieval", "10.18653/v1/2020.emnlp-main.550", "2004.04906", None, 5),
    ("P03", "RAG architecture", None, "2002.08909", "Proc. Int. Conf. Mach. Learn. (ICML)", 4),
    ("P04", "RAG architecture", "10.18653/v1/2021.eacl-main.74", "2007.01282", None, 5),
    ("P05", "RAG architecture", None, "2112.04426", "Proc. Int. Conf. Mach. Learn. (ICML)", 4),
    ("P06", "Retrieval", "10.1109/tbdata.2019.2921572", "1702.08734", None, 4),
    ("P07", "RAG architecture", "10.1162/tacl_a_00605", "2302.00083", None, 4),
    ("P08", "RAG architecture", "10.18653/v1/2024.naacl-long.463", "2301.12652", None, 4),
    # B - Parametric memory and its limits
    ("P09", "Parametric memory", "10.18653/v1/D19-1250", "1909.01066", None, 4),
    ("P10", "Parametric memory", "10.18653/v1/2023.acl-long.546", "2212.10511", None, 5),
    ("P11", "Context utilisation", "10.1162/tacl_a_00638", "2307.03172", None, 5),
    # C - Hallucination taxonomy, causes, theory
    ("P12", "Hallucination theory", "10.1145/3571730", "2202.03629", None, 5),
    ("P13", "Hallucination theory", "10.1145/3703155", "2311.05232", None, 5),
    ("P14", "Hallucination theory", None, "2309.01219", "arXiv preprint", 4),
    ("P15", "Hallucination theory", None, "2401.11817", "arXiv preprint", 4),
    ("P16", "Hallucination theory", None, "2509.04664", "arXiv preprint", 4),
    # D - Detection and factuality metrics
    ("P17", "Detection", "10.18653/v1/2023.emnlp-main.557", "2303.08896", None, 5),
    ("P18", "Detection", "10.1038/s41586-024-07421-0", None, None, 5),
    ("P19", "Benchmark", "10.18653/v1/2022.acl-long.229", "2109.07958", None, 4),
    ("P20", "Evaluation metric", "10.18653/v1/2023.emnlp-main.741", "2305.14251", None, 5),
    ("P21", "Detection", "10.1109/taslpro.2025.3635038", None, None, 4),
    # E - RAG-based mitigation pipelines
    ("P22", "Mitigation", "10.18653/v1/2021.findings-emnlp.320", "2104.07567", None, 5),
    ("P23", "Mitigation", None, "2310.11511", "Proc. Int. Conf. Learn. Represent. (ICLR)", 5),
    ("P24", "Mitigation", None, "2401.15884", "arXiv preprint", 5),
    ("P25", "Mitigation", "10.18653/v1/2023.emnlp-main.495", "2305.06983", None, 5),
    ("P26", "Mitigation", "10.18653/v1/2023.acl-long.557", "2212.10509", None, 5),
    ("P27", "Mitigation", "10.18653/v1/2024.findings-acl.212", "2309.11495", None, 5),
    ("P28", "Mitigation", "10.18653/v1/2023.acl-long.910", "2210.08726", None, 4),
    ("P29", "Mitigation", None, "2404.16130", "arXiv preprint", 5),
    # F - Evaluation frameworks and benchmarks
    ("P30", "Evaluation metric", "10.18653/v1/2024.eacl-demo.16", "2309.15217", None, 5),
    ("P31", "Benchmark", None, "2309.01431", "Proc. AAAI Conf. Artif. Intell.", 5),
    ("P32", "Benchmark", "10.18653/v1/2024.acl-long.585", "2401.00396", None, 5),
    # G - Recent journal syntheses and applied deployment
    ("P33", "Survey", "10.3390/math13050856", None, None, 5),
    ("P34", "Applied deployment", "10.3390/electronics14214227", None, None, 5),
    ("P35", "Applied deployment", "10.1109/access.2026.3659997", None, None, 4),
]

# Where a paper is cited by its proceedings rather than its preprint, the
# arXiv posting year is not the publication year. These are the three cases.
YEAR_OVERRIDE = {
    "P05": 2022,  # RETRO - arXiv Dec 2021, published ICML 2022
    "P23": 2024,  # Self-RAG - arXiv Oct 2023, published ICLR 2024
    "P31": 2024,  # RGB benchmark - arXiv Sep 2023, published AAAI 2024
}

# Additional verified references cited in the review paper but not carried
# through the Phase 3 matrix.
EXTRA = [
    ("R36", "Survey", None, "2312.10997", "arXiv preprint", 4),
    ("R37", "Survey", "10.1145/3637528.3671470", "2405.06211", None, 4),
    ("R38", "Survey", "10.1016/j.cosrev.2026.100970", None, None, 4),
    ("R39", "Survey", "10.1007/s10462-025-11454-w", None, None, 4),
    ("R40", "Survey", None, "2501.09136", "arXiv preprint", 4),
    ("R41", "Survey", None, "2408.08921", "arXiv preprint", 4),
    ("R42", "Mitigation", None, "2401.18059", "Proc. Int. Conf. Learn. Represent. (ICLR)", 4),
    ("R43", "Mitigation", None, "2307.03987", "arXiv preprint", 4),
    ("R44", "Applied deployment", "10.1002/aisy.202500255", None, None, 3),
    ("R45", "Survey", None, "2510.24476", "arXiv preprint", 4),
]


def crossref(doi: str) -> dict:
    req = urllib.request.Request("https://api.crossref.org/works/" + urllib.parse.quote(doi), headers=UA)
    m = json.load(urllib.request.urlopen(req, timeout=40))["message"]
    authors = [
        f"{a.get('given','')} {a.get('family','')}".strip()
        for a in m.get("author", [])
        if a.get("family")
    ]
    container = m.get("container-title") or [""]
    return {
        "title": (m.get("title") or [""])[0].strip(),
        "authors": authors,
        "year": (m.get("issued", {}).get("date-parts", [[None]])[0] or [None])[0],
        "venue": container[0] if container else "",
        "publisher": m.get("publisher", ""),
        "volume": m.get("volume", ""),
        "pages": m.get("page", "") or m.get("article-number", ""),
        "doi": m.get("DOI", ""),
    }


def arxiv(ids: list[str]) -> dict[str, dict]:
    url = "https://export.arxiv.org/api/query?id_list=" + ",".join(ids) + "&max_results=60"
    feed = ET.fromstring(urllib.request.urlopen(url, timeout=60).read())
    out = {}
    for e in feed.findall("a:entry", ARXIV_NS):
        raw = e.find("a:id", ARXIV_NS).text.rsplit("/", 1)[-1]
        base = raw.split("v")[0]
        out[base] = {
            "title": " ".join(e.find("a:title", ARXIV_NS).text.split()),
            "authors": [a.find("a:name", ARXIV_NS).text for a in e.findall("a:author", ARXIV_NS)],
            "year": int(e.find("a:published", ARXIV_NS).text[:4]),
            "arxiv": base,
        }
    return out


def main() -> int:
    rows = PAPERS + EXTRA
    ax_ids = sorted({a for _, _, _, a, _, _ in rows if a})
    print(f"Resolving {len(ax_ids)} arXiv records...")
    ax: dict[str, dict] = {}
    for i in range(0, len(ax_ids), 14):
        ax.update(arxiv(ax_ids[i : i + 14]))
        time.sleep(3)
    print(f"  got {len(ax)}")

    records = []
    for pid, theme, doi, ax_id, venue_override, relevance in rows:
        rec = {"id": pid, "theme": theme, "relevance": relevance}
        if doi:
            print(f"  {pid}  CrossRef {doi}")
            rec.update(crossref(doi))
            time.sleep(1)
        elif ax_id and ax_id in ax:
            rec.update(ax[ax_id])
            rec.update({"publisher": "arXiv", "volume": "", "pages": "", "doi": ""})
        else:
            print(f"  {pid}  UNRESOLVED")
            continue

        if ax_id:
            rec["arxiv"] = ax_id
        if venue_override:
            rec["venue"] = venue_override
        if pid in YEAR_OVERRIDE:
            rec["year"] = YEAR_OVERRIDE[pid]
        if not rec.get("publisher"):
            rec["publisher"] = "arXiv"

        author_list = rec.get("authors", [])
        rec["authors_full"] = "; ".join(author_list)
        rec["author_short"] = (
            author_list[0].split()[-1] + (" et al." if len(author_list) > 1 else "")
            if author_list
            else ""
        )
        rec["n_authors"] = len(author_list)
        records.append(rec)

    DATA.mkdir(exist_ok=True)
    fields = ["id", "theme", "title", "author_short", "authors_full", "n_authors",
              "year", "venue", "publisher", "volume", "pages", "doi", "arxiv", "relevance"]
    with (DATA / "papers.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for rec in records:
            writer.writerow({k: rec.get(k, "") for k in fields})

    print(f"\nWrote {len(records)} verified records to data/papers.csv")
    matrix = [r for r in records if r["id"].startswith("P")]
    print(f"  matrix papers : {len(matrix)}")
    print(f"  extra refs    : {len(records) - len(matrix)}")
    years = [r["year"] for r in records if r.get("year")]
    print(f"  year range    : {min(years)}-{max(years)}")
    pubs: dict[str, int] = {}
    for r in records:
        key = r["publisher"].split()[0] if r["publisher"] else "?"
        pubs[key] = pubs.get(key, 0) + 1
    print("  publishers    :", ", ".join(f"{k} {v}" for k, v in sorted(pubs.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
