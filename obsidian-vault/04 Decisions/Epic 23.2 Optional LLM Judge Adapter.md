# Epic 23.2 Optional LLM Judge Adapter

## Decision

The LLM judge interface is optional, experimental, and disabled by default. Epic
23.2 implements only a deterministic offline null provider.

## Rationale

The project needs a place to attach future semantic assessment of faithfulness,
groundedness, completeness, uncertainty honesty, and executive usefulness without
weakening the existing deterministic quality gates.

## Consequences

- CI continues to depend only on deterministic checks and JUnit XML.
- Missing judge reports are informational and do not create warnings or failures.
- Real providers must be added by a future explicit plan.
- Judge scores are for human review, not source-of-truth claims.
