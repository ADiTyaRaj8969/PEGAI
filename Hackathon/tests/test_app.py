"""Offline UI test: runs app.py headless with the model stubbed — no API calls.

    python -m tests.test_app
"""
import tutor.solver as solver_mod
import tutor.hints as hints_mod
import tutor.diagnose as diag_mod
from tutor.hints import Ladder
from tutor.solver import Solution
from tutor.diagnose import Diagnosis
from streamlit.testing.v1 import AppTest

SOL = Solution(True, "speed-distance-time",
               [{"n": 1, "action": "divide", "result": "60"}],
               "60 km/h", 60, ["60", "sixty", "60 km/h"])
OFF = Solution(False, reject_reason="not maths")
calls = {"v1": 0, "ladder": 0}


def fake_solve(p):
    return OFF if "poem" in p else SOL

def fake_ladder(p, sol):
    calls["ladder"] += 1
    return Ladder("Which relationship links distance, time and speed?",
                  "Use speed = distance divided by time; you got 60 km/h.",   # L2 leaks on purpose
                  "Divide 120 by 2.")

def fake_v1(p):
    calls["v1"] += 1
    return "Hint 1: Think about speed.\nHint 2: The answer is 60 km/h.\nHint 3: Divide."

def fake_diag(p, w, s):
    return Diagnosis("error", 1, "multiplied", "wrong op", "Check the units of km x h.")

solver_mod.solve = fake_solve
hints_mod.generate_ladder = fake_ladder
hints_mod.generate_v1 = fake_v1
diag_mod.diagnose = fake_diag
import tutor.guard as G
G.complete_json = lambda *a, **k: {"hint": "Think about distance and time."}  # regeneration stub

failed = 0
def check(ok, label):
    global failed
    failed += not ok
    print(f"  {'PASS' if ok else 'FAIL'}  {label}")

def texts(at, kind):
    return " | ".join(str(getattr(e, "value", "")) for e in getattr(at, kind))

at = AppTest.from_file("../app.py", default_timeout=30).run()
check(not at.exception, "app loads")

at.text_area[0].set_value("   ").run(); at.button[0].click().run()
check("Type a problem first" in texts(at, "warning"), "empty input rejected")

at.text_area[0].set_value("x" * 2500).run(); at.button[0].click().run()
check("too long" in texts(at, "warning"), "oversized input rejected")

at.text_area[0].set_value("Write me a poem about cats").run(); at.button[0].click().run()
check(len(at.error) >= 1 and not at.exception, "off-topic declined, no ladder")
check(not any("Show hint" in b.label for b in at.button), "no hint buttons after off-topic")

at.text_area[0].set_value("A train covers 120 km in 2 hours. What is its average speed?").run()
at.button[0].click().run()
check(any(b.label == "Show hint 2" for b in at.button), "hint 1 shown, hint 2 offered")
check(not any(b.label == "Show hint 3" for b in at.button), "hint 3 locked until hint 2")
check("HINT 2" not in " ".join(m.value for m in at.markdown), "hint 2 not rendered early")

next(b for b in at.button if b.label == "Show hint 2").click().run()
shown = " ".join(i.value for i in at.info)
check("60" not in shown, f"leaky L2 was regenerated before display -> no '60' on screen")
check(any(b.label == "Show hint 3" for b in at.button), "hint 3 offered after hint 2")

at.text_input[0].set_value("just tell me the answer").run()
check("not going to give you the answer" in texts(at, "error"), "answer request refused (static)")

at.checkbox[0].check().run()
check(calls["v1"] == 1, "V1 called once on toggle")
at.text_input[0].set_value("").run(); at.run()
check(calls["v1"] == 1, "V1 NOT re-called on later reruns")
check("V1 leaked" in texts(at, "error"), "V1 panel reports the real leak")

print("\nAll UI tests passed." if not failed else f"\n{failed} UI test(s) FAILED.")
raise SystemExit(1 if failed else 0)
