"""Claude client used to execute the prompt chain.

Two modes:

  live     - calls the Messages API. Requires credentials (an exported
             ANTHROPIC_API_KEY, or a profile from `ant auth login`; the SDK
             resolves both from the zero-argument constructor).
  replay   - reads the recorded run from `transcripts/`. This is the default
             when no credentials are present, so the pipeline and the report
             can be regenerated on any machine without spending tokens and
             without the evidence base changing underneath the document.

Replay is not a stub. The transcripts are the actual outputs the study was
written from, and re-running live will produce different text - which is
itself worth knowing, and is why the model is pinned rather than aliased.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

import anthropic

from .config import CLAUDE_MODEL, TRANSCRIPTS


class ReplayMissing(RuntimeError):
    """No recorded transcript for this step and no credentials to make one."""


@dataclass
class Turn:
    """One executed prompt and its response."""

    key: str
    prompt: str
    response: str
    mode: str
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def slug(self) -> str:
        return re.sub(r"[^a-z0-9]+", "_", self.key.lower()).strip("_")


def credentials_available() -> bool:
    """True if the SDK will find a credential without us supplying one."""
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        return True
    profile = Path.home() / ".config" / "anthropic"
    return profile.is_dir() and any(profile.iterdir())


class Runner:
    """Executes prompts, live or from the recorded run."""

    def __init__(self, *, mode: str = "auto", transcripts: Path | None = None):
        self.transcripts = transcripts or TRANSCRIPTS
        self.transcripts.mkdir(parents=True, exist_ok=True)

        if mode == "auto":
            mode = "live" if credentials_available() else "replay"
        if mode not in {"live", "replay"}:
            raise ValueError(f"mode must be 'live' or 'replay', got {mode!r}")

        self.mode = mode
        self._client = anthropic.Anthropic() if mode == "live" else None

    # -- public ------------------------------------------------------------

    def run(self, key: str, prompt: str, *, system: str | None = None) -> Turn:
        if self.mode == "replay":
            return self._replay(key, prompt)
        return self._live(key, prompt, system=system)

    # -- internals ---------------------------------------------------------

    def _path(self, key: str) -> Path:
        slug = re.sub(r"[^a-z0-9]+", "_", key.lower()).strip("_")
        return self.transcripts / f"{slug}.md"

    def _replay(self, key: str, prompt: str) -> Turn:
        path = self._path(key)
        if not path.exists():
            raise ReplayMissing(
                f"no transcript at {path}. Set ANTHROPIC_API_KEY (or run "
                f"`ant auth login`) and re-run with mode='live' to record one."
            )
        body = path.read_text(encoding="utf-8")
        # Transcripts store the prompt and the response either side of a rule
        # so the file is readable on its own as evidence.
        _, _, response = body.partition("\n---\n")
        return Turn(key=key, prompt=prompt, response=(response or body).strip(), mode="replay")

    def _live(self, key: str, prompt: str, *, system: str | None) -> Turn:
        assert self._client is not None

        kwargs = {
            "model": CLAUDE_MODEL,
            "max_tokens": 64000,
            # Adaptive thinking: these are multi-step verification prompts and
            # the reasoning quality is the point of the exercise.
            "thinking": {"type": "adaptive", "display": "summarized"},
            "output_config": {"effort": "high"},
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system

        try:
            # Streaming because max_tokens is large; get_final_message() gives
            # the assembled response without hand-rolling event handling.
            with self._client.messages.stream(**kwargs) as stream:
                message = stream.get_final_message()
        except anthropic.AuthenticationError:
            raise RuntimeError(
                "Credentials rejected. Check ANTHROPIC_API_KEY or run "
                "`ant auth status`."
            ) from None
        except anthropic.RateLimitError as exc:
            retry = exc.response.headers.get("retry-after", "60")
            raise RuntimeError(f"Rate limited; retry after {retry}s.") from None
        except anthropic.APIStatusError as exc:
            raise RuntimeError(f"API error {exc.status_code}: {exc.message}") from None
        except anthropic.APIConnectionError:
            raise RuntimeError("Network error reaching the Claude API.") from None

        if message.stop_reason == "refusal":
            detail = getattr(message.stop_details, "category", None)
            raise RuntimeError(f"Request declined by the model (category: {detail}).")

        text = "\n".join(b.text for b in message.content if b.type == "text").strip()

        turn = Turn(
            key=key,
            prompt=prompt,
            response=text,
            mode="live",
            input_tokens=message.usage.input_tokens,
            output_tokens=message.usage.output_tokens,
        )
        self._record(turn)
        return turn

    def _record(self, turn: Turn) -> None:
        """Write the transcript so a live run becomes tomorrow's replay."""
        self._path(turn.key).write_text(
            f"# {turn.key}\n\n"
            f"Model: `{CLAUDE_MODEL}`  \n"
            f"Tokens: {turn.input_tokens} in / {turn.output_tokens} out\n\n"
            f"## Prompt\n\n```\n{turn.prompt}\n```\n"
            f"\n---\n"
            f"{turn.response}\n",
            encoding="utf-8",
        )
