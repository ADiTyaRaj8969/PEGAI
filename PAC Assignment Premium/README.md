# LectureAI — Prompt Engineering Lecture Note Generator

**PAC Premium Learner Assignment · Question 2**
Aditya Raj · 92301733062 · ICT · 7EK1'A'

---

## What this is

A web application that generates **standardised** lecture notes from a course/
topic specification. The brief's problem statement is that AI-generated teaching
content "varies in technical depth, structure, accuracy, examples, visual
representation and presentation quality due to ineffective prompts" — so the
application's job is to remove that variance through prompt design, not to be a
chat wrapper.

## Run it

1. Open `index.html` in a browser (no server or build needed)
2. Click **API Key** in the navigation bar, paste a Gemini key from
   [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
3. Fill in the course and topic, tick the sections you want
4. Pick a prompt engineering technique and click **Generate Lecture Notes**

The key lives in `sessionStorage` only and is never written into the source.

## The six prompt engineering techniques

This is the substance of the assignment. Each technique builds a **structurally
different prompt** — not the same prompt with a different label:

| Technique | Mechanism | API calls |
|---|---|---|
| **Role Prompting** | Assigns an expert identity so tone, depth and priorities follow from the persona | 1 |
| **Structured Prompting** | Delimits the request into labelled `<task>` / `<context>` / `<constraints>` blocks so instruction cannot be confused with content | 1 |
| **Template Prompting** | Supplies a fixed skeleton with `{{placeholders}}` — this is what actually produces *standardisation* across different topics | 1 |
| **Few-Shot Prompting** | Two worked exemplars establish a house style (definition → intuition → formalism → worked case → misconception) | 1 |
| **Prompt Chaining** | Four dependent calls: outline → expand → examples → assessment, each constrained by the previous output | 4 |
| **Iterative Refinement** | Draft → the model critiques its own draft against explicit criteria → rewrite | 3 |

The last two are genuine multi-step workflows. Chaining passes each step's output
into the next prompt; iterative refinement passes both the original draft *and*
the critique into the rewrite. The step counter in the loading overlay shows this
happening.

**Prompt refinement** (the brief asks for it explicitly) is implemented three
ways: the built-in iterative technique above, a feedback box that revises the
current notes, and a fully editable prompt box for manual control.

**Shared house rules** are appended to every technique — depth must match the
Bloom's level, define terms on first use, and *never invent citations,
statistics or standards*; where a reference is needed but uncertain, the model
must emit `[VERIFY: …]` rather than fabricate. That last rule is the one that
matters for a teaching tool.

## Features

- Live prompt preview that updates as you type — you see exactly what will be sent
- **Compare All Techniques** runs all six on the same input and renders them side by side
- Version tabs to switch between generated variants
- Export to PDF via a print stylesheet
- History saved to `localStorage`, with open/delete
- Bloom's taxonomy level, target audience, duration and teaching method all feed the prompt
- 10 toggleable sections (theory, maths, algorithms, examples, case study, quiz, viva, references…)

## Error handling

Missing API key, malformed key, no topic, no sections selected, invalid key
(400), forbidden (403), model unavailable (404 — falls through a list of four
models automatically), rate limit (429), server error (5xx), safety block, empty
response, network failure, and blocked pop-ups on export. Each surfaces as a
toast; nothing crashes the page.

## Files

| File | Purpose |
|---|---|
| `index.html` | Interface (was already present) |
| `style.css` | Styling (was already present) |
| `app.js` | **The application** — techniques, API integration, rendering, history |

## Note on what was missing

`index.html` and `style.css` were already in this folder, but `index.html`
referenced `<script src="app.js"></script>` and **that file did not exist** — so
every button was inert and no AI integration was present. `app.js` is what makes
the interface work.

## Verification performed

`node --check` on `app.js`; all 15 inline `onclick` handlers confirmed to exist
and be exported to `window`; every element ID referenced by the JavaScript
confirmed to exist in `index.html`; no hardcoded API key. The six technique
builders were unit-tested in Node: all produce distinct prompts, each embeds the
topic and the anti-fabrication rule, declared step counts match actual chain
lengths, chained steps genuinely consume the previous step's output, and the
iterative rewrite receives both the draft and the critique.

**Not verified:** live Gemini output quality — that needs your API key, so the
first real run is yours.
