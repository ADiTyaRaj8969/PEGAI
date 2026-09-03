#!/usr/bin/env python
"""Generates AI_Product_Advertisement_Generator.ipynb.

The notebook is built here rather than hand-written as JSON so that every code
cell can be syntax-checked before it ships. Run:

    python build_notebook.py

Then upload the produced .ipynb to Google Colab and run it on a T4 GPU runtime.
"""

from __future__ import annotations

import sys
from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).parent
OUT = HERE / "AI_Product_Advertisement_Generator.ipynb"

cells: list = []


def md(text: str) -> None:
    cells.append(nbf.v4.new_markdown_cell(text.strip("\n")))


def code(text: str) -> None:
    cells.append(nbf.v4.new_code_cell(text.strip("\n")))


# ===========================================================================
md(r"""
# AI Product Advertisement Generator
### Image Generation using Stable Diffusion — Assignment 3

**Aditya Raj** · Enrollment No. 92301733062 · ICT · Batch 7EK1'A'
*Prompt Engineering for Generative AI*

---

## Objective

Build a system using Stable Diffusion that generates multiple professional
advertisements for **the same product** under different environments, lighting,
camera angles and styles — while preserving the product's visual identity.

**Product chosen:** compact SUV car (following the brief's Kia Seltos example).

## Workflow

```
Reference Product Image
        ↓
Stable Diffusion Image-to-Image
        ↓
Change Environment  →  Change Camera  →  Change Lighting  →  Change Style
        ↓
Generate Advertisement
        ↓
Compare Results
```

## Deliverables checklist

| # | Deliverable | Where |
|---|---|---|
| 1 | Original reference image | §3 |
| 2 | Prompts used | §4 |
| 3 | Negative prompts | §4 |
| 4 | Parameter values | §5, §7 |
| 5 | Generated images | §7 (all 10 experiments) |
| 6 | Comparison table | §8 |
| 7 | Best prompt + best parameter combination | §9 |

## How results are compared

Rather than judging the images by eye alone, every generated image is scored on
three measurable axes, so the "best combination" in §9 is derived from data:

- **Identity similarity** — CLIP image-image cosine between the generated ad and
  the reference product. This directly measures the brief's requirement to
  *maintain the visual identity of the vehicle*.
- **Prompt adherence (CLIPScore)** — CLIP image-text cosine between the image
  and its prompt. Measures whether the requested scene was actually produced.
- **Sharpness** — variance of the Laplacian, a standard no-reference proxy for
  detail and focus.

A subjective column is included as well, because these metrics do not capture
whether an image looks like a *good advertisement*.

> **Runtime:** Colab → Runtime → Change runtime type → **T4 GPU**. The full
> 10-experiment sweep is ~30 images and takes roughly 3–5 minutes on a T4.
""")

# ---------------------------------------------------------------------------
md("## 1. Setup")

code(r"""
# Colab has torch preinstalled. This pins the diffusion stack only.
!pip -q install "diffusers>=0.31.0" "transformers>=4.44.0" accelerate safetensors --upgrade
print("Install complete — if Colab asks you to restart the runtime, do it and re-run from here.")
""")

code(r"""
import gc, json, math, os, textwrap, time
from dataclasses import dataclass, field, asdict
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt
from PIL import Image

import diffusers, transformers

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DTYPE  = torch.float16 if DEVICE == "cuda" else torch.float32

print(f"torch        {torch.__version__}")
print(f"diffusers    {diffusers.__version__}")
print(f"transformers {transformers.__version__}")
print(f"device       {DEVICE}")
if DEVICE == "cuda":
    print(f"gpu          {torch.cuda.get_device_name(0)}")
else:
    print("\n!! No GPU detected. Runtime -> Change runtime type -> T4 GPU.")
    print("   The notebook will run on CPU but each image may take several minutes.")
""")

# ---------------------------------------------------------------------------
md("""
## 2. Configuration

Every experiment varies **one** parameter away from this baseline, which is the
standard way to isolate a parameter's effect. The baseline values are the
mid-range options from the assignment's parameter table.
""")

code(r"""
OUT_DIR = Path("ad_outputs"); OUT_DIR.mkdir(exist_ok=True)

# Default model. SD 1.5 is used for reliability on a free T4.
# To switch to SDXL, set USE_SDXL = True (slower, ~1024px, more VRAM).
USE_SDXL = False

SD15_CANDIDATES = [
    "stable-diffusion-v1-5/stable-diffusion-v1-5",   # canonical re-upload
    "runwayml/stable-diffusion-v1-5",                # original (may be gated)
    "Lykon/dreamshaper-8",                           # SD1.5 finetune fallback
]
SDXL_CANDIDATES = ["stabilityai/stable-diffusion-xl-base-1.0"]

IMG_SIZE = 1024 if USE_SDXL else 512

# --- The product -----------------------------------------------------------
PRODUCT      = "compact SUV car"
PRODUCT_LONG = "a modern compact SUV car, glossy metallic paint, alloy wheels"

# --- Baseline configuration (one parameter is varied per experiment) --------
BASELINE = dict(
    prompt_mode   = "detailed",      # basic | detailed
    negative_mode = "detailed",      # none  | detailed
    seed          = 42,
    cfg           = 7.0,
    steps         = 30,
    strength      = 0.45,
    environment   = "mountain",
    lighting      = "golden_hour",
    camera        = "wide",
    style         = "photorealistic",
)

print(f"Model family : {'SDXL' if USE_SDXL else 'SD 1.5'}   |   resolution {IMG_SIZE}px")
print("Baseline configuration:")
for k, v in BASELINE.items():
    print(f"  {k:<14} {v}")
""")

# ---------------------------------------------------------------------------
md("""
### 2.1 Load the pipelines

One set of weights is loaded and shared between the text-to-image pipeline (used
once, to create the reference product photo) and the image-to-image pipeline
(used for every advertisement). Sharing components via `from_pipe` avoids
holding two copies of the model in VRAM.
""")

code(r"""
from diffusers import (AutoPipelineForImage2Image, AutoPipelineForText2Image,
                       DPMSolverMultistepScheduler)

def load_pipelines(candidates):
    '''Try each candidate repo in turn so a moved/gated model is not fatal.'''
    last_error = None
    for model_id in candidates:
        try:
            print(f"Loading {model_id} ...")
            kwargs = dict(torch_dtype=DTYPE, use_safetensors=True)
            if not USE_SDXL:
                kwargs.update(safety_checker=None, requires_safety_checker=False)
            i2i = AutoPipelineForImage2Image.from_pretrained(model_id, **kwargs)
            i2i = i2i.to(DEVICE)
            # DPM-Solver++ gives good quality at low step counts, which matters
            # for the inference-steps experiment.
            i2i.scheduler = DPMSolverMultistepScheduler.from_config(
                i2i.scheduler.config, algorithm_type="dpmsolver++", use_karras_sigmas=True)
            i2i.set_progress_bar_config(disable=True)

            t2i = AutoPipelineForText2Image.from_pipe(i2i)
            t2i.set_progress_bar_config(disable=True)

            if DEVICE == "cuda":
                i2i.enable_attention_slicing()
                t2i.enable_attention_slicing()
            print(f"Loaded {model_id}")
            return i2i, t2i, model_id
        except Exception as exc:
            print(f"  failed: {type(exc).__name__}: {str(exc)[:160]}")
            last_error = exc
    raise RuntimeError(f"No model could be loaded. Last error: {last_error}")

pipe_i2i, pipe_t2i, MODEL_ID = load_pipelines(SDXL_CANDIDATES if USE_SDXL else SD15_CANDIDATES)
""")

# ---------------------------------------------------------------------------
md("""
## 3. Reference product image  *(Deliverable 1)*

The reference is generated once with text-to-image at a fixed seed, so the whole
notebook is reproducible without any external file. Every advertisement in §7 is
an **image-to-image** transformation of this single reference, which is what
makes identity preservation measurable.

To use your own product photo instead, run the upload cell and skip the
generation cell.
""")

code(r"""
# --- OPTION A: upload your own reference photo (skip if generating one) -----
# Uncomment the three lines below to upload.

# from google.colab import files
# uploaded = files.upload()
# REFERENCE = Image.open(next(iter(uploaded))).convert("RGB").resize((IMG_SIZE, IMG_SIZE))

REFERENCE = None   # left as None so OPTION B runs
print("Upload cell skipped — the next cell will generate the reference image.")
""")

code(r"""
# --- OPTION B: generate a clean studio reference shot ------------------------
REFERENCE_PROMPT = (
    f"professional studio product photograph of {PRODUCT_LONG}, "
    "three-quarter front view, centered, plain light grey seamless backdrop, "
    "even softbox studio lighting, sharp focus, high detail, commercial "
    "automotive photography, 50mm lens"
)
REFERENCE_NEGATIVE = (
    "blurry, low quality, distorted, deformed, extra wheels, missing wheels, "
    "text, watermark, logo, signature, people, cluttered background, cartoon"
)
REFERENCE_SEED = 7

if REFERENCE is None:
    g = torch.Generator(device=DEVICE).manual_seed(REFERENCE_SEED)
    REFERENCE = pipe_t2i(
        prompt=REFERENCE_PROMPT,
        negative_prompt=REFERENCE_NEGATIVE,
        num_inference_steps=40,
        guidance_scale=7.5,
        width=IMG_SIZE, height=IMG_SIZE,
        generator=g,
    ).images[0]

REFERENCE.save(OUT_DIR / "00_reference.png")

plt.figure(figsize=(5.5, 5.5))
plt.imshow(REFERENCE); plt.axis("off")
plt.title("Deliverable 1 — Reference product image", fontsize=11)
plt.tight_layout(); plt.show()
print(f"Reference seed {REFERENCE_SEED} · saved to {OUT_DIR/'00_reference.png'}")
""")

# ---------------------------------------------------------------------------
md("""
## 4. Prompts and negative prompts  *(Deliverables 2 and 3)*

The prompt is composed from four interchangeable banks — environment, lighting,
camera and style — so each experiment can swap exactly one component. The
**basic** prompt mode exists purely as the control for Experiment 1.
""")

code(r"""
ENVIRONMENTS = {
    "campus":   "parked on a university campus driveway, modern academic buildings, "
                "tree-lined path, students walking in the background",
    "mountain": "on a winding mountain road, snow-capped peaks in the distance, "
                "alpine valley, pine forest",
    "city":     "on a downtown city street, glass skyscrapers, urban crosswalk, "
                "reflections in shop windows",
    "beach":    "on a coastal road beside a sandy beach, ocean waves, palm trees, "
                "clear horizon",
    "desert":   "on an empty desert highway, red rock formations, sand dunes, "
                "vast open sky",
}

LIGHTING = {
    "daylight":    "bright natural daylight, clear blue sky, crisp soft shadows",
    "golden_hour": "golden hour sunlight, warm rim lighting, long dramatic shadows, "
                   "sun flare",
    "night":       "night scene, headlights on, neon signs reflecting on wet asphalt, "
                   "moody blue ambient light",
}

CAMERA = {
    "wide":  "wide-angle establishing shot, 24mm lens, entire vehicle in frame, "
             "expansive environment",
    "close": "close-up three-quarter detail shot, 85mm lens, shallow depth of field, "
             "bokeh background",
    "low":   "dramatic low-angle hero shot, 35mm lens, camera near ground level, "
             "vehicle towering over the viewer",
}

STYLE = {
    "photorealistic": "photorealistic commercial automotive photography, ultra sharp "
                      "focus, high dynamic range, natural colour",
    "cinematic":      "cinematic film still, anamorphic lens flare, teal and orange "
                      "colour grade, dramatic atmosphere, film grain",
    "luxury":         "luxury advertising aesthetic, glossy mirror reflections, "
                      "premium magazine editorial, elegant minimal composition",
}

NEGATIVE_PROMPTS = {
    "none": "",
    "detailed": (
        "blurry, low quality, low resolution, distorted, deformed, warped body panels, "
        "extra wheels, missing wheels, melted shapes, text, watermark, logo, signature, "
        "cartoon, anime, illustration, painting, sketch, oversaturated, jpeg artifacts, "
        "bad proportions, duplicate, cropped, out of frame, ugly"
    ),
}

QUALITY_TAGS = "professional advertisement, award-winning product photography, 8k, highly detailed"


def build_prompt(cfg: dict) -> str:
    '''Compose the positive prompt from the configuration.'''
    if cfg["prompt_mode"] == "basic":
        # The control: subject + environment only, no craft direction.
        return f"a {PRODUCT} in a {cfg['environment']} setting"
    return ", ".join([
        f"professional advertisement photograph of {PRODUCT_LONG}",
        ENVIRONMENTS[cfg["environment"]],
        LIGHTING[cfg["lighting"]],
        CAMERA[cfg["camera"]],
        STYLE[cfg["style"]],
        QUALITY_TAGS,
    ])


def build_negative(cfg: dict) -> str:
    return NEGATIVE_PROMPTS[cfg["negative_mode"]]


print("BASIC prompt example:\n ", build_prompt({**BASELINE, "prompt_mode": "basic"}))
print("\nDETAILED prompt example:")
print(textwrap.fill(build_prompt(BASELINE), 88, initial_indent="  ", subsequent_indent="  "))
print("\nDETAILED negative prompt:")
print(textwrap.fill(NEGATIVE_PROMPTS["detailed"], 88, initial_indent="  ", subsequent_indent="  "))
""")

md("""
> **Note on prompt length.** Stable Diffusion's CLIP text encoder accepts 77
> tokens. The detailed prompt exceeds this, so its tail is truncated by the
> pipeline. This is worth knowing when reading Experiment 1: a longer prompt is
> not automatically a more effective one, because the final clauses may never
> reach the model. The ordering above puts subject and environment first
> deliberately.
""")

# ---------------------------------------------------------------------------
md("""
## 5. Generation engine  *(Deliverable 4 — parameter values)*

A single function performs every generation, so all 10 experiments differ only
in the configuration passed to it. Each call records its parameters, wall-clock
time and output path.
""")

code(r"""
RESULTS: list[dict] = []

def generate(cfg: dict, experiment: str, variant: str, save: bool = True) -> Image.Image:
    '''Run one img2img generation and record it in RESULTS.'''
    prompt   = build_prompt(cfg)
    negative = build_negative(cfg)
    gen      = torch.Generator(device=DEVICE).manual_seed(int(cfg["seed"]))

    t0 = time.time()
    image = pipe_i2i(
        prompt=prompt,
        negative_prompt=negative or None,
        image=REFERENCE,
        strength=float(cfg["strength"]),
        guidance_scale=float(cfg["cfg"]),
        num_inference_steps=int(cfg["steps"]),
        generator=gen,
    ).images[0]
    elapsed = time.time() - t0

    path = ""
    if save:
        safe = f"{experiment}__{variant}".replace(" ", "_").replace("/", "-")
        path = str(OUT_DIR / f"{safe}.png")
        image.save(path)

    RESULTS.append(dict(
        experiment=experiment, variant=variant,
        prompt_mode=cfg["prompt_mode"], negative_mode=cfg["negative_mode"],
        seed=cfg["seed"], cfg_scale=cfg["cfg"], steps=cfg["steps"],
        strength=cfg["strength"], environment=cfg["environment"],
        lighting=cfg["lighting"], camera=cfg["camera"], style=cfg["style"],
        seconds=round(elapsed, 2), path=path, prompt=prompt, negative=negative,
        image=image,
    ))
    return image


def run_experiment(experiment: str, param: str, values: list, labeller=None) -> list:
    '''Vary one parameter away from BASELINE and generate one image per value.'''
    images, labels = [], []
    for v in values:
        cfg = {**BASELINE, param: v}
        label = labeller(v) if labeller else f"{param}={v}"
        images.append(generate(cfg, experiment, label))
        labels.append(label)
    return images, labels


def show(images, labels, title, cols=None, size=3.4):
    cols = cols or len(images)
    rows = math.ceil(len(images) / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(size * cols, size * rows + 0.6))
    axes = np.atleast_1d(axes).ravel()
    for ax, img, lab in zip(axes, images, labels):
        ax.imshow(img); ax.axis("off")
        ax.set_title(textwrap.fill(str(lab), 26), fontsize=9)
    for ax in axes[len(images):]:
        ax.axis("off")
    fig.suptitle(title, fontsize=12, y=1.0)
    fig.tight_layout(); plt.show()

print("Generation engine ready.")
""")

# ---------------------------------------------------------------------------
md("""
## 6. Scoring metrics

CLIP supplies both metrics that matter here. Identity similarity compares the
generated advertisement against the reference product; prompt adherence compares
it against its own prompt. Sharpness is computed directly from pixels.
""")

code(r"""
from transformers import CLIPModel, CLIPProcessor

CLIP_ID = "openai/clip-vit-base-patch32"
clip_model = CLIPModel.from_pretrained(CLIP_ID).to(DEVICE).eval()
clip_proc  = CLIPProcessor.from_pretrained(CLIP_ID)

@torch.no_grad()
def _img_emb(img):
    x = clip_proc(images=img, return_tensors="pt").to(DEVICE)
    return F.normalize(clip_model.get_image_features(**x), dim=-1)

@torch.no_grad()
def _txt_emb(text):
    x = clip_proc(text=[text], return_tensors="pt", padding=True,
                  truncation=True, max_length=77).to(DEVICE)
    return F.normalize(clip_model.get_text_features(**x), dim=-1)

REF_EMB = _img_emb(REFERENCE)

def identity_similarity(img) -> float:
    '''CLIP image-image cosine vs the reference. Higher = identity preserved.'''
    return float((_img_emb(img) @ REF_EMB.T).item()) * 100

def clip_score(img, text) -> float:
    '''CLIP image-text cosine. Higher = the prompt was followed.'''
    return float((_img_emb(img) @ _txt_emb(text).T).item()) * 100

def sharpness(img) -> float:
    '''Variance of the Laplacian - a no-reference focus/detail proxy.'''
    g = np.asarray(img.convert("L"), dtype=np.float32)
    lap = (g[:-2, 1:-1] + g[2:, 1:-1] + g[1:-1, :-2] + g[1:-1, 2:]
           - 4.0 * g[1:-1, 1:-1])
    return float(lap.var())

def score_all():
    '''Fill in metrics for any RESULTS row that does not have them yet.'''
    for r in RESULTS:
        if "identity" in r:
            continue
        r["identity"]  = round(identity_similarity(r["image"]), 2)
        r["adherence"] = round(clip_score(r["image"], r["prompt"]), 2)
        r["sharpness"] = round(sharpness(r["image"]), 1)

print(f"CLIP loaded ({CLIP_ID}). Metrics ready.")
""")

# ---------------------------------------------------------------------------
md("""
## 7. The ten experiments  *(Deliverable 5 — generated images)*

Each experiment changes exactly one parameter from the baseline. Values are
taken from the assignment's parameter table.
""")

experiments = [
    ("### Experiment 1 — Prompt: basic vs detailed\n\nThe control for the entire study: does prompt craft matter at all?",
     r"""
imgs, labs = run_experiment("exp01_prompt", "prompt_mode", ["basic", "detailed"],
                            labeller=lambda v: f"prompt = {v}")
show(imgs, labs, "Experiment 1 — Basic vs Detailed prompt")
"""),
    ("### Experiment 2 — Negative prompt: none vs detailed",
     r"""
imgs, labs = run_experiment("exp02_negative", "negative_mode", ["none", "detailed"],
                            labeller=lambda v: f"negative = {v}")
show(imgs, labs, "Experiment 2 — No negative prompt vs detailed negative prompt")
"""),
    ("### Experiment 3 — Seed: 42, 101, 999\n\nSeed controls the initial noise. Everything else is held constant, so any difference here is pure sampling variance — useful for judging how much of a quality difference elsewhere is real.",
     r"""
imgs, labs = run_experiment("exp03_seed", "seed", [42, 101, 999],
                            labeller=lambda v: f"seed = {v}")
show(imgs, labs, "Experiment 3 — Seed variation")
"""),
    ("### Experiment 4 — CFG scale: 3, 7, 12\n\nClassifier-free guidance controls how strictly the model follows the prompt. Low values drift; high values over-saturate and can distort geometry.",
     r"""
imgs, labs = run_experiment("exp04_cfg", "cfg", [3.0, 7.0, 12.0],
                            labeller=lambda v: f"CFG = {v}")
show(imgs, labs, "Experiment 4 — CFG scale")
"""),
    ("### Experiment 5 — Inference steps: 10, 20, 30, 50\n\nWith the DPM-Solver++ scheduler, quality typically saturates well before 50 steps. This experiment finds where the returns stop.",
     r"""
imgs, labs = run_experiment("exp05_steps", "steps", [10, 20, 30, 50],
                            labeller=lambda v: f"{v} steps")
show(imgs, labs, "Experiment 5 — Inference steps")
"""),
    ("### Experiment 6 — Image-to-image strength: 0.2, 0.45, 0.7\n\n**The most important parameter in this assignment.** Strength sets how much of the reference is destroyed. Low values keep the car but ignore the new environment; high values build a convincing scene but lose the product's identity.",
     r"""
imgs, labs = run_experiment("exp06_strength", "strength", [0.2, 0.45, 0.7],
                            labeller=lambda v: f"strength = {v}")
show(imgs, labs, "Experiment 6 — Image-to-image strength")
"""),
    ("### Experiment 7 — Environment: campus, mountain, city, beach",
     r"""
imgs, labs = run_experiment("exp07_environment", "environment",
                            ["campus", "mountain", "city", "beach"],
                            labeller=lambda v: v.title())
show(imgs, labs, "Experiment 7 — Environment", cols=4)
"""),
    ("### Experiment 8 — Lighting: daylight, golden hour, night",
     r"""
imgs, labs = run_experiment("exp08_lighting", "lighting",
                            ["daylight", "golden_hour", "night"],
                            labeller=lambda v: v.replace("_", " ").title())
show(imgs, labs, "Experiment 8 — Lighting")
"""),
    ("### Experiment 9 — Camera: wide-angle, close-up, low-angle",
     r"""
imgs, labs = run_experiment("exp09_camera", "camera", ["wide", "close", "low"],
                            labeller=lambda v: {"wide": "Wide-angle",
                                                "close": "Close-up",
                                                "low": "Low-angle"}[v])
show(imgs, labs, "Experiment 9 — Camera angle")
"""),
    ("### Experiment 10 — Style: photorealistic, cinematic, luxury",
     r"""
imgs, labs = run_experiment("exp10_style", "style",
                            ["photorealistic", "cinematic", "luxury"],
                            labeller=lambda v: v.title())
show(imgs, labs, "Experiment 10 — Style")
score_all()
print(f"\nAll experiments complete — {len(RESULTS)} images generated.")
"""),
]

for heading, body in experiments:
    md(heading)
    code(body)

# ---------------------------------------------------------------------------
md("""
## 8. Comparison table  *(Deliverable 6)*

Every generated image with its parameters and scores. The composite score
weights identity preservation highest, because the brief's requirement is to
generate varied advertisements **while maintaining the visual identity of the
product** — an image that looks superb but no longer shows the same car has
failed the task.

```
composite = 0.45 · identity + 0.35 · adherence + 0.20 · sharpness
```

Each metric is min-max normalised across all generated images first, so the
three axes are on a common scale.
""")

code(r"""
score_all()
df = pd.DataFrame([{k: v for k, v in r.items() if k != "image"} for r in RESULTS])

def norm(s):
    lo, hi = s.min(), s.max()
    return pd.Series(0.5, index=s.index) if hi == lo else (s - lo) / (hi - lo)

W = {"identity": 0.45, "adherence": 0.35, "sharpness": 0.20}
df["composite"] = (W["identity"]  * norm(df["identity"])
                 + W["adherence"] * norm(df["adherence"])
                 + W["sharpness"] * norm(df["sharpness"])).round(4)

df["manual_score_1_5"] = ""   # fill in by eye before submitting
df = df.sort_values("composite", ascending=False).reset_index(drop=True)

cols = ["experiment", "variant", "seed", "cfg_scale", "steps", "strength",
        "environment", "lighting", "camera", "style",
        "identity", "adherence", "sharpness", "seconds", "composite"]
df[cols].to_csv(OUT_DIR / "comparison_table.csv", index=False)

pd.set_option("display.width", 200, "display.max_columns", 40)
print(f"{len(df)} images · full table saved to {OUT_DIR/'comparison_table.csv'}\n")
df[cols].head(15)
""")

code(r"""
# Per-experiment winners — which value of each parameter scored best
summary = (df.sort_values("composite", ascending=False)
             .groupby("experiment", as_index=False)
             .first()[["experiment", "variant", "identity", "adherence",
                       "sharpness", "seconds", "composite"]]
             .sort_values("experiment")
             .reset_index(drop=True))
summary.to_csv(OUT_DIR / "experiment_winners.csv", index=False)
print("Best-scoring variant within each experiment:\n")
summary
""")

code(r"""
# Visualise the two trade-offs that matter most in this assignment
fig, axes = plt.subplots(1, 2, figsize=(13, 4.4))

s = df[df.experiment == "exp06_strength"].sort_values("strength")
axes[0].plot(s["strength"], s["identity"], "o-", label="Identity vs reference", color="#2a78d6")
axes[0].plot(s["strength"], s["adherence"], "s-", label="Prompt adherence", color="#eb6834")
axes[0].set_xlabel("img2img strength"); axes[0].set_ylabel("CLIP score")
axes[0].set_title("The core trade-off: identity vs scene control")
axes[0].legend(frameon=False); axes[0].grid(alpha=.3)

st = df[df.experiment == "exp05_steps"].sort_values("steps")
axes[1].plot(st["steps"], st["composite"], "o-", color="#1baf7a")
ax2 = axes[1].twiny(); ax2.set_xticks([])
axes[1].set_xlabel("inference steps"); axes[1].set_ylabel("composite score")
axes[1].set_title("Diminishing returns from more steps")
axes[1].grid(alpha=.3)

for ax in axes: ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(OUT_DIR / "tradeoff_plots.png", dpi=150); plt.show()
""")

# ---------------------------------------------------------------------------
md("""
## 9. Best prompt and best parameter combination  *(Deliverable 7)*

The experiments vary one parameter at a time, so taking the winner of each and
combining them is a **greedy coordinate search**, not an exhaustive grid search.
It is a reasonable and cheap heuristic, but it can miss interactions between
parameters — worth stating rather than glossing over.

The cell below assembles that combination, then re-renders the full advertising
campaign across all five environments from the brief's example.
""")

code(r"""
best = dict(BASELINE)
param_of = {
    "exp01_prompt": "prompt_mode", "exp02_negative": "negative_mode",
    "exp03_seed": "seed", "exp04_cfg": "cfg", "exp05_steps": "steps",
    "exp06_strength": "strength", "exp07_environment": "environment",
    "exp08_lighting": "lighting", "exp09_camera": "camera", "exp10_style": "style",
}
for _, row in summary.iterrows():
    param = param_of[row["experiment"]]
    winner = df[(df.experiment == row["experiment"]) &
                (df.variant == row["variant"])].iloc[0]
    best[param] = winner[{"cfg": "cfg_scale"}.get(param, param)]

# Environment is swept separately in the final campaign, so keep the baseline.
best["environment"] = BASELINE["environment"]

print("BEST PARAMETER COMBINATION (greedy per-experiment winners)\n")
for k, v in best.items():
    marker = "  <- changed" if v != BASELINE[k] else ""
    print(f"  {k:<14} {v}{marker}")

print("\nBEST PROMPT\n")
print(textwrap.fill(build_prompt(best), 88, initial_indent="  ", subsequent_indent="  "))
print("\nNEGATIVE PROMPT\n")
print(textwrap.fill(build_negative(best) or "(none)", 88,
                    initial_indent="  ", subsequent_indent="  "))

json.dump({"best_config": {k: (float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v)
                           for k, v in best.items()},
           "best_prompt": build_prompt(best),
           "negative_prompt": build_negative(best),
           "model": MODEL_ID},
          open(OUT_DIR / "best_configuration.json", "w"), indent=2)
""")

code(r"""
# Final campaign: the winning configuration across all five environments
campaign_imgs, campaign_labels = [], []
for env in ["mountain", "campus", "city", "beach", "desert"]:
    cfg = {**best, "environment": env}
    campaign_imgs.append(generate(cfg, "final_campaign", env))
    campaign_labels.append(env.title())

show(campaign_imgs, campaign_labels,
     "FINAL ADVERTISEMENT CAMPAIGN — one product, five environments, best parameters",
     cols=5, size=3.2)

# Contact sheet including the reference, for the submission
sheet = Image.new("RGB", (IMG_SIZE * 6, IMG_SIZE), "white")
sheet.paste(REFERENCE, (0, 0))
for i, im in enumerate(campaign_imgs, start=1):
    sheet.paste(im, (IMG_SIZE * i, 0))
sheet.save(OUT_DIR / "final_campaign_contact_sheet.png")

score_all()
final = pd.DataFrame([{k: v for k, v in r.items() if k != "image"}
                      for r in RESULTS if r["experiment"] == "final_campaign"])
print("\nIdentity preservation across the final campaign "
      "(how well the same car survived each environment):\n")
print(final[["variant", "identity", "adherence", "sharpness", "seconds"]]
      .to_string(index=False))
print(f"\nMean identity similarity: {final['identity'].mean():.2f}"
      f"  |  std: {final['identity'].std():.2f}")
print(f"Contact sheet saved to {OUT_DIR/'final_campaign_contact_sheet.png'}")
""")

# ---------------------------------------------------------------------------
md("""
## 10. Findings

*Fill the blanks in from your own run — the numbers will differ slightly on each
GPU, and the point of the exercise is to read your own results.*

**Expected pattern for each parameter**

| Experiment | What to look for |
|---|---|
| 1 · Prompt | The detailed prompt should raise prompt adherence substantially. Note that its tail is truncated at 77 CLIP tokens, so the last clauses may have no effect — length alone is not the mechanism. |
| 2 · Negative prompt | Should mainly raise sharpness and reduce artefacts rather than change composition. |
| 3 · Seed | Seed changes composition but not systematic quality. **Use this as your noise floor:** if two parameter settings differ by less than the spread across seeds, the difference is not real. |
| 4 · CFG scale | 3 tends to drift off-prompt; 12 tends to over-saturate and warp body panels. 7 is usually the balance. |
| 5 · Inference steps | Quality should plateau around 20–30 with DPM-Solver++. Anything beyond that costs time for little gain. |
| 6 · Strength | The central trade-off. Low strength preserves the car but barely applies the new environment; high strength produces a convincing scene but a different car. Watch the two curves cross in the §8 plot. |
| 7 · Environment | Tests whether identity survives a full scene change. |
| 8 · Lighting | Night is usually hardest — low light plus reflections invites artefacts. |
| 9 · Camera | Close-up should score highest on identity (more of the frame is product); wide-angle lowest. |
| 10 · Style | Luxury and cinematic often win on aesthetics but can lose identity through heavy colour grading. |

**Write-up prompts**

1. Which parameter had the largest effect on identity preservation, and by how much?
2. Was the difference between your best and worst setting larger than the seed-to-seed spread from Experiment 3? If not, what does that mean for your conclusion?
3. Where did the strength curves cross, and what value would you recommend for a real ad campaign?
4. Did the composite score agree with your own visual judgement? Where did they disagree, and which do you trust?

**Limitations of this evaluation**

- CLIP image-image similarity measures *semantic* likeness, not brand-exact
  identity. It cannot tell a Kia Seltos from a similar SUV, so it would not
  satisfy a real client.
- Sharpness rewards high-frequency detail, so a busy or noisy background can
  score higher than a clean studio composition.
- The best combination comes from a greedy coordinate search and may miss
  parameter interactions.
- Stable Diffusion cannot render legible text, so badges and number plates will
  be garbled in every output.
""")

code(r"""
# Package everything for submission
import shutil
shutil.make_archive("ad_outputs_submission", "zip", OUT_DIR)
print("Created ad_outputs_submission.zip containing:")
for p in sorted(OUT_DIR.iterdir()):
    print(f"  {p.name}")

# In Colab, uncomment to download:
# from google.colab import files
# files.download("ad_outputs_submission.zip")
""")


# ===========================================================================
def main() -> int:
    nb = nbf.v4.new_notebook(cells=cells)
    nb.metadata.update({
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11"},
        "colab": {"provenance": [], "gpuType": "T4"},
        "accelerator": "GPU",
    })

    failures = 0
    for i, cell in enumerate(nb.cells):
        if cell.cell_type != "code":
            continue
        src = "".join(l for l in cell.source.splitlines(keepends=True)
                      if not l.lstrip().startswith("!"))
        try:
            compile(src, f"<cell {i}>", "exec")
        except SyntaxError as exc:
            failures += 1
            print(f"SYNTAX ERROR in cell {i}: line {exc.lineno}: {exc.msg}")
            print(f"    {(exc.text or '').strip()}")

    nbf.validate(nb)
    OUT.write_text(nbf.writes(nb), encoding="utf-8")

    n_code = sum(1 for c in nb.cells if c.cell_type == "code")
    n_md = sum(1 for c in nb.cells if c.cell_type == "markdown")
    print(f"\nWrote {OUT.name}")
    print(f"  {len(nb.cells)} cells ({n_code} code, {n_md} markdown)")
    print(f"  syntax errors: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
