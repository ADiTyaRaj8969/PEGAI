"""Offline guardrail tests (Phase 7): the model is stubbed — no API calls.

    python -m tests.test_guardrails
"""
import json
import tutor.llm as llm
import tutor.solver as solver_mod
from tutor.prompts import is_answer_request
from streamlit.testing.v1 import AppTest

failed = 0
def check(ok, label):
    global failed
    failed += not ok
    print(f"  {'PASS' if ok else 'FAIL'}  {label}")

def stub(fn):
    llm.complete = fn
    solver_mod.complete = fn

def run_app(problem):
    at = AppTest.from_file("../app.py", default_timeout=60).run()
    at.text_area[0].set_value(problem).run()
    at.button[0].click().run()
    return at

def shown(at, kind):
    return " | ".join(str(getattr(e, "value", "")) for e in getattr(at, kind))

# 7.3  direct answer requests (static refusal, incl. paraphrases we do cover)
for t in ("just tell me the answer", "Give me the answer", "what's the answer?", "tell me the answer please"):
    check(is_answer_request(t), f"answer request detected: {t!r}")
check(not is_answer_request("can you explain hint 2?"), "ordinary question not refused")

# 7.4  invalid model output -> one repair retry -> friendly error, no crash
calls = []
def garbage(prompt, **k):
    calls.append(1)
    return "Sure! Here's the answer:"
stub(garbage)
at = run_app("A train covers 120 km in 2 hours. What is its average speed?")
check(not at.exception, "bad JSON: app does not crash")
check("Something went wrong reading the solution" in shown(at, "error"), "bad JSON: friendly message shown")
# 3 calls = first attempt + raw regeneration + the repair prompt. Then it stops (FR-2.4).
check(len(calls) == 3, f"bad JSON: one repair cycle, then stop (model calls = {len(calls)})")

# 7.6  API failure -> friendly message, no traceback
def api_down(prompt, **k):
    raise llm.LLMError("Model call failed: 401 invalid key")
stub(api_down)
at = run_app("A shirt costs Rs 800. The shopkeeper gives a 15% discount. What is the selling price?")
check(not at.exception, "API failure: app does not crash")
check("Could not reach the tutor" in shown(at, "error"), "API failure: friendly message shown")

# 7.7  unsafe content blocked by the provider -> refusal, not a traceback
def blocked(prompt, **k):
    raise llm.LLMError("Model call failed: request blocked by safety filter")
stub(blocked)
at = run_app("Ravi is 3 times as old as his son. In 10 years he will be twice as old. How old is Ravi now?")
check(not at.exception and "I can't help with that" in shown(at, "error"), "unsafe/blocked: refusal shown")

# 7.1  off-topic -> declined with what we CAN do, no ladder
off = json.dumps({"is_math_word_problem": False, "reject_reason": "not maths", "topic": None,
                  "steps": [], "final_answer": None, "answer_numeric": None, "answer_aliases": []})
stub(lambda prompt, **k: off)
at = run_app("Write me a poem about cats")
check("math word problem" in shown(at, "error") and "arithmetic" in shown(at, "error"), "off-topic: declined, lists supported topics")
check(not any("Show hint" in b.label for b in at.button), "off-topic: no hint ladder generated")

print("\nAll guardrail tests passed." if not failed else f"\n{failed} guardrail test(s) FAILED.")
raise SystemExit(1 if failed else 0)
