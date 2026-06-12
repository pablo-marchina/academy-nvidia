# Epic 32 — Evidence & Claim Ledger

**Date:** 2026-06-12
**Status:** Build — em execução

## Objetivo
Conectar evidencias a claims, medir cobertura de evidencia, detectar claims sem suporte e expor auditabilidade via API do produto.

## Escopo
### Dentro
- Modelo `ClaimRecord` com FK para Startup e AnalysisRun
- Enums: `ClaimType`, `SupportLevel`, `ClaimReviewStatus`
- `ClaimRepository` (CRUD, bulk, cobertura, claims criticas nao suportadas)
- `ClaimLedgerService` (geracao deterministica de claims a partir de registros persistidos)
- 3 endpoints: listar claims, cobertura de evidencia, revisar claim
- `claim_summary` injetado em `AnalysisRunRead`
- `unsupported_claim_count` e `evidence_coverage` no `OpportunityListItem`
- 5 readiness checks no degraded.py
- Testes unitarios (repository, ledger) e integracao (API)
- Migracao Alembic 0002
- Documentacao (plan, module doc, contract)

### Fora (v2)
- UI para revisao de claims
- LLM extraction de claims
- Notificacao de baixa cobertura
- Dashboard de auditoria

## Decisoes
- `evidence_refs_json` (JSON column) em vez de tabela `ClaimEvidenceLink`; link relacional documentado como evolucao futura
- Geracao deterministica a partir de registros persistidos; sem extracao LLM na v1
- Idempotencia: deleta e regenera todas as claims de um AnalysisRun
- `claim_summary` injetado via repositorio a nivel de rota
- Support levels mapeados de confidence float: strong >= 0.8, medium >= 0.5, weak, unsupported

## Files
- `src/database/models.py` — ClaimRecord model
- `src/services/product/claim_constants.py` — enums
- `src/repositories/claim.py` — ClaimRepository
- `src/services/product/claim_ledger.py` — ClaimLedgerService
- `src/services/product/degraded.py` — readiness checks
- `src/api/product_schemas.py` — schemas
- `src/api/product_routes.py` — endpoints
- `src/services/product/service.py` — integracao
- `migrations/versions/a1b2c3d4e5f6_create_claim_records.py`

## Next
- Rodar validacoes
- Atualizar ROADMAP, EVALS, DECISIONS
- Atualizar Obsidian vault
