# Epic 69: Free External Candidate Registry

## Context

The benchmark-first policy now allows free external APIs and services when they can improve product output quality. That rule must be auditable across the whole project, including candidates that were previously classified as external-only future research.

## Goal

Create a canonical registry for free external benchmark paths, generate evidence from it, and let the ranked value queue include only those external candidates whose no-cost benchmark path is explicitly documented.

## Scope

- Add a registry for free external candidates and candidates that still need free-tier or terms verification.
- Add a script that compares the registry with the generated candidate catalog.
- Integrate the review into `prove_final_product.py --quick`.
- Let `rank_value_candidates.py` consume the review so eligible free external candidates enter the ranking.
- Add focused unit tests.

## Non-goals

- Do not claim a currently available free API tier without explicit verification.
- Do not promote any external candidate to runtime from registry metadata alone.
- Do not execute network calls or external APIs in local proof.

## Validation

- `pytest` for the registry review and ranked value queue.
- Focused `ruff` and `black --check`.
- Regenerate evidence pack.
- Run quick final proof with live collection skipped.
