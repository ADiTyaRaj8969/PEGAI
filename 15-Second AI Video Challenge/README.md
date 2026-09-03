# 15-Second AI Video Challenge — Marwadi University 2050

**Aditya Raj** · 92301733062 · ICT · 7EK1'A'

---

## What you submit

**One PDF, uploaded to Drive with a public link**, containing the video link,
prompts, model name, generation explanation, and how the clips were combined.

`SUBMISSION_DOCUMENT.pdf` is that document — it just needs your video link.

## Three steps

1. **Generate the video.** Upload `Marwadi_2050_Video.ipynb` to Colab →
   Runtime → T4 GPU → Run all. Takes 6–10 minutes and produces
   `marwadi_2050_15s.mp4`.
2. **Upload the video** to Google Drive, sharing set to *Anyone with the link*.
3. **Paste the link** into `SUBMISSION_DOCUMENT.docx` (replacing the red
   placeholder in section 1), export to PDF, upload that to Drive as public, and
   submit the PDF link.

Re-run `python make_document.py` if you change any prompt in the notebook — the
document is generated from the notebook, so the two cannot drift apart.

## The video

| | |
|---|---|
| Theme | Marwadi University in 2050 |
| Structure | 5 clips × 3 seconds = **15.00 s** (the brief's "5 × 3-second clips" option) |
| Model | **Zeroscope v2 576w** (`cerspense/zeroscope_v2_576w`) — open source, watermark-free |
| Output | 576×320, 8 fps, 120 frames |
| Story | arrive → enter → learn → build → graduate |

| Shot | Time | Beat | Camera |
|---|---|---|---|
| 1 | 0–3 s | Arrival | Aerial drone push-in |
| 2 | 3–6 s | Entry | Low tracking shot |
| 3 | 6–9 s | Learning | Slow dolly-in |
| 4 | 9–12 s | Building | Low-angle orbit |
| 5 | 12–15 s | Graduation | Crane rising |

## How prompt engineering is demonstrated

The brief says the objective is **not** a beautiful video but demonstrable
control. Three mechanisms do that work:

**Six control dimensions per prompt** — subject, environment, camera, lighting,
style, quality. Each shot is *directed*, not merely described.

**A continuity anchor** repeated verbatim in all five prompts
(`futuristic university campus, glass and steel architecture with hanging
greenery, warm teal and amber colour grade`) so five separate generations read
as one place and one film.

**Camera movement as the storytelling device** — push-in → track → dolly →
orbit → crane-up. This is the single most useful finding: describing a *scene*
gives a nearly static shot; describing a *camera moving through* the scene is
what produces motion.

## Files

| File | Purpose |
|---|---|
| `Marwadi_2050_Video.ipynb` | Generates the clips and the final video |
| `SUBMISSION_DOCUMENT.pdf` / `.docx` | **The deliverable** — add your link |
| `build_notebook.py` | Builds the notebook, syntax-checking every cell |
| `make_document.py` | Builds the document from the notebook's own prompts |
| `selftest.py` | 50 logic checks |
| `Video Generation.pdf` | The original brief |

## What was verified, and what wasn't

**Verified locally** (`python selftest.py`, 50 checks): every code cell compiles;
the frame arithmetic lands on exactly 120 frames for `XFADE` values 0, 2, 4, 6
and 8; the cross-dissolve blends monotonically and preserves `uint8`; all five
prompts contain all six control dimensions plus the continuity anchor; all five
camera movements are distinct; the negative prompt blocks watermarks, text and
static output.

**One real bug this caught:** the first version cross-faded five 24-frame clips
and would have produced **96 frames = 12 seconds**, failing the 15-second
requirement — a cross-dissolve consumes frames rather than adding them. Frames
per clip is now derived from the target and the result is trimmed to exactly
120.

**Not verified:** video quality. There is no GPU on this machine, so no frame
has been rendered. The first real run is yours — and the prompt refinement log
in §5 of the notebook should be updated with what you actually observe.

## If the model fails to load

The notebook tries Zeroscope first, then falls back to
`damo-vilab/text-to-video-ms-1.7b` (ModelScope — note it renders a watermark).
If both fail, the usual cause is a Colab session without a GPU: check
Runtime → Change runtime type → T4 GPU.
