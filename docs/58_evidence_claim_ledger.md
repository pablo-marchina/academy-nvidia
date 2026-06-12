# Evidence & Claim Ledger

## Motivação
Claims geradas pela pipeline precisam ser rastreáveis até suas evidencias de origem. Sem esse vinculo, o usuário não pode auditar por que uma claim foi feita nem identificar claims sem suporte.

## Visão Geral
O Claim Ledger conecta cada claim (score, gap, mapping, uncertainty) às evidencias que a suportam. Para cada AnalysisRun, o ledger:
1. Gera claims deterministicamente a partir dos registros persistidos
2. Calcula cobertura de evidencia por run
3. Detecta claims criticas sem suporte
4. Expõe revisão humana (approve, reject, needs_more_evidence)

## Arquitetura
```
Pipeline → persist (startup_evidence, score_records, etc.)
         → ClaimLedgerService.build_claims_from_existing_records()
         → ClaimRepository.persist_claims_bulk()
         → ClaimRepository.get_evidence_coverage_summary()
         → API (claims, coverage, review)
```

## Componentes
### ClaimRecord (database/models)
- FK startup_id, analysis_run_id
- claim_text, claim_type, support_level, confidence
- evidence_refs_json (JSON column)
- used_in_score, used_in_gap, used_in_mapping, used_in_brief
- review_status, reviewer_notes
- metadata_json

### ClaimRepository (repositories/claim)
- CRUD: create_claim, create_claims_bulk, update_claim_review_status
- Query: list_claims_for_analysis_run, list_claims_for_startup
- Metrics: count_claims_by_support_level, get_evidence_coverage_summary
- Detection: list_unsupported_critical_claims
- Cleanup: delete_claims_for_run

### ClaimLedgerService (services/product/claim_ledger)
- build_claims_from_existing_records(run) → list[dict]
- persist_claims_for_run(run) → list[ClaimRecord]
- get_evidence_coverage_for_analysis_run(run_id) → dict
- detect_unsupported_claims(run_id) → list[dict]

## Endpoints
| Method | Path | Descrição |
|--------|------|-----------|
| GET | /api/v1/analysis-runs/{id}/claims | Lista claims (com filtro claim_type opcional) |
| GET | /api/v1/analysis-runs/{id}/evidence-coverage | Métricas de cobertura |
| PATCH | /api/v1/analysis-runs/{id}/claims/{claim_id}/review | Revisar claim |

## Integração
- `create_analysis_run_for_startup`: chama `persist_claims_for_run` após pipeline
- `get_analysis_run`: injeta `claim_summary` na resposta
- `list_analysis_runs`: injeta `claim_summary` em cada run
- `get_opportunity_list`: inclui `unsupported_claim_count` e `evidence_coverage`

## Limitações (v1)
- Sem tabela separada ClaimEvidenceLink (JSON column)
- Geração deterministica, sem LLM extraction
- Evidence coverage usa mapping simples (confidence → float)
- Sem notificações para baixa cobertura
