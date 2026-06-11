# RAG / Action Brief Regression Dashboard

## Overview

- Status: **WARN**
- Generated at: `2026-06-11T12:49:59.898871+00:00`
- Reports dir: `not found`

## Ingestion

| Metric | Value |
|---|---:|
| documents_seen | 10 |
| documents_valid | 10 |
| documents_skipped | 0 |
| chunks_created | 50 |
| chunks_upserted | 50 |
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
| rag_eval_passed | not run |
| rag_eval_failed_cases | 0 |
| missing_context_count | 0 |

## Golden Evals & Action Brief Checks

| Metric | Value |
|---|---:|
| golden_eval_passed | not run |
| golden_eval_failed_cases | 0 |
| action_brief_required_sections_passed | not run |
| missing_evidence_count | 0 |

## Answer Quality

| Metric | Value |
|---|---:|
| answer_quality_passed | true |
| answer_quality_junit_present | true |
| answer_quality_tests | 9 |
| answer_quality_failures | 0 |
| answer_quality_errors | 0 |
| answer_quality_skipped | 0 |
| answer_quality_failed_cases | 0 |
| unsupported_claim_count | 0 |
| required_sections_missing | 0 |
| citation_coverage | 0.0 |
| answer_quality_status | PASS |

## Warnings

- No corpus maintenance reports directory found.
- source_sync report not found.
- rag_eval_junit.xml not found.
- golden_eval_junit.xml not found.

## Failures

- None.

## Inputs

- `source_sync`: missing (`not found`)
- `freshness`: found (`C:\Users\Inteli\Documents\Projetos\academy-nvidia\data\ingestion_reports\freshness_after_qdrant_384_reingestion.md`)
- `ingestion`: found (`C:\Users\Inteli\Documents\Projetos\academy-nvidia\data\ingestion_reports\qdrant_384_reingestion.json`)
- `rag_eval`: missing (`not found`)
- `golden_eval`: missing (`not found`)
- `answer_quality`: found (`C:\Users\Inteli\Documents\Projetos\academy-nvidia\data\regression_reports\answer_quality_eval_junit.xml`)
