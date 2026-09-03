# AI Product Advertisement Generator — Assignment 3

**Aditya Raj** · 92301733062 · ICT · 7EK1'A'
Image Generation using Stable Diffusion

---

## Submit this

**`AI_Product_Advertisement_Generator.ipynb`** — 48 cells (25 code, 23 markdown).

## How to run

1. Open [colab.research.google.com](https://colab.research.google.com) → Upload → select the `.ipynb`
2. **Runtime → Change runtime type → T4 GPU** (the notebook checks this and warns you)
3. Runtime → Run all

~30 generated images, roughly **3–5 minutes** on a free T4. Everything lands in
`ad_outputs/` and the last cell zips it for download.

## Deliverables

| # | Required | Where |
|---|---|---|
| 1 | Original reference image | §3 — generated at a fixed seed, so the notebook runs with no external file |
| 2 | Prompts used | §4 — composed from environment/lighting/camera/style banks |
| 3 | Negative prompts | §4 — `none` vs `detailed` |
| 4 | Parameter values | §2 baseline + §7 per experiment |
| 5 | Generated images | §7 — all 10 experiments, displayed as labelled grids |
| 6 | Comparison table | §8 — `comparison_table.csv`, sortable, with metrics |
| 7 | Best prompt + best parameters | §9 — derived from the table, then re-rendered as a 5-environment campaign |

All 10 experiments from the brief are implemented: prompt, negative prompt, seed,
CFG scale, inference steps, img2img strength, environment, lighting, camera, style.

## How the comparison actually works

Rather than ranking images by eye, each one is scored on three measurable axes:

- **Identity similarity** — CLIP image-image cosine against the reference. This
  is the metric that matters most here, because the brief asks for varied ads
  *while maintaining the visual identity of the vehicle*.
- **Prompt adherence** — CLIP image-text cosine (CLIPScore).
- **Sharpness** — variance of the Laplacian.

```
composite = 0.45·identity + 0.35·adherence + 0.20·sharpness
```

each min-max normalised across all images first. §9 picks the winner of each
experiment and combines them. A `manual_score_1_5` column is left blank for your
own visual judgement — the metrics do not capture whether something looks like a
*good advertisement*.

## Files

| File | Purpose |
|---|---|
| `AI_Product_Advertisement_Generator.ipynb` | **The submission** |
| `build_notebook.py` | Generates the notebook; syntax-checks every code cell |
| `selftest.py` | Validates the GPU-independent logic (44 checks) |
| `png.pdf` | The original assignment brief |

Rebuild with `python build_notebook.py`, verify with `python selftest.py`.

## What I could and could not verify

**Verified locally:** every code cell compiles; prompt composition across all 135
environment × lighting × camera × style combinations; the sharpness metric
against flat/blurred/detailed control images; the full comparison-table and
best-configuration pipeline against synthetic data (including the
divide-by-zero guard when a metric column is constant).

**Not verified:** actual image quality. There is no GPU on this machine and the
SD weights are a multi-GB download, so no image has been generated. The notebook
is built to run correctly on Colab, but the first run is yours.

Two robustness measures for that first run: the model loader tries three
Stable Diffusion 1.5 repositories in turn, so a moved or gated repo is not fatal;
and text-to-image shares weights with image-to-image via `from_pipe`, so only one
copy sits in VRAM.

## Notes

- **Switching to SDXL:** set `USE_SDXL = True` in §2. Better quality at 1024px,
  but ~20–25 s per image on a T4 instead of ~4–6 s, and much closer to the
  free-tier memory ceiling.
- **Using your own product photo:** §3 has a commented-out Colab upload cell.
  Uncomment those three lines and the generation cell will skip itself.
- **Prompt truncation:** SD's CLIP text encoder caps at 77 tokens, so the tail of
  the detailed prompt is truncated. Subject and environment are ordered first
  deliberately. This is worth mentioning in your write-up for Experiment 1 —
  a longer prompt is not automatically a more effective one.
- **Seed as a noise floor:** Experiment 3 changes nothing but the seed. If two
  settings elsewhere differ by less than the spread across seeds, that difference
  is not real. §10 asks you to check this.
