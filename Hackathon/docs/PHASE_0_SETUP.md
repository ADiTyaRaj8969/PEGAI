<div align="center">

# Phase 0 · Setup

[![Time](https://img.shields.io/badge/11%3A00%20–%2011%3A15-0b3d62?style=flat-square)](#)
[![Prompts](https://img.shields.io/badge/prompts-none-6b7684?style=flat-square)](#)
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
google-generativeai>=0.8      # swap for your provider
```

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
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.0-flash
GOOGLE_API_KEY=your_key_here
```

## `tutor/llm.py`

One function, so no other module ever imports a vendor SDK. Swapping providers is then a one-file
change — worth the ten minutes when a quota runs out mid-demo.

```python
import os, json
from dotenv import load_dotenv

load_dotenv()

class LLMError(Exception):
    """Raised for any provider failure; caught by the UI (FR-6.6)."""

def complete(prompt: str, *, system: str = "", json_mode: bool = False,
             temperature: float = 0.2, max_tokens: int = 1200) -> str:
    """Send one prompt, return raw text. The only place a vendor SDK appears."""
    provider = os.getenv("LLM_PROVIDER", "gemini")
    try:
        if provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
            model = genai.GenerativeModel(
                os.getenv("LLM_MODEL", "gemini-2.0-flash"),
                system_instruction=system or None,
            )
            cfg = {"temperature": temperature, "max_output_tokens": max_tokens}
            if json_mode:
                cfg["response_mime_type"] = "application/json"
            return model.generate_content(prompt, generation_config=cfg).text
        raise LLMError(f"Unknown provider: {provider}")
    except KeyError:
        raise LLMError("API key missing. Copy .env.example to .env and add your key.")
    except Exception as e:
        raise LLMError(f"Model call failed: {e}") from e


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

### Two details that save time later

**`temperature=0.2` everywhere.** Low but not zero. The evaluation in Phase 8 compares V1 against
V2, and that comparison is only meaningful if the randomness is held down (NFR-7).

**`complete_json` strips fences and surrounding prose.** Models wrap JSON in ` ```json ` fences
even when told not to. Handling it in one place means Phases 2, 3, 4 and 6 never deal with it.

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
