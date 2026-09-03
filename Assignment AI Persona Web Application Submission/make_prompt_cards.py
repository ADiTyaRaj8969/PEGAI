#!/usr/bin/env python
"""Generates PROMPT_CARDS.md from the persona definitions inside index.html.

The Prompt Card document is a graded deliverable in its own right, so it is
extracted from the application rather than retyped - the document and the app
cannot disagree about what is actually sent to Gemini.

Run:  python make_prompt_cards.py
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
ELEMENTS = [
    ("Role", "role", "Who should the AI act as?"),
    ("Audience", "audience", "Who is the response for?"),
    ("Context", "context", "What background should the AI consider?"),
    ("Format", "format", "How should the response be presented?"),
    ("Constraints", "constraints", "What rules or limits apply?"),
    ("Language", "language", "Which language should be used?"),
]


def extract_personas() -> list[dict]:
    """Pull the PERSONAS array out of index.html by evaluating it in Node."""
    html = (HERE / "index.html").read_text(encoding="utf-8")
    js = re.findall(r"<script[^>]*>(.*?)</script>", html, re.S)[-1]
    start = js.index("const PERSONAS")
    end = js.index("const SAMPLES")
    snippet = js[start:end] + "\nprocess.stdout.write(JSON.stringify(PERSONAS));"

    tmp = HERE / "_personas.js"
    tmp.write_text(snippet, encoding="utf-8")
    try:
        out = subprocess.run([_node(), str(tmp)], capture_output=True,
                             text=True, check=True, timeout=60).stdout
    finally:
        tmp.unlink(missing_ok=True)
    return json.loads(out)


def _node() -> str:
    for exe in ("node", "node.exe"):
        try:
            subprocess.run([exe, "--version"], capture_output=True, check=True, timeout=30)
            return exe
        except (FileNotFoundError, subprocess.SubprocessError):
            continue
    raise RuntimeError("Node.js is required to extract the persona definitions.")


def main() -> int:
    personas = extract_personas()

    lines = [
        "# Prompt Cards — AI Career Counsellor",
        "",
        "**Aditya Raj** · 92301733062 · ICT · 7EK1'A'",
        "",
        "Every persona in the application is defined by these six elements. The",
        "cards below are extracted directly from `index.html`, so this document",
        "is exactly what the application sends to the Gemini API.",
        "",
        "## The six elements",
        "",
        "| Element | Meaning |",
        "|---|---|",
    ]
    lines += [f"| **{label}** | {meaning} |" for label, _, meaning in ELEMENTS]

    lines += [
        "",
        "## How a card becomes a prompt",
        "",
        "```",
        "Role + Audience + Context + Format + Constraints + Language + User Question",
        "                              ↓",
        "                        Final Prompt",
        "                              ↓",
        "                         Gemini API",
        "                              ↓",
        "                      Persona Response",
        "```",
        "",
        "For multiple personas, every selected card is placed in **one** prompt and",
        "the model returns one structured JSON entry per persona — so N personas",
        "cost one API request, not N.",
        "",
        "---",
        "",
    ]

    for i, p in enumerate(personas, start=1):
        lines += [
            f"## {i}. {p['name']}",
            "",
            f"*{p['blurb']}*",
            "",
            "| Element | Value |",
            "|---|---|",
        ]
        for label, key, _ in ELEMENTS:
            value = p["card"][key].replace("|", "\\|")
            lines.append(f"| **{label}** | {value} |")
        lines.append("")

    lines += [
        "---",
        "",
        "## Why the personas actually differ",
        "",
        "Persona differentiation is enforced in three places, not left to chance:",
        "",
        "1. **Different Role and Context.** Each card frames the same question",
        "   against a different professional concern — skills, hireability,",
        "   research fit, market validation, examination calendars.",
        "2. **Different Format.** Each persona's answer is structured by its own",
        "   Format field, so the replies do not even share a shape.",
        "3. **An explicit instruction.** The composed prompt states that the",
        "   personas must genuinely differ and must not paraphrase one another.",
        "",
        "Each card also carries three safety rules: refuse out-of-scope questions",
        "(`inScope: false`), never guarantee jobs, salaries, admission or funding,",
        "and never invent statistics, deadlines, cut-offs or company names.",
        "",
        f"*Generated from index.html — {len(personas)} personas × {len(ELEMENTS)} elements.*",
    ]

    out = HERE / "PROMPT_CARDS.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out.name}: {len(personas)} personas x {len(ELEMENTS)} elements")

    missing = [(p["name"], k) for p in personas for _, k, _ in ELEMENTS
               if not p["card"].get(k)]
    if missing:
        print("MISSING ELEMENTS:", missing)
        return 1
    print("All personas have all six elements.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
