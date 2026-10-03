<div align="center">

# Phase 0 · Setup

[![Time](https://img.shields.io/badge/11%3A00%20–%2011%3A15-0b3d62?style=flat-square)](#)
[![Prompts](https://img.shields.io/badge/prompts-none-6b7684?style=flat-square)](#)
[![Provider](https://img.shields.io/badge/provider-OpenRouter-1a7f64?style=flat-square)](#)
[![Cost](https://img.shields.io/badge/cost-free%20tier-2d7a2d?style=flat-square)](#)
[![Blocks](https://img.shields.io/badge/blocks-everything-b35309?style=flat-square)](#)

</div>

---

## Goal

Every team member can get a response from the same model on their own machine, and the repo is
ready to receive commits.

## Tasks

| # | Task | Output |
|---|---|---|
| 0.1 | `git init`, commit the docs, push | Repo live |
| 0.2 | `requirements.txt` | Installs clean |
| 0.3 | `.env.example` + `.gitignore` | No key in git |
| 0.4 | `tutor/llm.py` adapter + smoke test | Model responds |
| 0.5 | Open [PROMPT_HISTORY.md](PROMPT_HISTORY.md) with the 11:00 entry | Log running |

## Files

```
Hackathon/
├── app.py                  # Phase 5
├── requirements.txt
├── .env.example
├── .gitignore
├── tutor/
│   ├── __init__.py
│   ├── llm.py              # Phase 0  ← this phase
│   ├── prompts.py          # Phases 1,2,3,4,6
│   ├── solver.py           # Phase 2
│   ├── hints.py            # Phase 3
│   ├── guard.py            # Phase 4
│   └── diagnose.py         # Phase 6
├── eval/
│   ├── cases.json          # Phase 8
│   └── run_eval.py         # Phase 8
└── docs/
```

## `requirements.txt`

```
streamlit>=1.30
python-dotenv>=1.0
openai>=1.40                  # OpenRouter exposes an OpenAI-compatible API
```

> [!NOTE]
> We call **OpenRouter**, using the model `inclusionai/ling-3.1-flash`. OpenRouter's API is
> OpenAI-compatible, so the official `openai` package is the client — only the `base_url` and the
> key differ. No provider-specific SDK is needed.
>
> That model is **free**: OpenRouter lists it at $0 per token for both prompt and completion,
> with a 262k context window.

## `.gitignore`

```
.env
__pycache__/
*.pyc
.streamlit/secrets.toml
eval/results_*.json
```

> `.env` on the first line. A leaked API key in a public hackathon repo is the one mistake that
> cannot be undone by a later commit.

## `.env.example`

```
LLM_PROVIDER=openrouter
LLM_MODEL=inclusionai/ling-3.1-flash
OPENROUTER_API_KEY=your_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

> [!CAUTION]
> `.env` holds a live API key and is git-ignored. Never commit it, and never paste a key into
> `.env.example`, a doc, or a chat window. If a key is ever exposed, rotate it at
> [openrouter.ai/keys](https://openrouter.ai/keys).

> [!IMPORTANT]
> `LLM_MODEL` is read from the environment precisely so swapping models is a one-line fix in
> `.env`, not a code change. If the free model is rate-limited during the run, any other
> OpenRouter model ID drops in — look for a `:free` suffix to stay at zero cost.

## `tutor/llm.py`

One function, so no other module ever imports a vendor SDK. Swapping providers is then a one-file
change — worth the ten minutes when a quota runs out mid-demo.

```python
import os, json, time, random

try:                                 # convenience only — env vars may be set directly
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# The free pool is shared, so 429s from the upstream provider are routine and
# transient. Retrying costs a few seconds; not retrying costs the demo.
RETRY_STATUS = {408, 409, 429, 500, 502, 503, 504}
MAX_ATTEMPTS = 5


class LLMError(Exception):
    """Raised for any provider failure; caught by the UI (FR-6.6)."""


class _Transient(Exception):
    """Internal: a failure worth retrying. Never escapes this module."""


def _client():
    """OpenRouter speaks the OpenAI wire format, so the openai client works unchanged."""
    from openai import OpenAI
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise LLMError("OPENROUTER_API_KEY missing. Copy .env.example to .env and add your key.")
    return OpenAI(api_key=key, base_url=os.getenv("OPENROUTER_BASE_URL", OPENROUTER_BASE_URL))


def complete(prompt: str, *, system: str = "", json_mode: bool = False,
             temperature: float = 0.2, max_tokens: int = 1200) -> str:
    """Send one prompt, return raw text. The only place a vendor SDK appears."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    # ling-3.1-flash rejects response_format (no structured-outputs support), so JSON
    # is requested in the prompt and parsed tolerantly by complete_json().
    # It is also a reasoning model: thinking tokens eat into max_tokens and can leave the
    # reply empty, so thinking is switched off. Step-by-step work lives in the prompts.
    extra = {"extra_body": {"reasoning": {"enabled": False}}}

    last = None
    for attempt in range(MAX_ATTEMPTS):
        try:
            r = _client().chat.completions.create(
                model=os.getenv("LLM_MODEL", "inclusionai/ling-3.1-flash"),
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **extra,
            )
            choice = r.choices[0]
            text = choice.message.content or ""
            if not text.strip() or choice.finish_reason == "length":
                # Transient on a shared pool — worth another go before failing.
                raise _Transient("empty or truncated reply")
            return text

        except LLMError:
            raise                                # missing key etc. — don't retry
        except _Transient as e:
            last = e
        except Exception as e:
            if getattr(e, "status_code", None) not in RETRY_STATUS:
                raise LLMError(f"Model call failed: {e}") from e
            last = e

        if attempt < MAX_ATTEMPTS - 1:           # 1s, 2s, 4s, 8s + jitter
            time.sleep(2 ** attempt + random.uniform(0, 0.5))

    raise LLMError(
        f"The model is rate-limited or unavailable after {MAX_ATTEMPTS} attempts. "
        f"Wait a moment and try again, or set LLM_MODEL to another OpenRouter model. "
        f"Last error: {last}"
    )


def complete_json(prompt: str, *, system: str = "", temperature: float = 0.2) -> dict:
    """complete() plus tolerant JSON parsing. Raises ValueError on unparseable output."""
    raw = complete(prompt, system=system, json_mode=True, temperature=temperature)
    text = raw.strip()
    if text.startswith("```"):                      # strip markdown fences
        text = text.split("```")[1].removeprefix("json").strip()
    start, end = text.find("{"), text.rfind("}")    # tolerate prose around the object
    if start == -1 or end == -1:
        raise ValueError(f"No JSON object in model output: {raw[:200]}")
    return json.loads(text[start:end + 1])
```



### Three details that save time later

**`temperature=0.2` everywhere.** Low but not zero. The evaluation in Phase 8 compares V1 against
V2, and that comparison is only meaningful if the randomness is held down (NFR-7).

**`complete_json` strips fences and surrounding prose.** Models wrap JSON in ` ```json ` fences
even when told not to. Handling it in one place means Phases 2, 3, 4 and 6 never deal with it.

**There is no JSON mode — the prompts carry it alone.** `ling-3.1-flash` rejects
`response_format` with a 400 (*"does not support structured-outputs"*), so that parameter is gone.
Nothing enforces valid JSON at the API level: the wording *"return ONLY a JSON object"* in every
prompt from Phase 2 onward is now the only thing producing parseable output, backed by
`complete_json`'s tolerant parsing and Phase 2's repair retry.

> [!WARNING]
> Do not edit that wording out of any prompt, and do not weaken the schema blocks. With
> `response_format` unavailable they are load-bearing, not decorative.

**Reasoning is switched off.** `ling-3.1-flash` is a reasoning model, and thinking tokens count
against `max_tokens` — enough of them and the reply comes back empty. `complete()` disables
reasoning and raises on an empty or truncated response rather than returning `""` for a caller to
trip over. The step-by-step work we actually want lives in the prompts, not in hidden thinking.

## Smoke Test

```bash
python -c "from tutor.llm import complete; print(complete('Reply with the single word: ready'))"
```

## Exit Criteria

- [ ] Every member runs the smoke test successfully on their own machine
- [ ] `git status` shows `.env` as ignored, not untracked
- [ ] [PROMPT_HISTORY.md](PROMPT_HISTORY.md) has the 11:00 entry committed
- [ ] Function signatures in [SRS.md](SRS.md) §3.2–3.3 agreed, so the three tracks can split

---

<div align="center">

[Index](PHASES_INDEX.md) · [Phase 1 · V1 Baseline →](PHASE_1_BASELINE.md)

</div>
