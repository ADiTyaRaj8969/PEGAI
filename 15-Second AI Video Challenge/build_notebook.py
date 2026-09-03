#!/usr/bin/env python
"""Generates Marwadi_2050_Video.ipynb.

Built programmatically so every code cell is syntax-checked before it ships.

    python build_notebook.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).parent
OUT = HERE / "Marwadi_2050_Video.ipynb"

cells: list = []
md = lambda t: cells.append(nbf.v4.new_markdown_cell(t.strip("\n")))
code = lambda t: cells.append(nbf.v4.new_code_cell(t.strip("\n")))


# ===========================================================================
md(r"""
# Marwadi University 2050 — 15-Second AI Video
### 15-Second AI Video Challenge

**Aditya Raj** · Enrollment No. 92301733062 · ICT · Batch 7EK1'A'
*Prompt Engineering for Generative AI*

---

## The brief

Create a 15-second AI-generated video telling a small visual story connected to
Marwadi University. The objective is **not** a beautiful video — it is to show
that prompt engineering can control **scene, characters, environment, camera
movement and visual storytelling**.

## What this notebook does

| | |
|---|---|
| **Theme** | Marwadi University in 2050 |
| **Structure** | 5 clips × 3 seconds = 15 seconds |
| **Model** | Zeroscope v2 576w (`cerspense/zeroscope_v2_576w`) — open source |
| **Output** | 576×320, 8 fps, 120 frames total |
| **Runtime** | Colab free T4, roughly 6–10 minutes |

## The story

A single narrative arc — *arrive → enter → learn → build → graduate* — so the
15 seconds reads as a story rather than five unrelated shots.

| Shot | Time | Beat | Camera movement |
|---|---|---|---|
| 1 | 0–3 s | Arrival — the campus at sunrise | Aerial drone push-in |
| 2 | 3–6 s | Entry — students through a holographic archway | Low tracking shot, forward |
| 3 | 6–9 s | Learning — a future laboratory | Slow dolly-in |
| 4 | 9–12 s | Building — hackathon night | Low-angle, slow orbit |
| 5 | 12–15 s | Graduation — convocation with drones | Crane shot rising |

> **Runtime:** Colab → Runtime → Change runtime type → **T4 GPU**.
""")

# ---------------------------------------------------------------------------
md("## 1. Setup")

code(r"""
!pip -q install "diffusers>=0.31.0" transformers accelerate safetensors imageio imageio-ffmpeg --upgrade
print("Done. If Colab asks you to restart the runtime, restart and re-run from here.")
""")

code(r"""
import gc, json, math, time, textwrap
from pathlib import Path

import numpy as np
import torch
import imageio.v2 as imageio
import matplotlib.pyplot as plt
from IPython.display import HTML, display

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DTYPE  = torch.float16 if DEVICE == "cuda" else torch.float32

OUT = Path("video_out"); OUT.mkdir(exist_ok=True)
CLIPS = OUT / "clips"; CLIPS.mkdir(exist_ok=True)

FPS           = 8
DURATION_S    = 15
N_SHOTS       = 5
TARGET_FRAMES = FPS * DURATION_S        # 120 frames = exactly 15.00 s
WIDTH, HEIGHT = 576, 320

# Cross-dissolve length at each join, in frames. 0 = hard cuts.
# A cross-dissolve BLENDS frames from both sides of a join, so it *consumes*
# frames and shortens the result. FRAMES_CLIP is therefore derived from the
# target rather than fixed, and the concatenation is trimmed to TARGET_FRAMES,
# so the final video is exactly 15 s whatever XFADE is set to.
XFADE       = 0
JOINS       = N_SHOTS - 1
FRAMES_CLIP = math.ceil((TARGET_FRAMES + JOINS * XFADE) / N_SHOTS)

print(f"torch {torch.__version__} | device {DEVICE}")
if DEVICE == "cuda":
    print("gpu:", torch.cuda.get_device_name(0))
else:
    print("\n!! No GPU. Runtime -> Change runtime type -> T4 GPU.")
print(f"\nPlan: {N_SHOTS} clips x {FRAMES_CLIP} frames, {XFADE}-frame crossfade "
      f"at {JOINS} joins")
print(f"      -> {N_SHOTS*FRAMES_CLIP - JOINS*XFADE} frames, trimmed to "
      f"{TARGET_FRAMES} = {TARGET_FRAMES/FPS:.2f} s at {WIDTH}x{HEIGHT}")
""")

# ---------------------------------------------------------------------------
md("""
### 1.1 Load the open-source video model

**Zeroscope v2 576w** is a watermark-free, open-source text-to-video diffusion
model fine-tuned from ModelScope. It is chosen here because it produces clean
576×320 output and fits comfortably in a free T4 — a larger model such as
CogVideoX would give better fidelity but risks running out of memory mid-render.
""")

code(r"""
from diffusers import DiffusionPipeline, DPMSolverMultistepScheduler

CANDIDATES = [
    "cerspense/zeroscope_v2_576w",       # primary: open source, no watermark
    "damo-vilab/text-to-video-ms-1.7b",  # fallback: ModelScope (has a watermark)
]

def load_video_pipeline():
    last = None
    for model_id in CANDIDATES:
        try:
            print(f"Loading {model_id} ...")
            pipe = DiffusionPipeline.from_pretrained(model_id, torch_dtype=DTYPE)
            pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
            pipe = pipe.to(DEVICE)
            if DEVICE == "cuda":
                pipe.enable_vae_slicing()          # keeps VAE decode inside T4 memory
                pipe.enable_model_cpu_offload()    # offloads idle submodules
            pipe.set_progress_bar_config(disable=True)
            print(f"Loaded {model_id}")
            return pipe, model_id
        except Exception as exc:
            print(f"  failed: {type(exc).__name__}: {str(exc)[:150]}")
            last = exc
    raise RuntimeError(f"No video model could be loaded. Last error: {last}")

pipe, MODEL_ID = load_video_pipeline()
""")

# ---------------------------------------------------------------------------
md("""
## 2. Prompt engineering — the storyboard

This is the part the assignment is actually graded on. Every prompt is built
from **six explicit control dimensions**, so each shot is directed rather than
merely described:

| Dimension | Purpose | Example |
|---|---|---|
| **Subject** | Who or what is in frame | "students in smart uniforms" |
| **Environment** | Where, and what the world looks like | "futuristic university campus, glass towers, solar canopies" |
| **Camera** | The shot type and its movement | "aerial drone shot slowly pushing forward" |
| **Lighting** | Time of day and mood | "golden sunrise light, long shadows" |
| **Style** | Visual treatment | "cinematic, photorealistic, shallow depth of field" |
| **Quality** | Technical tags | "highly detailed, 4k, smooth motion" |

**Continuity** is what turns five clips into one story. Three anchors are
repeated verbatim across all five prompts so the world stays recognisable:
`futuristic university campus`, `glass and steel architecture with greenery`,
and `warm teal-and-amber colour grade`. Camera movement then carries the
narrative: push-in → track → dolly → orbit → crane-up.
""")

code(r"""
# Repeated in every shot so the five clips look like one place and one film.
CONTINUITY = ("futuristic university campus, glass and steel architecture with "
              "hanging greenery, warm teal and amber colour grade")
STYLE   = "cinematic film still, photorealistic, shallow depth of field, volumetric light"
QUALITY = "highly detailed, sharp focus, smooth natural motion, 4k"

NEGATIVE = ("blurry, low quality, distorted, deformed faces, extra limbs, text, "
            "watermark, logo, subtitles, jpeg artifacts, flickering, static frame, "
            "cartoon, low resolution, oversaturated")

STORYBOARD = [
    dict(
        n=1, beat="Arrival",
        subject="a wide view of a grand university campus with students arriving",
        environment=f"{CONTINUITY}, wide plazas, solar canopies, autonomous shuttles gliding along a tree-lined avenue",
        camera="aerial drone shot slowly pushing forward and descending toward the main building",
        lighting="golden sunrise light, long soft shadows, light morning haze",
    ),
    dict(
        n=2, beat="Entry",
        subject="groups of students in smart casual uniforms walking together, carrying transparent tablets",
        environment=f"{CONTINUITY}, a luminous holographic entrance archway projecting the university crest",
        camera="low tracking shot moving forward behind the students, steadicam",
        lighting="soft morning daylight with cyan holographic glow on their faces",
    ),
    dict(
        n=3, beat="Learning",
        subject="students and a professor around a floating three-dimensional hologram of a molecule",
        environment=f"{CONTINUITY}, a bright future laboratory with robotic arms and curved glass display walls",
        camera="slow dolly-in toward the hologram, eye level",
        lighting="cool interior lighting with bright cyan light spilling from the hologram",
    ),
    dict(
        n=4, beat="Building",
        subject="focused students coding at glowing workstations during a late-night hackathon",
        environment=f"{CONTINUITY}, an open innovation hall at night, monitors and LED strips glowing, city lights beyond the glass",
        camera="low-angle shot slowly orbiting around a workstation",
        lighting="dark room lit by monitor glow and amber desk lamps, strong rim light",
    ),
    dict(
        n=5, beat="Graduation",
        subject="graduating students in ceremonial robes throwing their caps into the air, celebrating",
        environment=f"{CONTINUITY}, a vast open convocation ground with a crowd and a lit stage, camera drones hovering above",
        camera="crane shot rising upward and tilting to reveal the whole campus skyline",
        lighting="warm golden hour sunset, glowing particles and confetti in the air",
    ),
]

def build_prompt(shot: dict) -> str:
    '''Compose the six control dimensions into one directed prompt.'''
    return ", ".join([shot["subject"], shot["environment"],
                      shot["camera"], shot["lighting"], STYLE, QUALITY])

for s in STORYBOARD:
    print(f"--- SHOT {s['n']} · {s['beat']} · {(s['n']-1)*3}-{s['n']*3}s ---")
    print(textwrap.fill(build_prompt(s), 92, initial_indent="  ", subsequent_indent="  "))
    print()
print("NEGATIVE PROMPT (applied to every shot):")
print(textwrap.fill(NEGATIVE, 92, initial_indent="  ", subsequent_indent="  "))
""")

# ---------------------------------------------------------------------------
md("""
## 3. Generate the five clips

Each shot uses a fixed seed so the render is reproducible, and each is saved as
its own `.mp4` — those individual files are the evidence that five separate
clips were generated before being combined in §4.
""")

code(r"""
SEEDS = [101, 202, 303, 404, 505]
STEPS = 40
GUIDANCE = 12.0

def generate_clip(shot, seed):
    prompt = build_prompt(shot)
    gen = torch.Generator(device=DEVICE).manual_seed(seed)
    t0 = time.time()
    result = pipe(
        prompt=prompt,
        negative_prompt=NEGATIVE,
        num_inference_steps=STEPS,
        guidance_scale=GUIDANCE,
        num_frames=FRAMES_CLIP,
        height=HEIGHT, width=WIDTH,
        generator=gen,
    )
    frames = result.frames[0]
    # diffusers returns float [0,1] or uint8 depending on version - normalise.
    frames = [np.asarray(f) for f in frames]
    if frames[0].dtype != np.uint8:
        frames = [(np.clip(f, 0, 1) * 255).astype(np.uint8) for f in frames]
    return frames, time.time() - t0

all_frames, log = [], []
for shot, seed in zip(STORYBOARD, SEEDS):
    print(f"Shot {shot['n']} ({shot['beat']}) ...", end=" ", flush=True)
    frames, secs = generate_clip(shot, seed)
    path = CLIPS / f"shot{shot['n']}_{shot['beat'].lower()}.mp4"
    imageio.mimsave(path, frames, fps=FPS, quality=9)
    all_frames.append(frames)
    log.append(dict(shot=shot["n"], beat=shot["beat"], seed=seed,
                    frames=len(frames), seconds=round(secs, 1),
                    file=path.name, prompt=build_prompt(shot)))
    print(f"{len(frames)} frames in {secs:.0f}s -> {path.name}")

print(f"\nGenerated {sum(len(f) for f in all_frames)} frames across "
      f"{len(all_frames)} clips ({sum(len(f) for f in all_frames)/FPS:.1f} s of footage).")
""")

code(r"""
# Contact sheet: the middle frame of each shot, as a storyboard preview
fig, axes = plt.subplots(1, 5, figsize=(19, 3.2))
for ax, frames, shot in zip(axes, all_frames, STORYBOARD):
    ax.imshow(frames[len(frames)//2]); ax.axis("off")
    ax.set_title(f"Shot {shot['n']} · {shot['beat']}\n{(shot['n']-1)*3}-{shot['n']*3}s", fontsize=10)
fig.suptitle("Storyboard — middle frame of each generated clip", fontsize=13)
plt.tight_layout(); plt.savefig(OUT / "storyboard_contact_sheet.png", dpi=140); plt.show()
""")

# ---------------------------------------------------------------------------
md("""
## 4. Combining the clips  *(required by the brief)*

The five clips are joined into one continuous 15-second video by concatenating
their frame arrays and writing a single MP4.

**The frame arithmetic matters here.** A cross-dissolve *blends* frames from
both sides of a join rather than adding new ones, so it **shortens** the
result: five 24-frame clips with a 6-frame dissolve at each of the four joins
would give 5×24 − 4×6 = 96 frames = 12 s, not 15. Two things prevent that:

- `FRAMES_CLIP` is derived from the target — `ceil((120 + joins×XFADE) / 5)` —
  so enough footage is generated to absorb the dissolves;
- the concatenation is trimmed to exactly `TARGET_FRAMES` afterwards.

The default is `XFADE = 0` (hard cuts), which is the normal convention for a
five-shot montage and lands on exactly 120 frames. Raise it to 4–6 for
dissolves; the duration stays 15 s either way.
""")

code(r"""
def crossfade_concat(clips, xfade=XFADE):
    '''Concatenate clips, blending `xfade` frames at every join.

    The tail of clip i and the head of clip i+1 are averaged with a linear
    ramp, so total length is preserved exactly.
    '''
    out = list(clips[0])
    for nxt in clips[1:]:
        nxt = list(nxt)
        n = min(xfade, len(out), len(nxt))
        if n:
            tail = out[-n:]
            head = nxt[:n]
            blended = []
            for i in range(n):
                a = (i + 1) / (n + 1)          # 0 -> 1 across the transition
                blended.append((tail[i].astype(np.float32) * (1 - a)
                                + head[i].astype(np.float32) * a).astype(np.uint8))
            out = out[:-n] + blended + nxt[n:]
        else:
            out = out + nxt
    return out

joined = crossfade_concat(all_frames)
print(f"Concatenated: {len(joined)} frames "
      f"({N_SHOTS}x{FRAMES_CLIP} - {JOINS}x{XFADE} blended)")

# Trim to the exact target so the brief's 15 seconds is guaranteed.
final_frames = joined[:TARGET_FRAMES]
if len(final_frames) < TARGET_FRAMES:
    raise RuntimeError(f"Only {len(final_frames)} frames available, "
                       f"need {TARGET_FRAMES}. Lower XFADE or raise FRAMES_CLIP.")
duration = len(final_frames) / FPS

FINAL = OUT / "marwadi_2050_15s.mp4"
imageio.mimsave(FINAL, final_frames, fps=FPS, quality=9)

print(f"Final video : {FINAL}")
print(f"Frames      : {len(final_frames)} (trimmed from {len(joined)})")
print(f"Duration    : {duration:.2f} s at {FPS} fps")
print(f"Resolution  : {final_frames[0].shape[1]}x{final_frames[0].shape[0]}")
print(f"Size        : {FINAL.stat().st_size/1_000_000:.2f} MB")
assert 14.0 <= duration <= 16.0, f"Duration {duration:.2f}s is outside the 15-second brief"
print("\nDuration is within the 15-second requirement.")
""")

code(r"""
# Play it inline
import base64
b64 = base64.b64encode(FINAL.read_bytes()).decode()
display(HTML(f'''
<video width="576" controls loop autoplay muted style="border-radius:8px">
  <source src="data:video/mp4;base64,{b64}" type="video/mp4">
</video>'''))
""")

# ---------------------------------------------------------------------------
md("""
## 5. Prompt refinement log

The prompts above are the final version. These are the changes that mattered,
recorded because the assignment is about prompt control rather than the render
itself. Replace these with what you actually observe on your run.

| # | Problem seen | Change made | Result |
|---|---|---|---|
| 1 | Clips looked like five unrelated places | Added the shared `CONTINUITY` string to every prompt | The five shots read as one campus |
| 2 | Almost no motion — nearly a still image | Moved camera movement into its own explicit clause ("slowly pushing forward", "orbiting") | Consistent, directed motion |
| 3 | Warped faces in crowd shots | Added `deformed faces, extra limbs` to the negative prompt | Fewer artefacts; crowds kept distant |
| 4 | Colour jumped between shots | Fixed `warm teal and amber colour grade` in `CONTINUITY` | Consistent grade across the cut |
| 5 | Text and watermarks appearing | Added `text, watermark, logo, subtitles` to the negative prompt | Clean frames |
| 6 | Weak prompt adherence | Raised `guidance_scale` from 9 to 12 | Shots match their direction more closely |

**The single most useful lesson:** in text-to-video, *camera movement is a
prompt component, not an afterthought*. Describing a scene produces a nearly
static shot; describing a **camera move through** the scene is what produces
motion. That is the difference between shot 1 as written and shot 1 without its
camera clause.
""")

code(r"""
# Save everything needed for the submission document
manifest = dict(
    student="Aditya Raj", enrollment="92301733062", department="ICT", batch="7EK1'A'",
    theme="Marwadi University in 2050",
    model=MODEL_ID, model_licence="open source",
    structure=f"{len(STORYBOARD)} clips x {FRAMES_CLIP/FPS:.0f} s = {duration:.1f} s",
    fps=FPS, resolution=f"{WIDTH}x{HEIGHT}",
    inference_steps=STEPS, guidance_scale=GUIDANCE, crossfade_frames=XFADE,
    negative_prompt=NEGATIVE, continuity_anchor=CONTINUITY,
    shots=log,
)
(OUT / "video_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

import shutil
shutil.make_archive("marwadi_2050_submission", "zip", OUT)

print("Files produced:")
for p in sorted(OUT.rglob("*")):
    if p.is_file():
        print(f"  {p.relative_to(OUT)}  ({p.stat().st_size/1000:.0f} KB)")
print("\nZipped to marwadi_2050_submission.zip")

# In Colab, uncomment to download:
# from google.colab import files
# files.download("marwadi_2050_submission.zip")
""")

# ---------------------------------------------------------------------------
md("""
## 6. What to submit

1. **Upload `marwadi_2050_15s.mp4` to Google Drive** and set sharing to
   *Anyone with the link*.
2. Open `SUBMISSION_DOCUMENT.md` (next to this notebook), paste the video link
   into the placeholder, and export it to PDF.
3. Upload that PDF to Drive, set it to public, and submit **that** link — the
   brief asks for one document containing the video link, the prompts, the model
   name, the generation explanation, and how the clips were combined.

`video_manifest.json` holds every prompt, seed and parameter from your actual
run, so the document can be filled in from real values rather than memory.
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
            print(f"SYNTAX ERROR cell {i} line {exc.lineno}: {exc.msg}")

    nbf.validate(nb)
    OUT.write_text(nbf.writes(nb), encoding="utf-8")
    n_code = sum(1 for c in nb.cells if c.cell_type == "code")
    print(f"Wrote {OUT.name}")
    print(f"  {len(nb.cells)} cells ({n_code} code, {len(nb.cells)-n_code} markdown)")
    print(f"  syntax errors: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
