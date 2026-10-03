"""Hint-Based Math Tutor — Team 5, Problem 13.

Phase 5 (UI) with the Phase 7 guardrails wired in.
Run with:  streamlit run app.py
"""
import streamlit as st

from tutor.llm import LLMError
from tutor.solver import solve
from tutor.hints import generate_ladder, generate_v1, parse_v1
from tutor.guard import safe_hint, leaks
from tutor.diagnose import diagnose
from tutor.prompts import (
    is_answer_request, ANSWER_REQUEST_REFUSAL, OFF_TOPIC_REFUSAL,
)

st.set_page_config(page_title="Hint-Based Math Tutor", layout="centered")

SAMPLES = {
    "— type your own —": "",
    "Train / speed": "A train covers 120 km in 2 hours. What is its average speed?",
    "Shirt / discount": "A shirt costs Rs 800. The shopkeeper gives a 15% discount. What is the selling price?",
    "Ravi / ages": "Ravi is 3 times as old as his son. In 10 years he will be twice as old. How old is Ravi now?",
    "Pipes / work rate": "Pipe A fills a tank in 6 hours and pipe B in 3 hours. How long do they take together?",
    "Garden / area": "A rectangular garden is 15 m long and 8 m wide. What is its area?",
}

MAX_CHARS = 2000

ss = st.session_state
ss.setdefault("level", 0)
ss.setdefault("hints", {})          # level -> (text, verdict), computed once
ss.setdefault("v1", {})             # problem -> V1 raw text, so reruns never re-call the model

st.title("Hint-Based Math Tutor")
st.caption("Team 5 · Problem 13 · Progressive hints that never give the answer away")


# ── problem intake ───────────────────────────────────────────────────
choice = st.selectbox("Sample problem", list(SAMPLES))
problem = st.text_area(
    "Problem", value=SAMPLES[choice], height=90,
    placeholder="Paste any school-level word problem…",
)

if st.button("Start tutoring", type="primary"):
    if not problem.strip():                                     # FR-6.5
        st.warning("Type a problem first.")
    elif len(problem) > MAX_CHARS:                              # FR-1.1
        st.warning(f"That's too long ({len(problem)} characters) — keep it under {MAX_CHARS}.")
    else:
        try:
            with st.spinner("Reading the problem…"):
                sol = solve(problem)
            if not sol.is_math_word_problem:                     # FR-1.3 / FR-6.1
                st.error(OFF_TOPIC_REFUSAL)
                if sol.reject_reason:
                    st.caption(sol.reject_reason)
                ss.level = 0
            else:
                with st.spinner("Writing hints…"):
                    ladder = generate_ladder(problem, sol)
                # Run the guard once per level and cache, so reruns are free.
                ss.hints = {
                    lvl: safe_hint(lvl, ladder.level(lvl), sol) for lvl in (1, 2, 3)
                }
                ss.sol, ss.ladder, ss.problem, ss.level = sol, ladder, problem, 1
        except LLMError as e:                                    # FR-6.6 / FR-6.7
            msg = str(e).lower()
            if "safety" in msg or "blocked" in msg:
                st.error("I can't help with that. Send me a math word problem instead.")
            else:
                st.error("Could not reach the tutor right now. Check your connection "
                         "or API key and try again.")
                st.caption(f"Technical detail: {e}")
        except ValueError as e:                                  # FR-6.4
            st.error("Something went wrong reading the solution. Try rephrasing the problem.")
            st.caption(f"Technical detail: {e}")


# ── hint ladder, revealed in order (FR-3.5) ──────────────────────────
if ss.level:
    st.divider()
    for lvl in range(1, ss.level + 1):
        hint, verdict = ss.hints[lvl]
        st.markdown(f"**HINT {lvl} of 3**")
        st.info(hint)
        if lvl < 3:
            if verdict.leaked:
                st.warning(f"Leak detected ({verdict.where}) — hint regenerated before display")
            else:
                st.success("Leak check passed · alias + numeric + equation scan")

    if ss.level < 3:
        if st.button(f"Show hint {ss.level + 1}"):
            ss.level += 1
            st.rerun()
    else:
        st.caption("That's all three hints — the last step is yours.")

    # Direct answer request (FR-6.3) — static refusal, no model call.
    asked = st.text_input("Ask the tutor something", placeholder="e.g. can you explain hint 2?")
    if asked:
        if is_answer_request(asked):
            st.error(ANSWER_REQUEST_REFUSAL.format(level=ss.level))
        else:
            st.caption("Use the hint buttons above — this tutor only gives graded hints.")


# ── check my working (Phase 6) ───────────────────────────────────────
if ss.level:
    st.divider()
    st.subheader("Check my working")
    working = st.text_area(
        "Your steps, one per line", height=110,
        placeholder="speed = distance x time\nspeed = 120 x 2 = 240",
    )
    if st.button("Check my steps"):
        if not working.strip():
            st.warning("Write your working first.")
        else:
            try:
                with st.spinner("Reading your working…"):
                    d = diagnose(ss.problem, working, ss.sol)
                if d.status == "correct":
                    st.success("Every step checks out. Well done.")
                elif d.status == "incomplete":
                    st.info("No mistakes so far — but you haven't finished yet.")
                else:
                    where = f"step {d.first_wrong_step}" if d.first_wrong_step else "your working"
                    st.error(f"First mistake: {where}")
                    if d.what_they_did:
                        st.caption(f"What you did: {d.what_they_did}")
                if d.targeted_hint:
                    st.info(d.targeted_hint)
            except LLMError as e:
                st.error("Could not reach the tutor right now.")
                st.caption(f"Technical detail: {e}")
            except ValueError as e:
                st.error("Could not read that working. Try one step per line.")
                st.caption(f"Technical detail: {e}")


# ── V1 vs V2 side by side (required by the brief) ────────────────────
if ss.level:
    st.divider()
    if st.checkbox("Compare V1 vs V2"):
        a, b = st.columns(2)
        with a:
            st.subheader("V1 — single prompt")
            st.caption("Zero-shot. One instruction not to reveal the answer. No verification.")
            try:
                if ss.problem not in ss.v1:
                    with st.spinner("Running V1…"):
                        ss.v1[ss.problem] = generate_v1(ss.problem)
                v1_text = ss.v1[ss.problem]
                st.text(v1_text)
                # V1 has no guard of its own; run ours over its output to show what it did.
                parts = parse_v1(v1_text)
                hits = [(l, leaks(parts.get(l, ""), ss.sol)) for l in (1, 2)]
                hits = [(l, v) for l, v in hits if v.leaked]
                if hits:
                    l, v = hits[0]
                    st.error(f"V1 leaked the answer at hint {l} ({v.where}: {v.value}) — "
                             "and nothing in V1 would have stopped it.")
                else:
                    st.warning("V1 did not leak here — but nothing in V1 checks. "
                               "It relies on the model obeying one instruction.")
            except LLMError as e:
                st.caption(f"V1 call failed: {e}")
        with b:
            st.subheader("V2 — decomposed + guarded")
            st.caption("Solve → hint → verify. Five techniques, deterministic guard.")
            for lvl in (1, 2, 3):
                st.markdown(f"**L{lvl}** {ss.hints[lvl][0]}")
            st.success("Every L1/L2 hint passed the leak guard before display.")
