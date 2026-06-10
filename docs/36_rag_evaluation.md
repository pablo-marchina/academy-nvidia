# RAG Evaluation & Retrieval Quality Gates

**Epic 12** | **Date**: 2026-06-09

## Objective

Create an offline evaluation layer to measure whether the Product RAG (`src/rag/`) retrieves the correct NVIDIA context for each gap and technology pair. All evaluation is deterministic — no embeddings, no Qdrant, no LLM judge, no external calls.

## Architecture

```
examples/rag_eval/
├── golden_queries.json        # 16 golden queries (10 gaps + 6 negative)
├── expected_contexts.json     # Expected chunk IDs per query

src/evaluation/
├── rag_eval_schemas.py        # RagEvalCase, RagRetrievalMetrics, RagEvalResult, RagQualityGateResult
├── rag_eval.py                # run_rag_eval(), compute_metrics(), run_quality_gates(), format_eval_summary()

tests/unit/test_rag_eval.py    # 20 tests covering golden queries, metrics, gates, brief compatibility
```

## Golden Queries

| case_id | gap_type | Expected Sources | Critical |
|---|---|---|---|
| `inference_cost_all` | `high_inference_cost` | nim, tensorrt_llm, triton | ✅ |
| `inference_cost_tensorrt` | `high_inference_cost` + TensorRT-LLM | tensorrt_llm | ✅ |
| `inference_cost_triton` | `high_inference_cost` + Triton | triton | |
| `latency_all` | `high_latency` | nim, tensorrt_llm, triton | |
| `latency_tensorrt` | `high_latency` + TensorRT-LLM | tensorrt_llm | |
| `agent_governance` | `agent_governance_gap` | nemo_guardrails | ✅ |
| `data_pipeline` | `slow_data_pipeline` | rapids | |
| `tabular_heavy` | `heavy_tabular_processing` | rapids | |
| `voice_ai` | `voice_need` | riva | ✅ |
| `external_api` | `external_api_dependency` | nim | |
| `simulation` | `simulation_need` | omniverse | |
| `robotics` | `robotics_need` | isaac | |
| `healthcare` | `healthcare_compliance_need` | clara_monai | |
| `cybersecurity` | `ai_cybersecurity_need` | morpheus | |
| `unknown_gap` | nonexistent_gap | (none, negative test) | ✅ |
| `empty_query` | (empty) | (none, negative test) | |

## Metrics (7)

| Metric | Definition |
|---|---|
| `hit_at_k` | At least one expected source appears in top_k results |
| `expected_source_coverage` | % of expected source_ids found in results |
| `expected_product_coverage` | % of expected products found in results |
| `irrelevant_context_count` | Chunks with source_id NOT in expected_source_ids |
| `missing_context_count` | Expected source_ids NOT found in results (top_k-aware) |
| `top_1_expected_match` | Top result is from an expected source |
| `context_precision` | Relevant / (relevant + irrelevant) in results |

## Quality Gates (6)

| Gate | What it checks | Fails if |
|---|---|---|
| `hit_at_3_for_critical` | Critical golden queries must have hit_at_k=True | Any critical case fails hit_at_k |
| `top_1_for_critical` | Critical golden queries must have top_1_expected_match | Any critical case fails top_1 |
| `zero_missing_for_known` | Known queries must have zero missing expected sources | missing_context_count > 0 for query with expected sources |
| `irrelevant_below_limit` | Irrelevant context count ≤ 1 per query | Any query exceeds 1 irrelevant |
| `provenance_check` | Every RetrievedContext must have source_id and url | Any context missing provenance |
| `missing_context_explicit` | Query without match must return missing_context | Negative query returns non-empty |

## Key Design Decisions

| Decision | Rationale |
|---|---|
| No LLM judge | Deterministic metrics are reproducible and testable |
| Golden queries versioned | Queries refer to source_ids from sources.yaml — single point of truth |
| Metrics via ChunkIndex | Reuses existing RAG module without modification |
| Quality gates separate from metrics | Gates aggregate metrics across cases for pass/fail decisions |
| Provenance gate at chunk level | Every retrieved context must carry source and url |

## Limitations

- Metrics do not measure semantic relevance (keyword-based only)
- Golden queries are manual — corpus changes may require updates
- No cross-query aggregate metrics (e.g., mean average precision)
