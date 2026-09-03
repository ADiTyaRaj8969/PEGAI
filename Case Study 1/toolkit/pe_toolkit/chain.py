"""Phase 10 - the seven-step investigation chain.

The point of chaining rather than asking one large question is that each step
narrows what the next one is allowed to do. Step 3 may only extract claims from
the sources step 2 found; step 7 may only use material that survived step 5.
A single prompt cannot enforce that, because nothing stops the model from
quietly reintroducing a claim it invented earlier in the same response.

Each step's output is written to `transcripts/` so the chain is auditable
after the fact - which is the difference between a workflow and a black box.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import datastore, prompts
from .llm import Runner, Turn


@dataclass
class ChainResult:
    turns: list[Turn] = field(default_factory=list)

    @property
    def total_tokens(self) -> tuple[int, int]:
        return (
            sum(t.input_tokens for t in self.turns),
            sum(t.output_tokens for t in self.turns),
        )

    def by_key(self, key: str) -> Turn | None:
        return next((t for t in self.turns if t.key == key), None)


def _sources_block() -> str:
    frame = datastore.sources()
    return "\n".join(
        f"{row['id']} [{row['source_type']}] {row['title']} "
        f"- {row['publisher']} ({row['pub_date']}) - {row['url']}"
        for _, row in frame.iterrows()
    )


def _claims_block() -> str:
    frame = datastore.claims()
    return "\n".join(
        f"{row['id']}: {row['claim']}  [sources: {row['source_ids']}]"
        for _, row in frame.iterrows()
    )


def _verified_block() -> str:
    """Only what survived verification is allowed into the final synthesis."""
    frame = datastore.claims()
    kept = frame[frame["verdict"].str.startswith(("Verified", "Partially"))]
    return "\n".join(
        f"{row['id']} [{row['verdict']}, {row['confidence']}% confidence] "
        f"{row['claim']}  [sources: {row['source_ids']}]"
        for _, row in kept.iterrows()
    )


def run(runner: Runner | None = None, *, claim: str | None = None) -> ChainResult:
    """Execute all seven steps, threading each output into the next."""
    runner = runner or Runner()
    result = ChainResult()

    claim = claim or datastore.claims().iloc[4]["claim"]  # C05, the 500 ml claim

    # Step 1 - scope the debate.
    result.turns.append(
        runner.run("chain_1_topic", prompts.P_CHAIN_TOPIC.rendered())
    )

    # Step 2 - find primary sources.
    result.turns.append(
        runner.run("chain_2_sources", prompts.P_CHAIN_SOURCES.rendered())
    )

    # Step 3 - extract atomic claims from those sources.
    result.turns.append(
        runner.run(
            "chain_3_claims",
            prompts.P_CHAIN_CLAIMS.rendered(sources=_sources_block()),
        )
    )

    # Step 4 - find where the claims collide.
    result.turns.append(
        runner.run(
            "chain_4_contradictions",
            prompts.P_CHAIN_CONTRADICTIONS.rendered(claims=_claims_block()),
        )
    )

    # Step 5 - verify one contested claim under ReAct.
    result.turns.append(
        runner.run(
            "chain_5_verify",
            prompts.P_CHAIN_VERIFY.rendered(claim=claim),
        )
    )

    # Step 6 - assess the sources themselves.
    result.turns.append(
        runner.run(
            "chain_6_bias",
            prompts.P_CHAIN_BIAS.rendered(sources=_sources_block()),
        )
    )

    # Step 7 - synthesise, using only what survived step 5.
    result.turns.append(
        runner.run(
            "chain_7_report",
            prompts.P_CHAIN_REPORT.rendered(
                verified=_verified_block(),
                guardrail=prompts.GUARDRAIL,
            ),
        )
    )

    return result


def workflow_table() -> list[dict[str, str]]:
    """The Phase 10 table, built from the prompt library so it cannot drift."""
    objectives = [
        "Topic Understanding",
        "Source Extraction",
        "Claim Identification",
        "Contradiction Detection",
        "Fact Verification",
        "Bias Analysis",
        "Final Report Generation",
    ]
    return [
        {
            "Step": str(i),
            "Objective": objective,
            "Technique": spec.technique,
            "Prompt used": spec.text,
        }
        for i, (objective, spec) in enumerate(zip(objectives, prompts.CHAIN), start=1)
    ]
