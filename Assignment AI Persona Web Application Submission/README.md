# AI Career Counsellor — Persona-Based Web Application

A single-file web application that gives career guidance from five distinct AI
counsellor personas, powered by the Gemini API.

---

## 1. Project title

**AI Career Counsellor — Persona-Based Guidance using the Gemini API**

## 2. Problem statement

Engineering students face career decisions with no single right answer. "Should
I prepare for placements or pursue higher studies?" gets a different — and
individually valid — answer from a technical mentor, a placement officer, a
research supervisor, a startup founder and a competitive-exam coach.

A general-purpose chatbot collapses all of these into one averaged, hedged reply
that reads reasonably and helps nobody. The student never sees that the question
has genuinely competing answers, or what the trade-off actually is.

## 3. Objective

Demonstrate that **prompt engineering — not model choice — controls output**, by
building an application where the same question, the same model and the same API
call produce five meaningfully different expert perspectives, plus a structured
comparison of them.

Concretely:

- Define each persona with the six Prompt Card elements (Role, Audience,
  Context, Format, Constraints, Language).
- Let the user query one persona or several.
- Use **one** Gemini request for multiple personas, not one per persona.
- Force out-of-scope refusal rather than confident guessing.
- Present a side-by-side comparison so the trade-off is visible.

## 4. Personas

| # | Persona | Perspective | Accent |
|---|---|---|---|
| 1 | Technical Career Counsellor | AI/ML, programming, projects, technical skill order | Blue |
| 2 | HR & Placement Counsellor | Resume signal, interviews, employability, hiring timeline | Orange |
| 3 | Academic & Research Counsellor | MS/M.Tech/PhD, research fit, funding, applications | Green |
| 4 | Entrepreneurship Counsellor | Validation, MVP, first revenue, risk management | Purple |
| 5 | Government & PSU Counsellor | GATE, PSU recruitment, civil services, banking | Red |

Persona 5 is my own addition. Public-sector careers are a major and genuinely
different path for Indian engineering students, and it runs on fixed exam
calendars rather than hiring cycles — which makes it disagree with the other
four in a useful way.

Colour is never the only signal: every persona also carries its full name in the
response header, so the interface does not depend on colour perception.

## 5. Prompt Cards

Full six-element cards for all five personas are in **[PROMPT_CARDS.md](PROMPT_CARDS.md)**
(the one-page deliverable). They are also viewable inside the app — click
"View Prompt Card" on any persona.

Example, abbreviated:

| Element | Technical Career Counsellor |
|---|---|
| **Role** | Senior Technical Career Counsellor specialising in AI, ML and Software Engineering, 12 years mentoring |
| **Audience** | Undergraduate ICT/CS students in India preparing for technical roles |
| **Context** | Student wants concrete direction: which skills, in what order, which projects prove ability |
| **Format** | Recommendation → Skills to Develop → Project Suggestions → Career Roadmap |
| **Constraints** | Never guarantee jobs or salaries · do not invent statistics · say "I don't know" if off-topic |
| **Language** | Simple English, expand acronyms on first use |

## 6. Technology used

| Layer | Choice |
|---|---|
| Frontend | Single `index.html` — HTML + CSS + JavaScript inline, as required |
| Framework | None. Vanilla JS, zero dependencies, zero build step |
| AI | Gemini API (`generativelanguage.googleapis.com/v1beta`) |
| Response format | Structured JSON via `responseSchema` |
| Key storage | `sessionStorage`, entered at runtime — never in source |

## 7. Gemini API integration

**Endpoint**

```
POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}
```

**One request for N personas.** This is the requirement the assignment
emphasises, so it drives the design. All selected Prompt Cards go into a single
structured prompt, and the model returns one JSON array entry per persona:

```
User question
      ↓
Selected personas → one structured prompt (all Prompt Cards)
      ↓
ONE Gemini API request   ← not one call per persona
      ↓
JSON: [{id, answer, mainRecommendation, priority, suggestedAction, inScope}, …]
      ↓
Separate response cards + comparison table
```

The app displays a badge reading **"1 API request for N personas"** on every
result, so the efficiency claim is visible rather than asserted.

**Structured output.** `generationConfig.responseSchema` constrains the reply to
a fixed schema. This is what makes the comparison table possible — the three
comparison fields are guaranteed present and short (≤ 6 words), instead of being
scraped out of prose with a regex.

**Model selection.** A dropdown defaults to `gemini-2.0-flash`. Because model
availability differs by account and region, **"Load my models"** calls the
`/v1beta/models` endpoint, filters to those supporting `generateContent`, and
repopulates the dropdown with what your key can actually use.

**Error handling** (section 17 of the brief):

| Situation | Message |
|---|---|
| No persona selected | "Please select at least one persona." |
| Empty question | "Please enter your career-related question." |
| No API key | "Please enter your Gemini API key in step 1." |
| Invalid key (400) | "That API key was rejected. Check it at aistudio.google.com/app/apikey." |
| Forbidden (403) | "Access denied. The key may lack permission for this model." |
| Model unavailable (404) | Names the model and suggests "Load my models" |
| Rate limited (429) | "Rate limit reached. Wait a moment and try again." |
| Server error (5xx) | "Gemini server error. Try again shortly." |
| Safety block | "The response was blocked by a safety filter. Try rephrasing." |
| Token limit hit | "Select fewer personas or shorten the question." |
| Malformed JSON | Falls back to extracting the JSON object; then a clear parse error |

The app never crashes on any of these — each surfaces as a readable message.

**Security note.** Because the app is frontend-only, the key travels from the
browser to Google directly. That is fine for an assignment demo, but for a real
deployment the call belongs behind a backend proxy so the key is never in the
client at all. Worth saying in the viva.

## 8. Application screenshots

> **To do before submitting.** Run the app, take these four screenshots, save
> them in `assets/`, and the links below will resolve.

| Screenshot | What to capture | File |
|---|---|---|
| Interface | Full page, personas visible | `assets/01-interface.png` |
| Single persona | One persona selected + its response | `assets/02-single-persona.png` |
| Multiple personas | 3+ selected, separate responses | `assets/03-multi-persona.png` |
| Comparison table | The side-by-side table | `assets/04-comparison.png` |

![Interface](assets/01-interface.png)
![Single persona](assets/02-single-persona.png)
![Multiple personas](assets/03-multi-persona.png)
![Comparison](assets/04-comparison.png)

## 9. How to run the application

1. Get a free Gemini API key at **aistudio.google.com/app/apikey**
2. Open `index.html` in any modern browser — no server, no install, no build
3. Paste the key into step 1 (optionally click **Load my models**)
4. Select one or more personas
5. Type a question and click **Get Career Advice**

The key stays in `sessionStorage` and is cleared when the tab closes.

## 10. Sample questions

Built into the app as one-click buttons:

1. *Should I prepare for placements or pursue higher studies?* — the sharpest
   persona disagreement; best question for the demo video
2. *I know Python but do not have any projects. What should I do?*
3. *Should I become an AI Engineer, Data Scientist or Software Developer?*
4. *What is the best recipe for pizza?* — **off-topic control.** Every persona
   should set `inScope: false` and decline. This is how you demonstrate that
   constraints are actually enforced, not decorative.

Test each with one persona, then with several, per section 18 of the brief.

## 11. Sample outputs

> **To do before submitting.** Paste your real outputs here after running.
> Expected shape for question 1 with three personas selected:

| Aspect | Technical | HR & Placement | Academic & Research |
|---|---|---|---|
| Main Recommendation | *(from run)* | *(from run)* | *(from run)* |
| Priority | *(from run)* | *(from run)* | *(from run)* |
| Suggested Action | *(from run)* | *(from run)* | *(from run)* |

The point to check: do the three rows genuinely diverge? If all three personas
recommend roughly the same thing, the prompt design has failed, and that is the
main thing this assignment is graded on.

## 12. Team members

| Name | Enrollment No. | Department | Batch |
|---|---|---|---|
| Aditya Raj | 92301733062 | ICT | 7EK1'A' |

---

## Requirements checklist

| Requirement | Status |
|---|---|
| Minimum 4 personas | 5 |
| Select one or multiple personas | Checkboxes + Select all / Clear |
| Responses generated by Gemini | Yes — no hard-coded replies anywhere |
| Meaningfully different perspectives | Enforced by distinct Prompt Cards + an explicit differentiation rule |
| One request for multiple personas | Yes — shown as a badge on every result |
| Six Prompt Card elements | All six, per persona |
| Single HTML file | Yes — HTML + CSS + JS inline |
| No API key in source | Runtime entry, `sessionStorage` only |
| Error handling | 11 cases, table above |
| Off-topic → "I don't know" | `inScope: false`, flagged in the UI |
| Comparison section | Auto-generated table for 2+ personas |
| README | This file |
| Demo video | **You must record it** — see below |

## Still to do

1. **Record the demo video** covering the 10 points in section 19 of the brief:
   interface → personas → single selection → question → response → multiple
   selection → same question → multiple responses → comparison → explanation of
   the Prompt Card and prompt flow.
   Use the **Preview constructed prompt** button for the last point — it shows
   the exact text sent to Gemini, which is the clearest way to explain the flow.
2. **Take the four screenshots** into `assets/`.
3. **Fill in section 11** with real outputs.
4. **Push to GitHub** and confirm no key is committed.

## Verification performed

JavaScript syntax-checked with `node --check`. Persona cards, prompt
construction, JSON schema and the output formatter were unit-tested in Node: all
five cards carry the six elements, every card enforces the out-of-scope,
no-guarantee and no-fabrication rules, the multi-persona prompt embeds all five
cards in one request, and the response formatter escapes HTML so model output
cannot inject markup.

Not verified: live Gemini responses. That needs your API key, so the first real
run is yours.
