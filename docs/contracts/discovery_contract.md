# Discovery API Contract

**Module:** `src/api/product_routes.py` (discovery routes)
**Version:** 1.0
**Date:** 2026-06-13

## Purpose

Expose multi-source startup discovery operations: manual seed entry, URL list
discovery, candidate management, dedup, and promotion to Startup records.

## Resource Contracts

### DiscoverySource

`GET /discovery/sources` returns a list of configured discovery sources with
metadata: `source_id`, `name`, `source_type`, `base_url`, `country_scope`,
`sector_scope`, `allowed`, `requires_api_key`, `rate_limit_hint`,
`collection_method`, `robots_or_terms_note`, `enabled_by_default`, `notes`,
`usable`.

Sources are defined in `src/config/discovery_sources.json` and loaded via
`src/discovery/source_registry.py`. No API key is required for the built-in 6
sources.

### DiscoveryRun

`POST /discovery/manual-seed` accepts `ManualSeedRequest` (list of entries with
`name`, `website`, `sector`, `description`, `country`). Creates a
`DiscoveryRun`, runs signal detection + dedup, returns `ManualSeedResponse`
with `discovery_run_id`, `status`, `candidates_created`, `duplicates_found`.

`POST /discovery/url-list` accepts `UrlListRequest` (list of URLs). Fetches
each URL via httpx, extracts AI-native signals via keyword matching, creates
candidates, returns `UrlListResponse` with error reporting.

Lifecycle values: `queued`, `running`, `completed`, `degraded`, `failed`.
Sources that partially fail produce a `degraded` run with `error_message`.

### DiscoveryCandidate

`GET /discovery/candidates` lists candidates with filters: `status`,
`source_id`, `sector`, `confidence_min` (0.0-1.0), `has_website`,
`ai_native_signal`.

`GET /discovery/candidates/{candidate_id}` returns full candidate detail
including `ai_native_signals_json` (matched signals, count,
confidence_contribution, has_nvidia_tech) and `evidence_refs_json`.

`POST /discovery/candidates/{candidate_id}/promote` promotes a candidate to a
Startup record. If a matching Startup already exists (by normalized_name or
website), the candidate is linked to the existing record. Returns
`PromoteCandidateResponse` with status: `promoted`,
`matched_existing_startup`, or `already_promoted`.

`POST /discovery/candidates/{candidate_id}/dedup` checks for duplicate
candidates by normalized_name or website domain. If found, marks the candidate
as `duplicate`. Returns `DedupCandidateResponse` with duplicate references or
nulls.

### AI-Native Signals

Signal detection is keyword-based (30+ patterns in `src/discovery/signals.py`):
AI, IA, LLM, machine learning, deep learning, GPU, CUDA, TensorRT, RAPIDS,
NeMo, Triton, NLP, inference, transformers, etc. Supports Portuguese keywords
(IA, inteligência artificial, aprendizado de máquina).

Confidence levels: `low` (<0.4), `medium` (0.4-0.69), `high` (>=0.7).
Calculated from: has_name (+0.3), has_website (+0.1), signal_contribution
(0.0-0.6), is_manual_seed (+0.2), source_reliable (+0.1).

### Dedup

Dedup uses `normalized_name` (casefold + whitespace collapse) and `website`
domain extraction. Duplicates are marked (`status=duplicate`), never deleted.
Existing Startup records are checked before promotion.

## Error Handling

- 404 for missing discovery runs or candidates.
- 409 for candidates that are already marked as duplicate (cannot promote).
- 422 for invalid input (empty name in manual seed, invalid URL in URL list).
- `degraded` run status when some URLs in a URL list fail to fetch.

## Dependencies

- `httpx` + `BeautifulSoup` for URL list fetching (already in project deps).
- No external paid APIs required.
- No scraping agressivo, no login/paywall bypass.
