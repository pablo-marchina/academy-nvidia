# Epic 40 — Startup Discovery Engine

## What
Multi-source engine to discover AI-native Brazilian startups, collect public evidence, detect AI-native signals, deduplicate, and promote to Startup records.

## Why
The pipeline had no upstream discovery layer. Startups had to be manually created via the API with no automated candidate intake, signal detection, or dedup.

## How

### Discovery Sources (6 definidas)
- `manual_seed_br_ai_startups` — manual seed list
- `configured_url_list` — user-provided URLs
- `distrito_startup_programs` — Distrito programs
- `ace_startups_portfolio` — Ace accelerator
- `bossa_invest_portfolio` — Bossa Invest VC
- `inovativa_startups` — Inovativa accelerator

### Flow
1. Source defines collection method (manual_seed, url_list, static_html)
2. Manual seed: entries -> signal detection -> dedup -> candidates
3. URL list: fetch -> parse -> signal detection -> dedup -> candidates
4. Candidate review -> promote to Startup -> pipeline flow

### Signal Detection
- 30+ keywords (AI, IA, LLM, GPU, CUDA, TensorRT, RAPIDS, NeMo, etc.)
- Portuguese support (IA, inteligência artificial, aprendizado de máquina)
- Confidence: 5 factors (name, website, signals, manual_seed, source_reliable)
- Output: signals list, signal_count, confidence_contribution, has_nvidia_tech, evidence_excerpts

### Dedup
- `normalized_name()` — casefold + whitespace collapse
- `extract_domain()` — URL domain extraction (removes www, scheme)
- Duplicates marked (status=duplicate), never deleted

### API (9 endpoints)
- Sources, manual-seed, url-list, runs, candidates, promote, dedup

## Constraints
- No scraping agressivo, no login/paywall bypass
- Error sources produce degraded (not failed) runs
- Duplicates are marked, never deleted
- No LLM, no external paid APIs
