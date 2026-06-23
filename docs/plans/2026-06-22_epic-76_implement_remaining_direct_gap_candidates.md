# Epic 76: Implement Remaining Direct Gap Candidates

## Summary

Implement executable local candidates for the 14 remaining direct gaps:

- GraphRAG/evidence graph: Neo4j, Memgraph, Kuzu, FalkorDB, NetworkX, LlamaIndex PropertyGraphIndex, DRIFT-like search, Temporal GraphRAG, Temporal Knowledge Graph.
- Evidence sufficiency/abstention: conformal prediction, conformal risk control, bayesian model averaging, ensemble of evaluators, model disagreement detection.

External graph engines will be represented as local comparable implementations, not claimed as live engine integrations. Statistical evidence candidates can be implemented directly.

## Scope

- Add local graph alternative candidate implementations.
- Add statistical evidence sufficiency candidate implementations.
- Update direct alternative gap benchmark to execute these candidates.
- Reduce remaining direct gap count based on benchmark results.
- Add focused unit tests.

## Non-Goals

- Do not require Docker, Neo4j, Memgraph, Kuzu, FalkorDB, or LlamaIndex services/packages.
- Do not claim a live third-party engine was benchmarked unless it actually ran.
- Do not add `cost_latency_reliability_controls`.

## Test Plan

- Unit tests for graph candidate execution and scoring shape.
- Unit tests for evidence statistical candidate execution.
- Unit tests for direct benchmark closing the previous `NEEDS_SEPARATE_IMPLEMENTATION` items.
- Focused black, ruff, mypy, pytest.
- Quick final proof.

