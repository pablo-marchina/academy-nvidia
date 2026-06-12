# Contract: Claim Ledger

## Versão
1.0.0 — 2026-06-12

## Propósito
Gerenciar claims geradas a partir de evidencias e registros de pipeline, medir cobertura de evidencia e permitir revisão humana.

## Dependências
- `src/repositories/claim.py` (ClaimRepository)
- `src/services/product/claim_constants.py` (enums)
- `src/database/models.py` (ClaimRecord)

## Inputs
### ClaimRepository.create_claim
- startup_id, analysis_run_id, claim_text, claim_type, support_level, confidence
- evidence_refs (opcional, lit[dict]), used_in_score/gap/mapping/brief (opcional)
- review_status (default "pending_review"), reviewer_notes (default "")

### ClaimRepository.create_claims_bulk
- Lista de dicts com campos acima

### ClaimLedgerService.build_claims_from_existing_records
- AnalysisRun (objeto carregado com relationships startup_evidence, score_records, gap_diagnosis_records, nvidia_mapping_records)

## Outputs
### GET /analysis-runs/{id}/claims
```json
{
  "claims": [
    {
      "id": "str",
      "startup_id": "str",
      "analysis_run_id": "str",
      "claim_text": "str",
      "claim_type": "str",
      "support_level": "str",
      "confidence": "str",
      "evidence_refs": [{}],
      "used_in_score": true,
      "used_in_gap": true,
      "used_in_mapping": false,
      "used_in_brief": false,
      "review_status": "pending_review",
      "reviewer_notes": "",
      "created_at": "ISO datetime"
    }
  ]
}
```

### GET /analysis-runs/{id}/evidence-coverage
```json
{
  "analysis_run_id": "str",
  "total_claims": 10,
  "supported_claims": 5,
  "unsupported_claims": 2,
  "weak_claims": 3,
  "critical_claims": 4,
  "critical_supported_claims": 2,
  "evidence_coverage": 0.62
}
```

### PATCH /analysis-runs/{id}/claims/{claim_id}/review
Input:
```json
{
  "review_status": "approved",
  "reviewer_notes": "Looks good"
}
```
Output: ClaimRead object

## Regras de Negócio
- `claim_summary` é calculado via ClaimRepository e injetado na rota
- `opportunity_list` items incluem `unsupported_claim_count` e `evidence_coverage`
- Support level mapping: evidence_refs vazio → unsupported, confidence high + refs → strong
- CRITICAL_CLAIM_TYPES: gap_claim, defensibility_claim, nvidia_fit_claim, production_readiness_claim
- Evidence coverage = sum(confidence_to_float(support_level)) / total_claims
- confidence_to_float: high=1.0, medium=0.6, low=0.2

## Erros
- 404: analysis_run ou claim nao encontrado
- 400: review_status invalido
- Validacao de review_status via set `CLAIM_REVIEW_STATUSES`

## Limitações Conhecidas
- `evidence_refs` armazenado como JSON column; sem enforced FK
- Idempotencia via delete+regenerate; pode causar janela de vazio
- Cobertura de evidencia usa mapping simples, sem weighted scoring
