# Epic 43 — Opportunity Score & Pipeline Ranking

## Objective
Build an evidence-backed opportunity scoring system that consolidates all existing analysis outputs (composite ranking, gaps, claims, activation recommendations, dossier, quality) into a single 0.0–1.0 score per startup, with explainable components, penalties, and tier-based ranking.

## Scope
- New `opportunity_score_records` table (migration 0007)
- `OpportunityScoreRecord` SQLAlchemy model
- `OpportunityScoreRepository`
- 5 new quality metric constants
- `opportunity_scoring` capability in registry
- 3 new degraded states
- `OpportunityScoreService` with 10 weighted components, 8 penalty types, weight redistribution, explanation model
- 4 new Pydantic schemas
- 4 new API endpoints
- 25+ unit tests + integration tests
- Documentation: plan, design doc, contract

## Out of Scope
- Changes to RAG retrieval, Qdrant ingestion, Discovery Engine, ML/learning-to-rank
- New complex UI, MCP, TOON/JTON, PDF, demo mode
- Scoring that depends on `data/demo_runs`
- LLM as primary judge

## Design
- Formula: `final_score = clamp(sum(component_weight * component_value) - sum(penalties), 0.0, 1.0)`
- 10 components with fixed weights that redistribute when data is missing
- 8 penalty types (unsupported claims, low evidence coverage, critical unsupported, degraded states, low confidence, contraindication, incomplete data, classification NON_AI)
- Score tiers: critical >=0.85, high >=0.70, medium >=0.50, low >=0.30, not_recommended <0.30 or contraindication
- Idempotency: replace latest score per analysis_run with incremental score_version

## Implementation Steps
1. Migration 0007 — create `opportunity_score_records` table
2. Add `OpportunityScoreRecord` model
3. Create `OpportunityScoreRepository`
4. Add quality metric constants, capability, degraded states
5. Create `OpportunityScoreService`
6. Add schemas to `product_schemas.py`
7. Add endpoints to `product_routes.py`
8. Create unit tests (25+)
9. Create integration tests
10. Create fixtures
11. Create documentation
12. Update README, ROADMAP, EVALS
13. Run validation suite
