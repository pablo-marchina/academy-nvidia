# Epic 67 - Free External API Value Policy

## Goal

Update the benchmark-first selection policy so the project chooses the technology or tool that generates the most output value, including free external APIs when they are reproducible, compliant, and do not require paid credentials.

## Scope

- Document that local-first is not an absolute preference.
- Allow free external APIs/services in benchmark ranking when the candidate metadata says they are free, public, no-cost, or do not require paid credentials.
- Keep paid SaaS, hardware-only, licensed, or unavailable credential candidates blocked/future research until direct access exists.
- Keep local tests reproducible: external-free candidates may be benchmark candidates, but product tests still need local skips/null providers or explicit environment-blocked evidence.
- Add tests proving free external candidates enter the ranked queue while paid/credentialed candidates remain excluded.

## Non-Goals

- No live external API calls in unit tests.
- No credential commits.
- No automatic runtime promotion.
- No broad recataloging in this increment.

## Validation

- Focused pytest for ranking policy.
- Focused black/ruff on touched files.
- Quick proof if ranking changes remain compatible.
