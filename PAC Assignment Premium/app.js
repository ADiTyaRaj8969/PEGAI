/* =====================================================================
   LectureAI — Prompt Engineering Lecture Note Generator
   PAC Premium Learner Assignment · Question 2
   Aditya Raj · 92301733062 · ICT · 7EK1'A'
   ---------------------------------------------------------------------
   index.html is the interface; this file is the whole application.

   The assignment asks for a website that generates standardised lecture
   notes and demonstrates prompt engineering. So the six techniques below
   are not cosmetic labels over one prompt — each builds a structurally
   different prompt, and two of them (chaining, iterative refinement) run
   genuine multi-step workflows with several API calls.
   ===================================================================== */

'use strict';

/* ------------------------------------------------------------------ */
/* Configuration                                                       */
/* ------------------------------------------------------------------ */

const MODELS = [
  'gemini-2.0-flash',
  'gemini-2.0-flash-lite',
  'gemini-1.5-flash',
  'gemini-1.5-pro'
];

const API_BASE = 'https://generativelanguage.googleapis.com/v1beta/models';

const state = {
  technique: 'role',
  versions: [],       // [{technique, label, text, prompt, steps, ms}]
  activeVersion: 0,
  lastPrompt: '',
  model: MODELS[0]
};

/* ------------------------------------------------------------------ */
/* Small helpers                                                       */
/* ------------------------------------------------------------------ */

const $ = id => document.getElementById(id);
const val = id => ($(id) ? $(id).value.trim() : '');
const checked = id => ($(id) ? $(id).checked : false);

const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g,
  c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

function toast(message, kind) {
  const box = $('toastContainer');
  if (!box) return;
  const el = document.createElement('div');
  el.className = 'toast ' + (kind || '');
  el.textContent = message;
  box.appendChild(el);
  setTimeout(() => { el.style.opacity = '0'; setTimeout(() => el.remove(), 400); }, 3200);
}

function loading(on, text, sub) {
  const o = $('loadingOverlay');
  if (!o) return;
  o.style.display = on ? 'flex' : 'none';
  if (text && $('loadingText')) $('loadingText').textContent = text;
  if (sub && $('loadingSubText')) $('loadingSubText').textContent = sub;
}

function busy(on) {
  const b = $('btnGenerate');
  if (!b) return;
  b.disabled = on;
  if ($('generateText')) $('generateText').textContent = on ? 'Generating…' : 'Generate Lecture Notes';
}

/* Minimal, safe Markdown renderer. Input is escaped first, so model
   output can never inject HTML into the page. */
function mdToHtml(src) {
  const lines = esc(src).split('\n');
  let out = '', inUl = false, inOl = false, inCode = false;
  const closeLists = () => {
    if (inUl) { out += '</ul>'; inUl = false; }
    if (inOl) { out += '</ol>'; inOl = false; }
  };
  for (const raw of lines) {
    const line = raw.replace(/\s+$/, '');
    if (/^```/.test(line.trim())) {
      closeLists();
      out += inCode ? '</code></pre>' : '<pre><code>';
      inCode = !inCode;
      continue;
    }
    if (inCode) { out += line + '\n'; continue; }
    if (!line.trim()) { closeLists(); continue; }

    const h = line.match(/^(#{1,6})\s+(.*)$/);
    if (h) { closeLists(); const n = Math.min(h[1].length + 1, 6); out += `<h${n}>${inline(h[2])}</h${n}>`; continue; }
    if (/^\s*([-*_])\s*\1\s*\1[\s-*_]*$/.test(line)) { closeLists(); out += '<hr/>'; continue; }

    const ol = line.match(/^\s*\d+[.)]\s+(.*)$/);
    if (ol) { if (inUl) { out += '</ul>'; inUl = false; } if (!inOl) { out += '<ol>'; inOl = true; } out += `<li>${inline(ol[1])}</li>`; continue; }

    const ul = line.match(/^\s*[-*•]\s+(.*)$/);
    if (ul) { if (inOl) { out += '</ol>'; inOl = false; } if (!inUl) { out += '<ul>'; inUl = true; } out += `<li>${inline(ul[1])}</li>`; continue; }

    if (/^\s*\|.*\|\s*$/.test(line)) { closeLists(); out += `<p style="font-family:monospace;font-size:0.85em">${inline(line)}</p>`; continue; }

    closeLists();
    out += `<p>${inline(line)}</p>`;
  }
  closeLists();
  if (inCode) out += '</code></pre>';
  return out;
}
const inline = s => s
  .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  .replace(/(^|[^*])\*([^*]+)\*/g, '$1<em>$2</em>')
  .replace(/`([^`]+)`/g, '<code>$1</code>');

/* ------------------------------------------------------------------ */
/* API key handling — never stored in source, session only             */
/* ------------------------------------------------------------------ */

function getKey() { return sessionStorage.getItem('gemini_api_key') || ''; }

function refreshKeyDot() {
  const dot = $('apiKeyStatus');
  if (!dot) return;
  const has = !!getKey();
  dot.className = 'dot ' + (has ? 'dot-green' : 'dot-red');
  dot.title = has ? 'API key configured' : 'No API key set';
}

function openApiKeyModal() {
  if ($('apiKeyInput')) $('apiKeyInput').value = getKey();
  if ($('apiModal')) $('apiModal').classList.add('open');
}
function closeApiKeyModal() { if ($('apiModal')) $('apiModal').classList.remove('open'); }
function closeApiModalOnOverlay(e) { if (e && e.target && e.target.id === 'apiModal') closeApiKeyModal(); }

function toggleApiKeyVisibility() {
  const i = $('apiKeyInput');
  if (i) i.type = i.type === 'password' ? 'text' : 'password';
}

function saveApiKey() {
  const key = $('apiKeyInput') ? $('apiKeyInput').value.trim() : '';
  if (!key) { toast('Please enter an API key.', 'error'); return; }
  if (!/^AIza[\w-]{20,}$/.test(key)) {
    toast('That does not look like a Gemini key (expected AIza…).', 'error');
    return;
  }
  sessionStorage.setItem('gemini_api_key', key);
  refreshKeyDot();
  closeApiKeyModal();
  toast('API key saved for this browser session.', 'success');
}

/* ------------------------------------------------------------------ */
/* Gemini call                                                         */
/* ------------------------------------------------------------------ */

async function callGemini(prompt, opts) {
  const key = getKey();
  if (!key) throw new Error('No API key set. Click "API Key" in the navigation bar.');

  const cfg = Object.assign({ temperature: 0.65, maxOutputTokens: 8192 }, opts || {});
  let lastErr = null;

  // Try the preferred model, then fall back if the account lacks access.
  const order = [state.model].concat(MODELS.filter(m => m !== state.model));
  for (const model of order) {
    let res;
    try {
      res = await fetch(`${API_BASE}/${model}:generateContent?key=${encodeURIComponent(key)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ role: 'user', parts: [{ text: prompt }] }],
          generationConfig: cfg
        })
      });
    } catch (netErr) {
      throw new Error('Network error — check your internet connection.');
    }

    if (res.ok) {
      const data = await res.json();
      const cand = data.candidates && data.candidates[0];
      if (!cand) throw new Error('The API returned no content. The prompt may have been blocked.');
      if (cand.finishReason === 'SAFETY') throw new Error('Response blocked by a safety filter. Try rephrasing the topic.');
      const text = (cand.content && cand.content.parts || []).map(p => p.text || '').join('');
      if (!text.trim()) throw new Error('The API returned an empty response.');
      if (model !== state.model) { state.model = model; toast('Switched to ' + model, 'success'); }
      return text;
    }

    let detail = '';
    try { const j = await res.json(); detail = (j.error && j.error.message) || ''; } catch (e) {}

    if (res.status === 404) { lastErr = new Error(`Model ${model} unavailable.`); continue; }
    if (res.status === 400 && /API key not valid/i.test(detail))
      throw new Error('That API key was rejected. Check it at aistudio.google.com/apikey.');
    if (res.status === 403) throw new Error('Access denied (403). The key may lack permission.');
    if (res.status === 429) throw new Error('Rate limit reached (429). Wait a moment and retry.');
    if (res.status >= 500) { lastErr = new Error(`Server error ${res.status}.`); continue; }
    throw new Error(`Request failed (${res.status}). ${detail}`);
  }
  throw lastErr || new Error('All models failed. Check your API key.');
}

/* ------------------------------------------------------------------ */
/* Form -> structured spec                                             */
/* ------------------------------------------------------------------ */

const SECTIONS = [
  ['incIntro', 'Introduction and motivation'],
  ['incConcepts', 'Core concepts and definitions'],
  ['incMath', 'Mathematical formulation and derivations'],
  ['incAlgo', 'Algorithms and pseudocode'],
  ['incExamples', 'Worked numerical examples'],
  ['incCaseStudy', 'Real-world case study'],
  ['incQuiz', 'Quiz questions with answers'],
  ['incViva', 'Viva / interview questions'],
  ['incRef', 'References and further reading'],
  ['incSummary', 'Summary and key takeaways']
];

function readForm() {
  return {
    courseName: val('courseName') || 'Untitled Course',
    courseCode: val('courseCode'),
    courseOutcomes: val('courseOutcomes'),
    moduleName: val('moduleName'),
    moduleNo: val('moduleNo'),
    topic: val('topic'),
    subtopic: val('subtopic'),
    learningObj: val('learningObj'),
    bloom: val('bloomLevel') || 'Understand',
    audience: val('targetAudience') || 'Undergraduate Engineering students',
    duration: val('lectureDuration') || '1 hour',
    method: val('teachingMethod') || 'Chalk and Talk',
    sections: SECTIONS.filter(([id]) => checked(id)).map(([, label]) => label)
  };
}

function validateForm(f) {
  if (!f.topic) return 'Please enter the lecture topic.';
  if (!f.courseName || f.courseName === 'Untitled Course') return 'Please enter the course name.';
  if (!f.sections.length) return 'Select at least one section to include.';
  return null;
}

function contextBlock(f) {
  const lines = [
    `Course: ${f.courseName}${f.courseCode ? ' (' + f.courseCode + ')' : ''}`,
    f.moduleName ? `Module${f.moduleNo ? ' ' + f.moduleNo : ''}: ${f.moduleName}` : '',
    `Topic: ${f.topic}`,
    f.subtopic ? `Sub-topics: ${f.subtopic}` : '',
    f.courseOutcomes ? `Course outcomes: ${f.courseOutcomes}` : '',
    f.learningObj ? `Learning objectives: ${f.learningObj}` : '',
    `Bloom's level: ${f.bloom}`,
    `Audience: ${f.audience}`,
    `Lecture duration: ${f.duration}`,
    `Teaching method: ${f.method}`
  ].filter(Boolean);
  return lines.join('\n');
}

const sectionList = f => f.sections.map((s, i) => `${i + 1}. ${s}`).join('\n');

const HOUSE_RULES =
`Rules that apply to the whole document:
- Depth must match the Bloom's level and audience stated above; do not drift higher or lower.
- Define every technical term on first use.
- Do not invent citations, statistics, standards or author names. If a reference
  is needed and you are not certain of it, write [VERIFY: <what to check>].
- Use LaTeX-style notation for mathematics, written inline as $...$.
- Use Markdown headings, tables and fenced code blocks.
- Keep the content deliverable within the stated lecture duration.`;

/* ------------------------------------------------------------------ */
/* The six prompt engineering techniques                                */
/* ------------------------------------------------------------------ */

const TECHNIQUES = {
  role: {
    name: 'Role Prompting',
    blurb: 'Assigns an expert identity so tone, depth and priorities follow from the persona.',
    steps: 1,
    build: f => `You are a Senior Professor of Engineering with 20 years of experience teaching
${f.courseName} to ${f.audience}. You are known for lecture notes that are technically
precise, well sequenced, and genuinely usable in a classroom rather than a summary of a textbook.

Prepare standardised lecture notes for the following session.

${contextBlock(f)}

Include exactly these sections, in this order:
${sectionList(f)}

${HOUSE_RULES}

Write as the professor would write for their own class: assume the reader is a
student who has completed the prerequisites but has not seen this topic before.`
  },

  structured: {
    name: 'Structured Prompting',
    blurb: 'Delimits the request into labelled blocks so the model cannot conflate instruction with content.',
    steps: 1,
    build: f => `<task>
Generate standardised university lecture notes.
</task>

<context>
${contextBlock(f)}
</context>

<required_sections>
${sectionList(f)}
</required_sections>

<constraints>
${HOUSE_RULES}
</constraints>

<output_format>
Markdown. Begin with an H1 title, then one H2 per required section, in the order
listed. Under each H2 include the substantive content — never a placeholder.
End with a table of the key formulae or definitions introduced.
</output_format>

<quality_bar>
The notes must be usable by a different faculty member with no further editing.
Any statement a student could reasonably ask "why?" about must already carry its
justification.
</quality_bar>`
  },

  template: {
    name: 'Template Prompting',
    blurb: 'Supplies a fixed skeleton so every generated note has identical structure — the standardisation the brief asks for.',
    steps: 1,
    build: f => `Fill in the lecture-note template below for the session described. Reproduce the
template's structure exactly: same headings, same order, same tables. Replace every
{{...}} placeholder with real content and remove the braces. Add nothing outside
the template.

CONTEXT
${contextBlock(f)}

TEMPLATE
# {{Topic}} — Lecture Notes
**Course:** {{course}} | **Module:** {{module}} | **Duration:** {{duration}} | **Bloom:** {{bloom}}

## Learning Outcomes
| # | On completing this lecture the student will be able to… | Bloom |
|---|---|---|
| 1 | {{outcome}} | {{level}} |
| 2 | {{outcome}} | {{level}} |
| 3 | {{outcome}} | {{level}} |

## Prerequisites
- {{prerequisite}}

${f.sections.map(s => `## ${s}\n{{content for ${s.toLowerCase()}}}`).join('\n\n')}

## Board Plan
| Time | What the teacher writes / shows | Student activity |
|---|---|---|
| {{mm:ss}} | {{content}} | {{activity}} |

## Key Formulae and Definitions
| Term / Formula | Meaning | Where used |
|---|---|---|
| {{item}} | {{meaning}} | {{use}} |

${HOUSE_RULES}`
  },

  fewshot: {
    name: 'Few-Shot Prompting',
    blurb: 'Shows two worked exemplars so the model matches a demonstrated house style rather than guessing it.',
    steps: 1,
    build: f => `Below are two short examples of the lecture-note house style used in this
department. Study the depth, the ordering, and how each example moves from
definition to intuition to formalism to a worked case. Then write full notes for
the requested topic in the same style.

EXAMPLE 1 (fragment — Data Structures, "Hash Tables")
## Core Concept
A hash table stores key–value pairs and reaches an entry in expected O(1) time by
computing an index from the key rather than searching for it.
**Intuition:** a library that computes each book's shelf from its title, instead of
scanning every shelf.
**Formally:** for a table of size $m$ and hash function $h$, key $k$ maps to slot
$h(k) \\bmod m$. Two keys sharing a slot is a *collision*, resolved by chaining or
open addressing.
**Worked case:** inserting keys 15, 11, 27 with $h(k)=k$, $m=8$ gives slots 7, 3, 3 —
27 collides with 11 and is chained behind it.
**Common misconception:** O(1) is the *expected* cost. With a poor hash function
every key can land in one slot, degrading to O(n).

EXAMPLE 2 (fragment — Signals & Systems, "Convolution")
## Core Concept
Convolution computes the output of a linear time-invariant system as the weighted
overlap of the input with a flipped, shifted impulse response.
**Intuition:** every input sample sets off an echo; the output at any instant is the
sum of all echoes arriving then.
**Formally:** $y[n]=\\sum_{k=-\\infty}^{\\infty} x[k]\\,h[n-k]$.
**Worked case:** $x=[1,2]$, $h=[1,1]$ gives $y=[1,3,2]$ — length $2+2-1=3$.
**Common misconception:** the flip is not optional. Correlation omits it and gives a
different result for asymmetric $h$.

Notice that every concept carries: definition → intuition → formal statement →
worked case → a misconception to pre-empt. Follow that pattern.

NOW WRITE THE FULL NOTES FOR:
${contextBlock(f)}

Required sections:
${sectionList(f)}

${HOUSE_RULES}`
  },

  chain: {
    name: 'Prompt Chaining',
    blurb: 'Four dependent calls — outline, then expansion, then examples, then assessment — each constrained by the previous output.',
    steps: 4,
    build: f => `[Step 1 of 4 — outline]
Act as a curriculum designer. Produce a detailed teaching outline for:

${contextBlock(f)}

Sections to cover:
${sectionList(f)}

Return only the outline: numbered sections, the sub-points under each, and a
minute budget per section totalling ${f.duration}. No prose content yet.`,

    chain: [
      (f, prev) => `[Step 2 of 4 — expand]
Here is the approved outline for a lecture on "${f.topic}" for ${f.audience}:

${prev}

Expand every section into full lecture-note content at Bloom's level ${f.bloom}.
Follow the outline exactly — do not add, drop or reorder sections. Respect each
section's minute budget when deciding depth.

${HOUSE_RULES}`,

      (f, prev) => `[Step 3 of 4 — examples]
Here are the lecture notes so far on "${f.topic}":

${prev}

Improve them by inserting, at the right points: at least two fully worked
numerical examples with every intermediate step shown, one real-world
application relevant to ${f.audience}, and a "Common Mistakes" box listing three
errors students actually make on this topic and why each happens.

Return the complete improved notes, not a list of the additions.`,

      (f, prev) => `[Step 4 of 4 — assessment]
Here are the near-final lecture notes on "${f.topic}":

${prev}

Append an assessment section aligned to Bloom's level ${f.bloom}:
- 5 multiple-choice questions with the correct answer and a one-line explanation
- 3 short-answer questions with model answers
- 2 viva questions with the expected discussion points
- 1 assignment problem with a marking scheme

Return the complete final document with this section appended.`
    ]
  },

  iterative: {
    name: 'Iterative Refinement',
    blurb: 'Generates a draft, has the model critique it against explicit criteria, then rewrites — three calls.',
    steps: 3,
    build: f => `[Pass 1 of 3 — draft]
Write lecture notes for:

${contextBlock(f)}

Sections:
${sectionList(f)}

${HOUSE_RULES}`,

    chain: [
      (f, prev) => `[Pass 2 of 3 — critique]
You are a senior faculty reviewer on a curriculum committee. Critically review the
lecture notes below for a ${f.duration} session with ${f.audience} at Bloom's
level ${f.bloom}.

${prev}

Assess against: technical accuracy; appropriateness of depth for the stated
audience and Bloom's level; completeness of the required sections; quality and
correctness of examples; clarity of explanation; realistic fit within the stated
duration.

Return only a numbered list of specific, actionable defects. Quote the offending
text for each. Do not rewrite anything yet. If a section is genuinely sound, say
so briefly rather than inventing a criticism.`,

      (f, prev, first) => `[Pass 3 of 3 — revise]
Original lecture notes:
---
${first}
---

Reviewer's critique:
---
${prev}
---

Rewrite the notes addressing every point in the critique. Preserve what the
reviewer found sound. Return the complete revised document only — no changelog,
no commentary.

${HOUSE_RULES}`
    ]
  }
};

/* ------------------------------------------------------------------ */
/* Technique selection + live prompt preview                            */
/* ------------------------------------------------------------------ */

function selectTechnique(name, el) {
  if (!TECHNIQUES[name]) return;
  state.technique = name;
  document.querySelectorAll('.technique-btn').forEach(b => b.classList.remove('active'));
  if (el) el.classList.add('active');
  updatePromptPreview();
}

function updatePromptPreview() {
  const box = $('promptPreview');
  if (!box) return;
  const f = readForm();
  if (!f.topic) {
    box.textContent = 'Fill the form and select a technique to see the prompt here.';
    return;
  }
  const t = TECHNIQUES[state.technique];
  state.lastPrompt = t.build(f);
  const header = t.steps > 1
    ? `# ${t.name} — step 1 of ${t.steps}. Later steps are built from each step's output.\n\n`
    : `# ${t.name}\n\n`;
  box.textContent = header + state.lastPrompt;
}

function copyPrompt() {
  const text = $('promptPreview') ? $('promptPreview').textContent : '';
  if (!text.trim()) return toast('Nothing to copy yet.', 'error');
  navigator.clipboard.writeText(text)
    .then(() => toast('Prompt copied to clipboard.', 'success'))
    .catch(() => toast('Could not access the clipboard.', 'error'));
}

/* ------------------------------------------------------------------ */
/* Generation                                                          */
/* ------------------------------------------------------------------ */

async function runTechnique(techniqueKey, f, onStep) {
  const t = TECHNIQUES[techniqueKey];
  const prompts = [];
  let first = '', out = '';

  const p0 = t.build(f);
  prompts.push(p0);
  if (onStep) onStep(1, t.steps);
  out = await callGemini(p0);
  first = out;

  if (t.chain) {
    for (let i = 0; i < t.chain.length; i++) {
      if (onStep) onStep(i + 2, t.steps);
      const p = t.chain[i](f, out, first);
      prompts.push(p);
      out = await callGemini(p);
    }
  }
  return { text: out, prompts };
}

async function generateNotes() {
  const f = readForm();
  const problem = validateForm(f);
  if (problem) return toast(problem, 'error');
  if (!getKey()) { openApiKeyModal(); return toast('Set your Gemini API key first.', 'error'); }

  const t = TECHNIQUES[state.technique];
  busy(true);
  loading(true, 'Generating lecture notes…', `${t.name} — step 1 of ${t.steps}`);
  const t0 = performance.now();

  try {
    const res = await runTechnique(state.technique, f, (step, total) => {
      loading(true, 'Generating lecture notes…',
        `${t.name} — step ${step} of ${total}`);
    });
    const ms = performance.now() - t0;
    state.versions = [{
      technique: state.technique, label: t.name, text: res.text,
      prompts: res.prompts, ms: ms
    }];
    state.activeVersion = 0;
    renderOutput(f);
    toast(`Notes generated with ${t.name}.`, 'success');
  } catch (err) {
    toast(err.message, 'error');
  } finally {
    loading(false);
    busy(false);
  }
}

async function generateAllVersions() {
  const f = readForm();
  const problem = validateForm(f);
  if (problem) return toast(problem, 'error');
  if (!getKey()) { openApiKeyModal(); return toast('Set your Gemini API key first.', 'error'); }

  const keys = Object.keys(TECHNIQUES);
  const totalCalls = keys.reduce((n, k) => n + TECHNIQUES[k].steps, 0);
  if (!confirm(`Compare all 6 techniques?\n\nThis makes ${totalCalls} API calls and may take a few minutes.`)) return;

  busy(true);
  state.versions = [];
  let done = 0;

  for (const key of keys) {
    const t = TECHNIQUES[key];
    try {
      const t0 = performance.now();
      const res = await runTechnique(key, f, (step, total) => {
        loading(true, `Technique ${keys.indexOf(key) + 1} of 6 — ${t.name}`,
          `step ${step} of ${total} · ${done} of ${totalCalls} calls complete`);
      });
      done += t.steps;
      state.versions.push({
        technique: key, label: t.name, text: res.text,
        prompts: res.prompts, ms: performance.now() - t0
      });
    } catch (err) {
      toast(`${t.name} failed: ${err.message}`, 'error');
    }
  }

  loading(false);
  busy(false);
  if (!state.versions.length) return toast('All techniques failed.', 'error');
  state.activeVersion = 0;
  renderOutput(f);
  renderComparison(f);
  toast(`Generated ${state.versions.length} versions. See Technique Comparison.`, 'success');
  const c = $('comparison');
  if (c) c.scrollIntoView({ behavior: 'smooth' });
}

async function regenerateNotes() {
  if (!state.versions.length) return toast('Generate notes first.', 'error');
  return generateNotes();
}

async function refineNotes() {
  const feedback = val('refineFeedback');
  if (!feedback) return toast('Enter feedback describing what to improve.', 'error');
  if (!state.versions.length) return toast('Generate notes first.', 'error');

  const f = readForm();
  const current = state.versions[state.activeVersion];
  const prompt = `Here are existing lecture notes on "${f.topic}" for ${f.audience}:

---
${current.text}
---

The faculty member reviewing these notes asks for the following changes:
"${feedback}"

Apply exactly those changes. Do not alter anything the feedback did not ask about,
and do not reduce technical accuracy to satisfy a request for simplicity — if a
requested change would make something wrong, keep it correct and add a note
explaining the tension.

Return the complete revised notes.

${HOUSE_RULES}`;

  busy(true);
  loading(true, 'Refining lecture notes…', 'Applying your feedback');
  try {
    const t0 = performance.now();
    const text = await callGemini(prompt);
    state.versions.push({
      technique: current.technique,
      label: current.label + ' + refinement ' + (state.versions.length),
      text: text, prompts: [prompt], ms: performance.now() - t0
    });
    state.activeVersion = state.versions.length - 1;
    renderOutput(f);
    if ($('refineFeedback')) $('refineFeedback').value = '';
    toast('Notes refined.', 'success');
  } catch (err) {
    toast(err.message, 'error');
  } finally {
    loading(false); busy(false);
  }
}

async function regenerateCustom() {
  const custom = val('customPromptArea');
  if (!custom) return toast('Write a custom prompt first.', 'error');
  if (!getKey()) { openApiKeyModal(); return toast('Set your Gemini API key first.', 'error'); }

  busy(true);
  loading(true, 'Generating from your custom prompt…', 'Full manual control');
  try {
    const t0 = performance.now();
    const text = await callGemini(custom);
    state.versions.push({
      technique: 'custom', label: 'Custom prompt',
      text: text, prompts: [custom], ms: performance.now() - t0
    });
    state.activeVersion = state.versions.length - 1;
    renderOutput(readForm());
    toast('Generated from your custom prompt.', 'success');
  } catch (err) {
    toast(err.message, 'error');
  } finally {
    loading(false); busy(false);
  }
}

/* ------------------------------------------------------------------ */
/* Rendering                                                           */
/* ------------------------------------------------------------------ */

function renderOutput(f) {
  const sec = $('outputSection');
  if (!sec) return;
  sec.style.display = 'block';

  const v = state.versions[state.activeVersion];
  const words = v.text.trim().split(/\s+/).length;

  if ($('outputMeta')) {
    $('outputMeta').textContent =
      `${f.topic} · ${v.label} · ${words} words · ${(v.ms / 1000).toFixed(1)}s · ` +
      `${v.prompts.length} API call${v.prompts.length > 1 ? 's' : ''} · ${state.model}`;
  }

  const tabs = $('versionTabs');
  if (tabs) {
    tabs.innerHTML = state.versions.length > 1
      ? state.versions.map((ver, i) =>
        `<button class="version-tab${i === state.activeVersion ? ' active' : ''}" data-v="${i}">${esc(ver.label)}</button>`).join('')
      : '';
    tabs.querySelectorAll('.version-tab').forEach(b => {
      b.onclick = () => { state.activeVersion = +b.dataset.v; renderOutput(f); };
    });
  }

  if ($('outputContent')) $('outputContent').innerHTML = mdToHtml(v.text);
  if ($('refinePanel')) $('refinePanel').style.display = 'block';
  if ($('customPromptArea') && !$('customPromptArea').value.trim()) {
    $('customPromptArea').value = v.prompts[v.prompts.length - 1];
  }
  sec.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function renderComparison(f) {
  const grid = $('comparisonGrid');
  if (!grid) return;
  if (!state.versions.length) {
    grid.innerHTML = '<div class="empty-state"><div class="empty-icon">&#128202;</div>' +
      '<p>Run "Compare All Techniques" to see every technique side by side.</p></div>';
    return;
  }
  grid.innerHTML = state.versions.map((v, i) => {
    const words = v.text.trim().split(/\s+/).length;
    const t = TECHNIQUES[v.technique];
    const preview = v.text.replace(/[#*`|>]/g, '').replace(/\s+/g, ' ').slice(0, 320);
    return `<div class="comparison-card card">
      <h3 class="card-title">${esc(v.label)}</h3>
      <p class="card-sub">${esc(t ? t.blurb : 'User-supplied prompt.')}</p>
      <div class="comp-content">
        <p style="font-size:0.8rem;opacity:0.75">
          ${words} words &middot; ${v.prompts.length} API call${v.prompts.length > 1 ? 's' : ''}
          &middot; ${(v.ms / 1000).toFixed(1)}s
        </p>
        <p style="font-size:0.85rem">${esc(preview)}…</p>
        <button class="btn-secondary btn-sm" data-view="${i}">View full notes</button>
      </div>
    </div>`;
  }).join('');
  grid.querySelectorAll('[data-view]').forEach(b => {
    b.onclick = () => { state.activeVersion = +b.dataset.view; renderOutput(readForm()); };
  });
}

/* ------------------------------------------------------------------ */
/* Output actions                                                      */
/* ------------------------------------------------------------------ */

function copyOutput() {
  if (!state.versions.length) return toast('Nothing to copy yet.', 'error');
  navigator.clipboard.writeText(state.versions[state.activeVersion].text)
    .then(() => toast('Lecture notes copied.', 'success'))
    .catch(() => toast('Could not access the clipboard.', 'error'));
}

function exportPDF() {
  if (!state.versions.length) return toast('Generate notes first.', 'error');
  const f = readForm();
  const v = state.versions[state.activeVersion];
  const w = window.open('', '_blank');
  if (!w) return toast('Pop-up blocked — allow pop-ups to export.', 'error');
  w.document.write(`<!DOCTYPE html><html><head><meta charset="utf-8">
    <title>${esc(f.topic)} — Lecture Notes</title><style>
    body{font-family:Georgia,'Times New Roman',serif;max-width:760px;margin:36px auto;
         padding:0 20px;line-height:1.6;color:#111}
    h1{font-size:24px;border-bottom:2px solid #1f3864;padding-bottom:8px;color:#1f3864}
    h2{font-size:18px;margin-top:26px;color:#1f3864}
    h3{font-size:15px;margin-top:18px}
    table{border-collapse:collapse;width:100%;margin:12px 0;font-size:13px}
    th,td{border:1px solid #bbb;padding:6px 9px;text-align:left}
    th{background:#1f3864;color:#fff}
    pre{background:#f4f4f2;padding:10px;border-radius:6px;overflow:auto;font-size:12px}
    code{background:#f0f0ee;padding:1px 4px;border-radius:3px;font-size:0.92em}
    .meta{color:#555;font-size:12px;border-bottom:1px solid #ddd;padding-bottom:10px;margin-bottom:18px}
    @media print{body{margin:0}}
    </style></head><body>
    <div class="meta"><strong>${esc(f.courseName)}</strong>${f.courseCode ? ' (' + esc(f.courseCode) + ')' : ''}
      &middot; ${esc(f.audience)} &middot; ${esc(f.duration)} &middot; Bloom: ${esc(f.bloom)}<br/>
      Generated with ${esc(v.label)} &middot; ${new Date().toLocaleString()}</div>
    ${mdToHtml(v.text)}</body></html>`);
  w.document.close();
  setTimeout(() => w.print(), 400);
  toast('Print dialog opened — choose "Save as PDF".', 'success');
}

/* ------------------------------------------------------------------ */
/* History (localStorage)                                              */
/* ------------------------------------------------------------------ */

const HKEY = 'lectureai_history';
const loadHistory = () => { try { return JSON.parse(localStorage.getItem(HKEY)) || []; } catch (e) { return []; } };
const storeHistory = h => localStorage.setItem(HKEY, JSON.stringify(h.slice(0, 30)));

function saveToHistory() {
  if (!state.versions.length) return toast('Generate notes first.', 'error');
  const f = readForm();
  const v = state.versions[state.activeVersion];
  const h = loadHistory();
  h.unshift({
    id: Date.now(), topic: f.topic, course: f.courseName, technique: v.label,
    bloom: f.bloom, audience: f.audience, words: v.text.trim().split(/\s+/).length,
    date: new Date().toLocaleString(), text: v.text
  });
  storeHistory(h);
  renderHistory();
  toast('Saved to history.', 'success');
}

function renderHistory() {
  const box = $('historyContainer');
  if (!box) return;
  const h = loadHistory();
  if (!h.length) {
    box.innerHTML = '<div class="empty-state"><div class="empty-icon">&#128194;</div>' +
      '<p>No saved notes yet. Generate and save lecture notes to see them here.</p></div>';
    return;
  }
  box.innerHTML = h.map(item => `
    <div class="history-item">
      <div class="history-item-info">
        <div class="history-item-title">${esc(item.topic)}</div>
        <div class="history-item-meta">
          ${esc(item.course)} &middot; ${esc(item.technique)} &middot; Bloom: ${esc(item.bloom)}
          &middot; ${item.words} words &middot; ${esc(item.date)}
        </div>
      </div>
      <div class="history-item-actions">
        <button class="btn-secondary btn-sm" data-load="${item.id}">Open</button>
        <button class="btn-secondary btn-sm" data-del="${item.id}">Delete</button>
      </div>
    </div>`).join('');

  box.querySelectorAll('[data-load]').forEach(b => {
    b.onclick = () => {
      const item = loadHistory().find(x => x.id === +b.dataset.load);
      if (!item) return;
      state.versions.push({
        technique: 'history', label: item.technique + ' (saved)',
        text: item.text, prompts: ['(loaded from history)'], ms: 0
      });
      state.activeVersion = state.versions.length - 1;
      renderOutput(readForm());
      toast('Loaded from history.', 'success');
    };
  });
  box.querySelectorAll('[data-del]').forEach(b => {
    b.onclick = () => {
      storeHistory(loadHistory().filter(x => x.id !== +b.dataset.del));
      renderHistory();
      toast('Deleted.', 'success');
    };
  });
}

/* ------------------------------------------------------------------ */
/* Init                                                                */
/* ------------------------------------------------------------------ */

document.addEventListener('DOMContentLoaded', () => {
  refreshKeyDot();
  renderHistory();
  renderComparison(readForm());

  // Live prompt preview as the form changes
  const form = $('lectureForm');
  if (form) {
    form.addEventListener('input', updatePromptPreview);
    form.addEventListener('change', updatePromptPreview);
    form.addEventListener('submit', e => { e.preventDefault(); generateNotes(); });
  }

  if ($('apiKeyInput')) {
    $('apiKeyInput').addEventListener('keydown', e => { if (e.key === 'Enter') saveApiKey(); });
  }
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeApiKeyModal(); });

  updatePromptPreview();

  if (!getKey()) {
    setTimeout(() => toast('Set your Gemini API key to start generating.', ''), 700);
  }
});

/* Expose the functions index.html calls through inline onclick handlers. */
Object.assign(window, {
  openApiKeyModal, closeApiKeyModal, closeApiModalOnOverlay, toggleApiKeyVisibility,
  saveApiKey, selectTechnique, copyPrompt, generateNotes, generateAllVersions,
  copyOutput, exportPDF, saveToHistory, regenerateNotes, refineNotes, regenerateCustom
});
