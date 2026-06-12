# Epic 32 — Evidence & Claim Ledger

**Status:** Implementado
**Data:** 2026-06-12

## Resumo
Claim Ledger conecta cada claim (score, gap, mapping, uncertainty) as evidencias que a suportam. Para cada AnalysisRun:
1. Gera claims deterministicamente a partir dos registros persistidos
2. Calcula cobertura de evidencia
3. Detecta claims criticas sem suporte
4. Permite revisao humana via API

## Arquivos Criados
- `src/database/models.py` — ClaimRecord model
- `src/services/product/claim_constants.py` — enums
- `src/repositories/claim.py` — ClaimRepository
- `src/services/product/claim_ledger.py` — ClaimLedgerService
- `migrations/versions/a1b2c3d4e5f6_create_claim_records.py`
- `tests/unit/test_claim_repository.py` (12)
- `tests/unit/test_claim_ledger.py` (9)
- `tests/integration/test_claim_api.py` (10)

## Decisoes
- Deterministico (sem LLM)
- JSON column para evidence_refs
- Delete+regenerate para idempotencia
- Ver Decision 035 e nota em 04 Decisions/

## Proximos Passos (v2)
- LLM extraction de claims
- Tabela ClaimEvidenceLink com FK enforcement
- Notificacao de baixa cobertura
- Dashboard de auditoria
