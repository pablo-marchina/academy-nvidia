# Epic 23 Answer Quality Evaluation

**Date:** 2026-06-11
**Decision:** Use deterministic offline answer quality gates before any optional
LLM judge.

## Context

The project already evaluates RAG retrieval and pipeline golden outputs, but did
not separately evaluate whether final Action Brief answers preserve evidence,
uncertainty, RAG citations, and recommendation invariants.

## Decision

Implement answer quality as a pure evaluator over `StartupActionBrief` plus
versioned golden expectations. CI remains offline and deterministic. LLM judge
dimensions such as faithfulness, groundedness, relevancy, completeness, and
honesty are documented for future optional use, but not implemented as blocking
CI behavior.

## Consequences

- Regressions in final answer structure and grounding can be caught without
  external calls.
- Unsupported-claim detection is pattern-based and conservative.
- Semantic entailment remains a future capability, not a current promise.
