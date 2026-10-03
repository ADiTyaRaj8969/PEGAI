"""FastAPI backend for the React UI.

Run:  python -m uvicorn server:app --reload --port 8000

The hint ladder is gated **server-side**: level N+1 is refused until level N has
been requested. The Streamlit version gated in the UI, which a student could
bypass by reading the network tab — here the later hints never leave the server
until they are earned.
"""
import uuid
from dataclasses import dataclass, field

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os

from tutor.llm import LLMError
from tutor.solver import solve, Solution
from tutor.hints import generate_ladder, generate_v1, Ladder
from tutor.guard import safe_hint
from tutor.diagnose import diagnose
from tutor.llm import complete_json
from tutor.prompts import (
    is_answer_request, ANSWER_REQUEST_REFUSAL, OFF_TOPIC_REFUSAL,
    TOPICS, PRACTICE_PROMPT,
)

app = FastAPI(title="Hint-Based Math Tutor API")

# The Vite dev server runs on another port during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SAMPLES = [
    {"label": "Speed — train", "problem": "A train covers 120 km in 2 hours. What is its average speed?"},
    {"label": "Percentage — discount", "problem": "A shirt costs Rs 800. The shopkeeper gives a 15% discount. What is the selling price?"},
    {"label": "Ages — Ravi", "problem": "Ravi is 3 times as old as his son. In 10 years he will be twice as old. How old is Ravi now?"},
    {"label": "Work rate — pipes", "problem": "Pipe A fills a tank in 6 hours and pipe B in 3 hours. How long do they take together?"},
    {"label": "Mensuration — garden", "problem": "A rectangular garden is 15 m long and 8 m wide. What is its area?"},
    {"label": "Compound interest", "problem": "Rs 10000 is invested at 10% per annum compounded annually. What is the amount after 2 years?"},
    {"label": "Quadratic equations", "problem": "Solve x^2 - 5x + 6 = 0 for x."},
    {"label": "HCF and LCM", "problem": "Find the HCF and LCM of 24 and 36."},
    {"label": "Arithmetic progression", "problem": "The 5th term of an AP is 17 and the 9th term is 29. Find the first term."},
    {"label": "Trigonometry", "problem": "A ladder leans against a wall at 60 degrees to the ground and its foot is 3 m from the wall. How long is the ladder?"},
    {"label": "Probability", "problem": "Two dice are thrown together. What is the probability that the sum is 9?"},
    {"label": "Permutations", "problem": "In how many ways can the letters of the word LEVEL be arranged?"},
    {"label": "Coordinate geometry", "problem": "Find the distance between the points (3, 4) and (7, 1)."},
    {"label": "Statistics", "problem": "Find the mean of 12, 15, 18, 21 and 24."},
    {"label": "Limits", "problem": "Evaluate the limit of (x^2 - 9)/(x - 3) as x approaches 3."},
    {"label": "Derivatives", "problem": "Differentiate f(x) = 3x^2 + 5x - 7 with respect to x."},
    {"label": "Integrals", "problem": "Evaluate the integral of 2x dx from x = 0 to x = 3."},
    {"label": "Matrices", "problem": "Find the determinant of the matrix [[2, 3], [1, 4]]."},
    {"label": "Vector algebra", "problem": "Find the dot product of the vectors 2i + 3j + k and i - j + 4k."},
    {"label": "Complex numbers", "problem": "Find the modulus of the complex number 3 + 4i."},
]

MAX_CHARS = 2000


@dataclass
class Session:
    problem: str
    sol: Solution
    ladder: Ladder
    revealed: int = 0                       # highest level served so far
    cache: dict = field(default_factory=dict)
    v1: str | None = None


SESSIONS: dict[str, Session] = {}


class ProblemIn(BaseModel):
    problem: str


class WorkingIn(BaseModel):
    working: str


class AskIn(BaseModel):
    question: str


def _session(sid: str) -> Session:
    s = SESSIONS.get(sid)
    if not s:
        raise HTTPException(404, "Session not found. Start a new problem.")
    return s


def _label(slug: str) -> str:
    """'applications-of-derivatives' -> 'Applications of Derivatives'."""
    small = {"of", "and", "to"}
    words = [w if w in small else w.upper() if w in ("hcf", "lcm") else w.capitalize()
             for w in slug.split("-")]
    return " ".join(words)


# Canned problems indexed by topic, so a searched topic with a sample is instant.
_BY_TOPIC = {
    "speed-distance-time": 0, "percentage": 1, "age": 2, "work-rate": 3,
    "mensuration": 4, "compound-interest": 5, "quadratic-equations": 6,
    "hcf-and-lcm": 7, "arithmetic-progressions": 8, "trigonometry": 9,
    "probability": 10, "permutations-and-combinations": 11,
    "coordinate-geometry": 12, "statistics": 13, "limits": 14,
    "applications-of-derivatives": 15, "integrals": 16, "matrices": 17,
    "vector-algebra": 18, "complex-numbers": 19,
}


@app.get("/api/samples")
def samples():
    return SAMPLES


@app.get("/api/topics")
def topics(q: str = ""):
    """Searchable topic list. Matches on the slug and the readable label."""
    needle = q.strip().lower()
    out = []
    for slug in TOPICS:
        if slug == "other":
            continue
        label = _label(slug)
        if needle and needle not in slug.lower() and needle not in label.lower():
            continue
        idx = _BY_TOPIC.get(slug)
        out.append({
            "slug": slug,
            "label": label,
            "sample": SAMPLES[idx]["problem"] if idx is not None else None,
        })
    return out


class TopicIn(BaseModel):
    topic: str


@app.post("/api/practice")
def practice(body: TopicIn):
    """Generate a fresh problem for a topic that has no canned sample."""
    slug = (body.topic or "").strip()
    if slug not in TOPICS:
        raise HTTPException(400, "Unknown topic.")
    try:
        d = complete_json(PRACTICE_PROMPT.format(topic=_label(slug)), temperature=0.8)
    except LLMError as e:
        raise HTTPException(503, f"Could not generate a problem. {e}")
    except ValueError as e:
        raise HTTPException(502, f"Could not read the generated problem. ({e})")
    problem = (d.get("problem") or "").strip()
    if not problem:
        raise HTTPException(502, "The model returned an empty problem. Try again.")
    return {"topic": slug, "problem": problem}


@app.post("/api/session")
def start(body: ProblemIn):
    problem = (body.problem or "").strip()
    if not problem:                                          # FR-6.5
        raise HTTPException(400, "Type a problem first.")
    if len(problem) > MAX_CHARS:                             # FR-1.1
        raise HTTPException(400, f"That's too long ({len(problem)} characters) — keep it under {MAX_CHARS}.")

    try:
        sol = solve(problem)
    except LLMError as e:                                    # FR-6.6 / 6.7
        msg = str(e).lower()
        if "safety" in msg or "blocked" in msg:
            raise HTTPException(400, "I can't help with that. Send me a math word problem instead.")
        raise HTTPException(503, f"Could not reach the tutor right now. {e}")
    except ValueError as e:                                  # FR-6.4
        raise HTTPException(502, f"Could not read the solution. Try rephrasing the problem. ({e})")

    if not sol.is_math_word_problem:                         # FR-1.3 / 6.1
        raise HTTPException(400, OFF_TOPIC_REFUSAL + (f" ({sol.reject_reason})" if sol.reject_reason else ""))

    try:
        ladder = generate_ladder(problem, sol)
    except (LLMError, ValueError) as e:
        raise HTTPException(503, f"Could not write the hints. {e}")

    sid = uuid.uuid4().hex
    SESSIONS[sid] = Session(problem=problem, sol=sol, ladder=ladder)
    return {"session_id": sid, "topic": sol.topic, "levels": 3}


@app.get("/api/session/{sid}/hint/{level}")
def hint(sid: str, level: int):
    s = _session(sid)
    if level not in (1, 2, 3):
        raise HTTPException(400, "Levels are 1, 2 and 3.")
    if level > s.revealed + 1:                               # FR-3.5, enforced here
        raise HTTPException(
            403, f"Hint {level} is locked. View hint {s.revealed + 1} first.")

    if level not in s.cache:
        text, verdict = safe_hint(level, s.ladder.level(level), s.sol)
        s.cache[level] = {
            "level": level,
            "hint": text,
            "guarded": level < 3,
            "leak_detected": verdict.leaked,
            "leak_where": verdict.where,
        }
    s.revealed = max(s.revealed, level)
    return s.cache[level]


@app.post("/api/session/{sid}/diagnose")
def check_working(sid: str, body: WorkingIn):
    s = _session(sid)
    working = (body.working or "").strip()
    if not working:
        raise HTTPException(400, "Write your working first.")
    try:
        d = diagnose(s.problem, working, s.sol)
    except LLMError as e:
        raise HTTPException(503, f"Could not reach the tutor right now. {e}")
    except ValueError as e:
        raise HTTPException(502, f"Could not read that working. Try one step per line. ({e})")
    return {
        "status": d.status,
        "first_wrong_step": d.first_wrong_step,
        "what_they_did": d.what_they_did,
        "why_wrong": d.why_wrong,
        "targeted_hint": d.targeted_hint,
    }


@app.post("/api/session/{sid}/ask")
def ask(sid: str, body: AskIn):
    """Direct answer requests are refused with static text — no model call.

    A request to break the core guarantee should not be routed through the
    thing being guarded (FR-6.3).
    """
    s = _session(sid)
    if is_answer_request(body.question or ""):
        return {"refused": True,
                "message": ANSWER_REQUEST_REFUSAL.format(level=max(s.revealed, 1))}
    return {"refused": False,
            "message": "Use the hint buttons — this tutor only gives graded hints."}


@app.get("/api/session/{sid}/compare")
def compare(sid: str):
    """V1 vs V2 on the same problem, for the side-by-side demo panel."""
    s = _session(sid)
    if s.v1 is None:
        try:
            s.v1 = generate_v1(s.problem)
        except LLMError as e:
            raise HTTPException(503, f"V1 call failed. {e}")
    v2 = []
    for lvl in (1, 2, 3):
        if lvl not in s.cache:
            text, verdict = safe_hint(lvl, s.ladder.level(lvl), s.sol)
            s.cache[lvl] = {"level": lvl, "hint": text, "guarded": lvl < 3,
                            "leak_detected": verdict.leaked, "leak_where": verdict.where}
        v2.append(s.cache[lvl])
    return {"v1_raw": s.v1, "v2": v2}


# ── serve the built React app, when it exists ────────────────────────
DIST = os.path.join(os.path.dirname(__file__), "web", "dist")
if os.path.isdir(DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(DIST, "assets")), name="assets")

    @app.get("/")
    def index():
        return FileResponse(os.path.join(DIST, "index.html"))
