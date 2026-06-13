# RAG / Action Brief Regression Dashboard

## Overview

- Status: **PASS**
- Generated at: `2026-06-13T19:25:02.148666+00:00`
- Reports dir: `C:\Users\Inteli\Documents\Projetos\academy-nvidia\.pytest_tmp_epic36_1\test_json_contains_required_fi0`

## Ingestion

| Metric | Value |
|---|---:|
| documents_seen | 10 |
| documents_valid | 10 |
| documents_skipped | 0 |
| chunks_created | 50 |
| chunks_upserted | 0 |
| sources_failed | 0 |
| validation_errors | 0 |

## Freshness

| Metric | Value |
|---|---:|
| stale_sources | 0 |
| expired_sources | 0 |
| deprecated_sources | 0 |

## RAG Evals

| Metric | Value |
|---|---:|
| rag_eval_passed | true |
| rag_eval_failed_cases | 0 |
| missing_context_count | 0 |

## Golden Evals & Action Brief Checks

| Metric | Value |
|---|---:|
| golden_eval_passed | true |
| golden_eval_failed_cases | 0 |
| action_brief_required_sections_passed | true |
| missing_evidence_count | 0 |

## Answer Quality

| Metric | Value |
|---|---:|
| answer_quality_passed | true |
| answer_quality_junit_present | true |
| answer_quality_tests | 2 |
| answer_quality_failures | 0 |
| answer_quality_errors | 0 |
| answer_quality_skipped | 0 |
| answer_quality_failed_cases | 0 |
| unsupported_claim_count | 0 |
| required_sections_missing | 0 |
| citation_coverage | 0.0 |
| answer_quality_status | PASS |

## Optional LLM Judge

Informational only. This optional judge is not a CI gate.

| Metric | Value |
|---|---:|
| llm_judge_status | INFO |
| llm_judge_report_present | false |
| llm_judge_provider | not run |
| llm_judge_total_cases | 0 |
| llm_judge_completed_cases | 0 |
| llm_judge_error_cases | 0 |
| llm_judge_mean_score | 0.0 |
| llm_judge_mean_faithfulness_score | 0.0 |
| llm_judge_mean_answer_relevancy_score | 0.0 |
| llm_judge_mean_groundedness_score | 0.0 |
| llm_judge_mean_completeness_score | 0.0 |
| llm_judge_mean_uncertainty_honesty_score | 0.0 |
| llm_judge_mean_executive_usefulness_score | 0.0 |

## Warnings

- None.

## Failures

- None.

## Inputs

- `source_sync`: found (`C:\Users\Inteli\Documents\Projetos\academy-nvidia\.pytest_tmp_epic36_1\test_json_contains_required_fi0\source_sync_dry_run.json`)
- `freshness`: found (`C:\Users\Inteli\Documents\Projetos\academy-nvidia\.pytest_tmp_epic36_1\test_json_contains_required_fi0\freshness_audit.json`)
- `ingestion`: found (`C:\Users\Inteli\Documents\Projetos\academy-nvidia\.pytest_tmp_epic36_1\test_json_contains_required_fi0\qdrant_ingest_dry_run.json`)
- `rag_eval`: found (`C:\Users\Inteli\Documents\Projetos\academy-nvidia\.pytest_tmp_epic36_1\test_json_contains_required_fi0\rag_eval_junit.xml`)
- `golden_eval`: found (`C:\Users\Inteli\Documents\Projetos\academy-nvidia\.pytest_tmp_epic36_1\test_json_contains_required_fi0\golden_eval_junit.xml`)
- `answer_quality`: found (`C:\Users\Inteli\Documents\Projetos\academy-nvidia\.pytest_tmp_epic36_1\test_json_contains_required_fi0\answer_quality_eval_junit.xml`)
- `answer_quality_llm_judge`: info (`C:\Users\Inteli\Documents\Projetos\academy-nvidia\.pytest_tmp_epic36_1\test_json_contains_required_fi0\answer_quality_llm_judge_report.json`) - optional report not run
