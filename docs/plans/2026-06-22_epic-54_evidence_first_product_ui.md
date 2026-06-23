# Epic 54: Evidence-First Product UI e API Evidence Bundle

## Summary

Adicionar uma visao evidence-first consolidada para analysis runs. A API ja expoe claims, coverage, recommendations, dossier e oportunidades; este incremento agrega esses sinais em um evidence bundle unico e apresenta na UI confiança, evidencias, lacunas, degradacoes, lineage e alternativas que perderam.

## Key Changes

- Criar endpoint `GET /analysis-runs/{analysis_run_id}/evidence-bundle`.
- Agregar claims, evidence coverage, activation recommendations, dossier, degraded checks, missing evidence, RAG/supporting refs, confidence, uncertainty e lineage em um payload unico.
- Criar tipos frontend e uma `EvidenceFirstRunView` acessivel pelo detalhe do analysis run/startup.
- Mostrar estados honestos quando RAG/Qdrant ou evidencia estao ausentes, sem apresentar recomendacoes como totalmente provadas.
- Gerar report opcional `final_case_evidence/evidence_first_ui_report.json` para evidenciar campos e rotas criticas.

## Test Plan

- Unit/API tests para evidence bundle com run inexistente, run sem claims e run com claims/recommendations.
- Frontend typecheck/build para os novos tipos e componentes.
- Validacao com quick proof, pytest focado, ruff, black e mypy focados.

## Assumptions

- Sem dependencia de Docker, PostgreSQL ou Qdrant reais para os testes locais.
- Nao alterar scoring, retrieval RAG ou recommendation central.
- Recomendacao sem evidencia deve aparecer como nao comprovada ou pendente, nunca como provada.
