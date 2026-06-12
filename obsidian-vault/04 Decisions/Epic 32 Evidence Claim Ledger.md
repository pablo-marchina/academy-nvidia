# Decision: Epic 32 — Evidence & Claim Ledger

**Date:** 2026-06-12

## Context
Claims produzidas pela pipeline nao eram rastreaveis ate suas evidencias de origem. Nao havia metrica de cobertura de evidencia nem deteccao de claims sem suporte.

## Decision
Implementar Claim Ledger deterministico (sem LLM extraction):
- `evidence_refs` como JSON column (sem FK enforcement)
- Idempotencia via delete+regenerate para cada AnalysisRun
- Support levels mapeados de confidence float: strong (>=0.8), medium (>=0.5), weak, unsupported
- CRITICAL_CLAIM_TYPES: gap_claim, defensibility_claim, nvidia_fit_claim, production_readiness_claim

## Consequences
- Claims totalmente deterministicas e testaveis
- Cobertura de evidencia calculada como supported/total
- 3 endpoints REST: list claims, evidence coverage, review claim
- 28 novos testes (18 unit + 10 integration)
- Sem LLM, sem tabela separada ClaimEvidenceLink
