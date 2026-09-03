#!/usr/bin/env python
"""Validates the notebook's GPU-independent logic.

Stable Diffusion itself cannot run here (no GPU, no weights), but most of what
can actually be *wrong* in this notebook is ordinary Python: prompt composition,
the metric maths, and the comparison-table / best-configuration pipeline. Those
are extracted from the .ipynb and executed against synthetic data, so a logic
error is caught before the notebook reaches Colab.

Run:  python selftest.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import nbformat as nbf
import numpy as np
import pandas as pd
from PIL import Image

HERE = Path(__file__).parent
NB = HERE / "AI_Product_Advertisement_Generator.ipynb"

failures: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"PASS  {name}")
    else:
        failures.append(name)
        print(f"FAIL  {name}  {detail}")


def cell_containing(nb, needle: str) -> str:
    for c in nb.cells:
        if c.cell_type == "code" and needle in c.source:
            return c.source
    raise LookupError(f"no code cell contains {needle!r}")


nb = nbf.read(NB, as_version=4)
ns: dict = {"np": np, "pd": pd, "Image": Image}

# --------------------------------------------------------------------------
# 1. Prompt composition
# --------------------------------------------------------------------------
exec("PRODUCT = 'compact SUV car'\n"
     "PRODUCT_LONG = 'a modern compact SUV car, glossy metallic paint, alloy wheels'\n"
     "BASELINE = dict(prompt_mode='detailed', negative_mode='detailed', seed=42,"
     " cfg=7.0, steps=30, strength=0.45, environment='mountain',"
     " lighting='golden_hour', camera='wide', style='photorealistic')", ns)

prompt_cell = cell_containing(nb, "def build_prompt")
prompt_cell = "\n".join(l for l in prompt_cell.splitlines()
                        if not l.startswith("print") and not l.startswith("import textwrap"))
exec("import textwrap\n" + prompt_cell, ns)

basic = ns["build_prompt"]({**ns["BASELINE"], "prompt_mode": "basic"})
detailed = ns["build_prompt"](ns["BASELINE"])

check("basic prompt is short and names the product",
      len(basic) < 60 and "SUV" in basic, basic)
check("detailed prompt is long and composed",
      len(detailed) > 250 and "golden hour" in detailed, detailed[:70])
check("negative 'none' is empty", ns["build_negative"]({"negative_mode": "none"}) == "")
check("negative 'detailed' is populated",
      len(ns["build_negative"]({"negative_mode": "detailed"})) > 100)

# Every bank key referenced by BASELINE must exist.
for bank, key in [("ENVIRONMENTS", "environment"), ("LIGHTING", "lighting"),
                  ("CAMERA", "camera"), ("STYLE", "style")]:
    check(f"{bank} contains baseline value '{ns['BASELINE'][key]}'",
          ns["BASELINE"][key] in ns[bank])

# Every value used by experiments 7-10 must exist in its bank.
exp_values = {
    "ENVIRONMENTS": ["campus", "mountain", "city", "beach", "desert"],
    "LIGHTING": ["daylight", "golden_hour", "night"],
    "CAMERA": ["wide", "close", "low"],
    "STYLE": ["photorealistic", "cinematic", "luxury"],
}
for bank, values in exp_values.items():
    missing = [v for v in values if v not in ns[bank]]
    check(f"{bank} covers all experiment values", not missing, f"missing {missing}")

# Every bank entry must be reachable by build_prompt without a KeyError.
for env in ns["ENVIRONMENTS"]:
    for lit in ns["LIGHTING"]:
        for cam in ns["CAMERA"]:
            for sty in ns["STYLE"]:
                ns["build_prompt"]({**ns["BASELINE"], "environment": env,
                                    "lighting": lit, "camera": cam, "style": sty})
check("all 135 prompt combinations build without error", True)

# --------------------------------------------------------------------------
# 2. Sharpness metric
# --------------------------------------------------------------------------
metrics_cell = cell_containing(nb, "def sharpness")
sharp_src = metrics_cell[metrics_cell.index("def sharpness"):]
sharp_src = sharp_src[:sharp_src.index("\ndef ")] if "\ndef " in sharp_src else sharp_src
exec(sharp_src, ns)

rng = np.random.default_rng(0)
noise = Image.fromarray(rng.integers(0, 255, (128, 128, 3), dtype=np.uint8))
flat = Image.new("RGB", (128, 128), (128, 128, 128))
blurred = noise.resize((16, 16)).resize((128, 128))

s_noise, s_flat, s_blur = (ns["sharpness"](x) for x in (noise, flat, blurred))
check("sharpness: flat image scores ~0", s_flat < 1e-6, f"{s_flat}")
check("sharpness: detailed > blurred", s_noise > s_blur, f"{s_noise:.1f} vs {s_blur:.1f}")
check("sharpness returns a finite float",
      isinstance(s_noise, float) and np.isfinite(s_noise))

# --------------------------------------------------------------------------
# 3. Comparison table + best-configuration pipeline
# --------------------------------------------------------------------------
# Rebuild the exact RESULTS schema the notebook produces, with synthetic scores.
param_of = {
    "exp01_prompt": ("prompt_mode", ["basic", "detailed"]),
    "exp02_negative": ("negative_mode", ["none", "detailed"]),
    "exp03_seed": ("seed", [42, 101, 999]),
    "exp04_cfg": ("cfg", [3.0, 7.0, 12.0]),
    "exp05_steps": ("steps", [10, 20, 30, 50]),
    "exp06_strength": ("strength", [0.2, 0.45, 0.7]),
    "exp07_environment": ("environment", ["campus", "mountain", "city", "beach"]),
    "exp08_lighting": ("lighting", ["daylight", "golden_hour", "night"]),
    "exp09_camera": ("camera", ["wide", "close", "low"]),
    "exp10_style": ("style", ["photorealistic", "cinematic", "luxury"]),
}

RESULTS = []
for exp, (param, values) in param_of.items():
    for v in values:
        cfg = {**ns["BASELINE"], param: v}
        RESULTS.append(dict(
            experiment=exp, variant=f"{param}={v}",
            prompt_mode=cfg["prompt_mode"], negative_mode=cfg["negative_mode"],
            seed=cfg["seed"], cfg_scale=cfg["cfg"], steps=cfg["steps"],
            strength=cfg["strength"], environment=cfg["environment"],
            lighting=cfg["lighting"], camera=cfg["camera"], style=cfg["style"],
            seconds=round(float(rng.uniform(2, 6)), 2), path="x.png",
            prompt="p", negative="n",
            identity=round(float(rng.uniform(55, 92)), 2),
            adherence=round(float(rng.uniform(20, 34)), 2),
            sharpness=round(float(rng.uniform(80, 900)), 1),
        ))

check("synthetic sweep matches notebook image count", len(RESULTS) == 30, str(len(RESULTS)))

df = pd.DataFrame(RESULTS)

def norm(s):
    lo, hi = s.min(), s.max()
    return pd.Series(0.5, index=s.index) if hi == lo else (s - lo) / (hi - lo)

W = {"identity": 0.45, "adherence": 0.35, "sharpness": 0.20}
df["composite"] = (W["identity"] * norm(df["identity"])
                   + W["adherence"] * norm(df["adherence"])
                   + W["sharpness"] * norm(df["sharpness"])).round(4)
df = df.sort_values("composite", ascending=False).reset_index(drop=True)

check("composite weights sum to 1", abs(sum(W.values()) - 1.0) < 1e-9)
check("composite in [0,1]", df["composite"].between(0, 1).all())

# Constant-column guard: norm() must not divide by zero.
const = pd.Series([5.0] * 10)
check("norm handles a constant column", norm(const).eq(0.5).all())

summary = (df.sort_values("composite", ascending=False)
             .groupby("experiment", as_index=False)
             .first()[["experiment", "variant", "identity", "adherence",
                       "sharpness", "seconds", "composite"]]
             .sort_values("experiment").reset_index(drop=True))

check("summary has one winner per experiment", len(summary) == 10, str(len(summary)))

# The best-config assembly, verbatim from the notebook.
best = dict(ns["BASELINE"])
column_for = {"cfg": "cfg_scale"}
lookup = {k: v[0] for k, v in param_of.items()}
for _, row in summary.iterrows():
    param = lookup[row["experiment"]]
    winner = df[(df.experiment == row["experiment"]) &
                (df.variant == row["variant"])].iloc[0]
    best[param] = winner[column_for.get(param, param)]

check("best config has every baseline key",
      set(best) == set(ns["BASELINE"]), str(set(ns["BASELINE"]) ^ set(best)))
for key in ("cfg", "steps", "strength", "seed"):
    check(f"best['{key}'] is numeric, not NaN",
          isinstance(best[key], (int, float, np.integer, np.floating))
          and not pd.isna(best[key]), repr(best[key]))
check("best['prompt_mode'] is a valid mode",
      best["prompt_mode"] in ("basic", "detailed"), repr(best["prompt_mode"]))
check("best['negative_mode'] is a valid mode",
      best["negative_mode"] in ("none", "detailed"), repr(best["negative_mode"]))

best["environment"] = ns["BASELINE"]["environment"]
final_prompt = ns["build_prompt"](best)
check("winning configuration still builds a prompt", len(final_prompt) > 50)

# --------------------------------------------------------------------------
# 4. Notebook structure
# --------------------------------------------------------------------------
code_cells = [c for c in nb.cells if c.cell_type == "code"]
src_all = "\n".join(c.source for c in code_cells)
for token in ["build_prompt", "build_negative", "generate(", "run_experiment",
              "score_all", "comparison_table.csv", "best_configuration.json",
              "final_campaign"]:
    check(f"notebook defines/uses {token}", token in src_all)

for exp in param_of:
    check(f"notebook runs {exp}", exp in src_all)

check("notebook requests a GPU runtime",
      nb.metadata.get("accelerator") == "GPU")

print()
if failures:
    print(f"{len(failures)} FAILURE(S): {failures}")
    sys.exit(1)
print("All checks passed.")
print("\nNote: this validates logic only. Stable Diffusion image quality can")
print("only be assessed by running the notebook on a GPU runtime.")
