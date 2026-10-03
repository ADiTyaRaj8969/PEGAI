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
