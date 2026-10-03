"""Phase 4 — the leak guard.

The brief asks for "a check that the answer is never leaked at levels 1-2".
That check is this module: plain Python, not a prompt. A model that leaks is
also a model that can wrongly report it did not, so the two failures are
correlated and the second cannot catch the first.

Three layers:
  1. leaks()     deterministic detection
  2. safe_hint() one regeneration with the leaked value named
  3. redact()    string substitution, which cannot fail
"""
import re
from dataclasses import dataclass
from fractions import Fraction

from tutor.llm import complete_json
from tutor.prompts import LEAK_CRITIQUE_PROMPT, LEVEL_CONTRACTS

WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
    "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
    "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
    "eighty": 80, "ninety": 90, "hundred": 100,
}

NUM_RE = re.compile(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?(?:\s*/\s*\d+)?")
TOL = 1e-6


@dataclass
class LeakVerdict:
    leaked: bool
    value: str | None = None      # what was found, for the critique prompt
    where: str | None = None      # which rule fired, for the demo


def _numbers_in(text: str) -> set[float]:
    """Every number in the text, including word forms and fractions."""
    found: set[float] = set()
    for m in NUM_RE.findall(text):
        try:
            found.add(float(Fraction(m.replace(" ", "").replace(",", ""))))
        except (ValueError, ZeroDivisionError):
            pass

    tokens = re.findall(r"[a-z]+", text.lower())
    for i, t in enumerate(tokens):                      # "sixty", "sixty five"
        if t in WORDS:
            n = WORDS[t]
            if i + 1 < len(tokens) and tokens[i + 1] in WORDS and WORDS[tokens[i + 1]] < 10:
                n += WORDS[tokens[i + 1]]
            found.add(float(n))
    return found


def leaks(hint: str, sol) -> LeakVerdict:
    """Deterministic answer-presence check (FR-4.1 - 4.3)."""
    if not hint:
        return LeakVerdict(False)

    # Rule 1 - alias string match, from the solver's answer_aliases
    low = hint.lower()
    for alias in sorted(sol.answer_aliases or [], key=len, reverse=True):
        if alias and alias.lower() in low:
            return LeakVerdict(True, alias, "alias match")

    # Rule 2 - numeric match within tolerance
    if sol.answer_numeric is not None:
        target = float(sol.answer_numeric)
        for n in _numbers_in(hint):
            if abs(n - target) < TOL:
                return LeakVerdict(True, str(sol.answer_numeric), "numeric match")

        # Rule 3 - the answer as the right-hand side of an equation (FR-4.3)
        for rhs in re.findall(r"=\s*([^.,;!?\n]+)", hint):
            for n in _numbers_in(rhs):
                if abs(n - target) < TOL:
                    return LeakVerdict(True, rhs.strip(), "equation RHS")

    return LeakVerdict(False)


MASK = "[hidden — try the next hint]"


def redact(hint: str, sol, verdict: LeakVerdict) -> str:
    """Last line of defence. Must not be able to fail (FR-4.5).

    Removes the literal leaked string, every alias, and any numeric token
    equal to the answer — so a near-miss on the literal value cannot let the
    answer through.
    """
    out = hint
    if verdict.value:
        out = re.sub(re.escape(verdict.value), MASK, out, flags=re.IGNORECASE)

    if sol.answer_numeric is not None:
        target = float(sol.answer_numeric)

        def _scrub(m: re.Match) -> str:
            try:
                if abs(float(Fraction(m.group().replace(" ", "").replace(",", ""))) - target) < TOL:
                    return MASK
            except (ValueError, ZeroDivisionError):
                pass
            return m.group()

        out = NUM_RE.sub(_scrub, out)
        for word, val in WORDS.items():                  # "sixty"
            if abs(val - target) < TOL:
                out = re.sub(rf"\b{word}\b", MASK, out, flags=re.IGNORECASE)

    for alias in sorted(sol.answer_aliases or [], key=len, reverse=True):
        if alias:
            out = re.sub(re.escape(alias), MASK, out, flags=re.IGNORECASE)

    return out


def safe_hint(level: int, hint: str, sol) -> tuple[str, LeakVerdict]:
    """Return a hint guaranteed free of the answer, plus the verdict for the UI.

    Level 3 may approach the answer, so it is exempt from the check.
    """
    if level >= 3:
        return hint, LeakVerdict(False)

    v = leaks(hint, sol)
    if not v.leaked:
        return hint, v

    try:
        retry = complete_json(LEAK_CRITIQUE_PROMPT.format(
            level=level,
            leaked_value=v.value,
            where=v.where,
            hint_text=hint,
            level_contract=LEVEL_CONTRACTS.get(level, ""),
        ))["hint"]
    except Exception:
        return redact(hint, sol, v), v       # regeneration failed, redact instead

    v2 = leaks(retry, sol)
    if not v2.leaked:
        return retry, v
    return redact(retry, sol, v2), v2
