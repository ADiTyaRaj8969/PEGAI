# Phase 5 — Streamlit UI

**12:25 – 12:50 · No new prompts · Depends on Phases 2–4**

## Goal

A judge who has never seen the project can type an unseen word problem and walk the hint ladder
without being told how.

## What the UI Must Prove

The UI is not decoration — it is where three graded requirements become visible:

| Requirement | How the UI shows it |
|---|---|
| 3-level ladder, revealed in order (FR-3.5) | Buttons gate: L2 locked until L1 is shown |
| The leak check runs (FR-4.6) | A verdict badge under every hint |
| V1 vs V2 comparison (brief) | Side-by-side panel on the same input |

A green "leak check passed" badge on each hint is the single highest-value pixel in the demo. It
turns an invisible guarantee into something a judge can see firing.

---

## Layout

```
┌──────────────────────────────────────────────────────────────┐
│  Hint-Based Math Tutor          Team 5 · Problem 13          │
├──────────────────────────────────────────────────────────────┤
│  Sample problem  [ Train / speed            ▾ ]              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ A train covers 120 km in 2 hours. What is its average  │  │
│  │ speed?                                                 │  │
│  └────────────────────────────────────────────────────────┘  │
│                                            [ Start tutoring ]│
├──────────────────────────────────────────────────────────────┤
│  HINT 1 of 3                                                 │
│  This problem ties together three quantities: how far...     │
│  ✅ leak check passed · alias + numeric + equation scan      │
│                                                              │
│  [ Show hint 2 ]   [ Show hint 3 (locked) ]                  │
├──────────────────────────────────────────────────────────────┤
│  CHECK MY WORKING                                            │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ 1. speed = distance x time                             │  │
│  │ 2. speed = 120 x 2 = 240                               │  │
│  └────────────────────────────────────────────────────────┘  │
│                                           [ Check my steps ] │
├──────────────────────────────────────────────────────────────┤
│  ☐ Compare V1 vs V2                                          │
└──────────────────────────────────────────────────────────────┘
```

---

## Implementation Sketch

```python
# app.py
import streamlit as st
from tutor.solver import solve
from tutor.hints import generate_ladder, generate_v1
from tutor.guard import safe_hint
from tutor.llm import LLMError

st.set_page_config(page_title="Hint-Based Math Tutor", page_icon="🧮")
st.title("🧮 Hint-Based Math Tutor")
st.caption("Team 5 · Problem 13 · Progressive hints that never give the answer away")

SAMPLES = {
    "— type your own —": "",
    "Train / speed": "A train covers 120 km in 2 hours. What is its average speed?",
    "Shirt / discount": "A shirt costs Rs 800. The shopkeeper gives a 15% discount. What is the selling price?",
    "Ravi / ages": "Ravi is 3 times as old as his son. In 10 years he will be twice as old. How old is Ravi now?",
    "Pipes / work rate": "Pipe A fills a tank in 6 hours, pipe B in 3 hours. How long together?",
    "Garden / area": "A rectangular garden is 15 m by 8 m. A 2 m path runs around it. Find the path's area.",
}

ss = st.session_state
ss.setdefault("level", 0)

choice = st.selectbox("Sample problem", list(SAMPLES))
problem = st.text_area("Problem", value=SAMPLES[choice], height=90,
                       placeholder="Paste any school-level word problem…")

if st.button("Start tutoring", type="primary"):
    if not problem.strip():                                   # FR-6.5
        st.warning("Type a problem first.")
    elif len(problem) > 2000:                                 # FR-1.1
        st.warning("That's too long — keep it under 2000 characters.")
    else:
        try:
            with st.spinner("Reading the problem…"):
                sol = solve(problem)
            if not sol.is_math_word_problem:                   # FR-1.3
                st.error(f"That doesn't look like a math word problem. "
                         f"{sol.reject_reason or ''} Try one of the samples above.")
            else:
                ss.sol = sol
                ss.ladder = generate_ladder(problem, sol)
                ss.problem, ss.level = problem, 1
        except LLMError as e:                                  # FR-6.6
            st.error(f"Could not reach the tutor right now. {e}")

# ── hint ladder, revealed in order (FR-3.5) ──────────────────────────
if ss.level:
    for lvl in range(1, ss.level + 1):
        raw = getattr(ss.ladder, f"l{lvl}")
        hint, verdict = safe_hint(lvl, raw, ss.sol)
        st.markdown(f"**HINT {lvl} of 3**")
        st.info(hint)
        if lvl < 3:
            if verdict.leaked:
                st.warning("⚠️ leak detected — hint regenerated before display")
            else:
                st.success("✅ leak check passed · alias + numeric + equation scan")
    if ss.level < 3 and st.button(f"Show hint {ss.level + 1}"):
        ss.level += 1
        st.rerun()
```

The gating is `ss.level` alone: a hint cannot render before the level counter reaches it, so the
ordering requirement is structural rather than a disabled button a judge might bypass.

---

## The V1 vs V2 Panel

This is the brief's "side-by-side comparison in the demo". Keep it simple:

```python
if st.checkbox("Compare V1 vs V2"):
    a, b = st.columns(2)
    with a:
        st.subheader("V1 — single prompt")
        st.caption("Zero-shot. One instruction not to reveal the answer. No verification.")
        st.text(generate_v1(ss.problem))
        st.error("No programmatic check — a leak here reaches the student.")
    with b:
        st.subheader("V2 — decomposed + guarded")
        st.caption("Solve → hint → verify. Five techniques, deterministic guard.")
        for lvl in (1, 2, 3):
            hint, v = safe_hint(lvl, getattr(ss.ladder, f"l{lvl}"), ss.sol)
            st.markdown(f"**L{lvl}** {hint}")
        st.success("Every L1/L2 hint passed the leak guard before display.")
```

---

## Error Surfaces (FR-6.6)

Every failure gets a sentence a student could understand. No stack traces.

| Failure | Message |
|---|---|
| Empty input | "Type a problem first." |
| Over 2000 chars | "That's too long — keep it under 2000 characters." |
| Not a math problem | "That doesn't look like a math word problem. Try one of the samples above." |
| API down / quota | "Could not reach the tutor right now." |
| Unparseable output | "Something went wrong reading the solution. Try rephrasing the problem." |

---

## Exit Criteria

- [ ] A teammate who did not build the UI runs an unseen problem end to end, unaided
- [ ] L2 cannot be reached without viewing L1; L3 not without L2
- [ ] The leak badge appears under every L1 and L2 hint
- [ ] The V1/V2 panel renders both on one screen
- [ ] All five error surfaces tested — none crashes the app
- [ ] Browser zoom at 100% shows the ladder without scrolling (projector check)

**Next:** [Phase 6 — Wrong-Step Detection](PHASE_6_DIAGNOSE.md)
