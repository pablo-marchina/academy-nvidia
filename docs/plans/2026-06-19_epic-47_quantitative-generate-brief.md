# Epic 47 - Quantitative generate_brief

## Context
`generate_brief` must produce a deterministic, evidence-grounded ActionBrief from
existing workflow state. It must not call LLMs, Qdrant, scraping, internet, or
recompute recommendations and scores.

## Scope
- `src/briefing/`
- `src/agents/graph.py` only for `generate_brief` node wiring
- `src/agents/state.py` only for brief state fields
- `src/quality/` if quality gate snapshot/status needs alignment
- Required unit tests for generate brief, graph, quality gates, and recommendation
  engine if ranking fields need coverage

## Plan
1. Keep `ActionBrief` as a structured Pydantic output with numeric summaries,
   recommendation records, blockers, audit trail, quality snapshot, and calibration
   snapshot.
2. Filter final `top_recommendations` to recommendations with
   `production_allowed=true` and explicit evidence plus RAG support.
3. Put blocked or inconsistent recommendations only in blockers/needs-review
   context, never as final recommendations.
4. Determine `brief_status` deterministically from ranking status, quality status,
   unsupported critical claims, calibration gaps, support inconsistencies, and
   production recommendation availability.
5. Compute required `brief_metrics` from state and recommendation records without
   recalculating upstream scores or rankings.
6. Ensure audit trail lists executed nodes, calibration decision IDs, evidence IDs,
   RAG context IDs, propagated blockers, and quality gate status.
7. Extend tests for filtering, blockers, numeric summaries, support IDs,
   status transitions, and absence of external service imports.

## Validation
- `python -m pytest tests/unit/test_generate_brief.py`
- `python -m pytest tests/unit/test_langgraph_product_graph.py`
- `python -m pytest tests/unit/test_quality_gates.py`
- `python -m pytest tests/unit/test_recommendation_engine.py`
- `python -m mypy src`

## Main Risk
The current workflow has partially overlapping field names from ranking and older
briefing code. The implementation must preserve backward-compatible state keys
while making the production brief stricter.
