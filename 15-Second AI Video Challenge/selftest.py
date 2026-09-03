#!/usr/bin/env python
"""Validates the notebook's GPU-independent logic.

The video model cannot run here, but the parts that can actually be wrong are
ordinary Python: the frame arithmetic that has to land on exactly 15 seconds,
the cross-dissolve blending, and the prompt composition. Those are extracted
from the .ipynb and tested against synthetic frames.

Run:  python selftest.py
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

import nbformat as nbf
import numpy as np

NB = Path(__file__).parent / "Marwadi_2050_Video.ipynb"
failures: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"PASS  {name}")
    else:
        failures.append(name)
        print(f"FAIL  {name}  {detail}")


nb = nbf.read(NB, as_version=4)


def cell_with(needle: str) -> str:
    for c in nb.cells:
        if c.cell_type == "code" and needle in c.source:
            return c.source
    raise LookupError(needle)


# ---------------------------------------------------------------- config
cfg_src = cell_with("TARGET_FRAMES")
ns: dict = {"math": math}
for line in cfg_src.splitlines():
    s = line.strip()
    if re.match(r"^(FPS|DURATION_S|N_SHOTS|TARGET_FRAMES|XFADE|JOINS|FRAMES_CLIP|WIDTH, HEIGHT)\s*=", s):
        exec(s, ns)

check("target is 120 frames", ns["TARGET_FRAMES"] == 120, str(ns.get("TARGET_FRAMES")))
check("15 seconds at 8 fps", ns["TARGET_FRAMES"] / ns["FPS"] == 15.0)
check("five shots", ns["N_SHOTS"] == 5)
check("joins = shots - 1", ns["JOINS"] == ns["N_SHOTS"] - 1)
check("frames/clip derived, not hard-coded",
      ns["FRAMES_CLIP"] == math.ceil((ns["TARGET_FRAMES"] + ns["JOINS"] * ns["XFADE"]) / ns["N_SHOTS"]),
      str(ns["FRAMES_CLIP"]))
check("default XFADE gives exactly 24 frames/clip",
      ns["XFADE"] != 0 or ns["FRAMES_CLIP"] == 24, str(ns["FRAMES_CLIP"]))

# ------------------------------------------------------------ crossfade
src = cell_with("def crossfade_concat")
fn = src[src.index("def crossfade_concat"):]
fn = fn[:fn.index("\njoined =")] if "\njoined =" in fn else fn
exec("import numpy as np\n" + fn, ns)
crossfade_concat = ns["crossfade_concat"]


def fake(n, value):
    return [np.full((8, 8, 3), value, dtype=np.uint8) for _ in range(n)]


# The core arithmetic: for every XFADE, enough footage must survive the join.
for xf in (0, 2, 4, 6, 8):
    fpc = math.ceil((120 + 4 * xf) / 5)
    clips = [fake(fpc, 20 * (i + 1)) for i in range(5)]
    joined = crossfade_concat(clips, xfade=xf)
    expected = 5 * fpc - 4 * xf
    check(f"XFADE={xf}: concat length is 5*{fpc}-4*{xf}={expected}",
          len(joined) == expected, str(len(joined)))
    check(f"XFADE={xf}: >=120 frames survive for the trim",
          len(joined) >= 120, str(len(joined)))
    check(f"XFADE={xf}: trimmed video is exactly 15.00 s",
          len(joined[:120]) / 8 == 15.0)

# Blending behaviour
clips = [fake(24, 0), fake(24, 200)]
hard = crossfade_concat(clips, xfade=0)
check("hard cut adds no frames", len(hard) == 48, str(len(hard)))
check("hard cut keeps original values",
      hard[23].max() == 0 and hard[24].min() == 200)

soft = crossfade_concat(clips, xfade=6)
check("crossfade consumes frames", len(soft) == 42, str(len(soft)))
mid = [f[0, 0, 0] for f in soft[18:24]]
check("crossfade ramps monotonically 0->200",
      all(a < b for a, b in zip(mid, mid[1:])) and 0 < mid[0] and mid[-1] < 200,
      str(mid))
check("crossfade output stays uint8", soft[20].dtype == np.uint8)

check("single clip passes through unchanged",
      len(crossfade_concat([fake(24, 5)], xfade=6)) == 24)

# ------------------------------------------------------------- prompts
psrc = cell_with("STORYBOARD = [")
exec(psrc[:psrc.index("for s in STORYBOARD")], ns)
STORYBOARD, build_prompt = ns["STORYBOARD"], ns["build_prompt"]

check("five shots storyboarded", len(STORYBOARD) == 5, str(len(STORYBOARD)))
check("shots numbered 1-5", [s["n"] for s in STORYBOARD] == [1, 2, 3, 4, 5])
check("every shot has a distinct beat",
      len({s["beat"] for s in STORYBOARD}) == 5)

for s in STORYBOARD:
    p = build_prompt(s)
    check(f"shot {s['n']} prompt has all six dimensions",
          all(part in p for part in (s["subject"], s["environment"],
                                     s["camera"], s["lighting"],
                                     ns["STYLE"], ns["QUALITY"])))
    check(f"shot {s['n']} carries the continuity anchor",
          ns["CONTINUITY"] in p)
    check(f"shot {s['n']} directs camera movement",
          re.search(r"\b(push|track|dolly|orbit|crane|pan|tilt|steadicam|descend|rising)\w*\b",
                    s["camera"], re.I) is not None, s["camera"])

check("camera movements are all different",
      len({s["camera"] for s in STORYBOARD}) == 5)
check("negative prompt blocks watermarks and text",
      all(w in ns["NEGATIVE"] for w in ("watermark", "text", "logo")))
check("negative prompt blocks static output", "static frame" in ns["NEGATIVE"])

# ------------------------------------------------------------ structure
all_src = "\n".join(c.source for c in nb.cells if c.cell_type == "code")
for token in ("zeroscope", "crossfade_concat", "marwadi_2050_15s.mp4",
              "video_manifest.json", "mimsave", "storyboard_contact_sheet"):
    check(f"notebook uses {token}", token in all_src)
check("notebook requests a GPU runtime", nb.metadata.get("accelerator") == "GPU")
check("duration is asserted in the notebook", "14.0 <= duration <= 16.0" in all_src)

print()
if failures:
    print(f"{len(failures)} FAILURE(S): {failures}")
    sys.exit(1)
print("All checks passed.")
print("\nNote: logic only. Video quality can only be judged by running the")
print("notebook on a GPU runtime.")
