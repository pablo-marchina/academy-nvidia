# Epic 33 NVIDIA Activation Playbook Library

## Resumo
Implementação da biblioteca de playbooks de ativação NVIDIA com matching determinístico, confidence scoring, ranking, persistência em banco e exposição via API REST.

## O que foi feito
- 10 playbooks definidos em YAML (inferência, latência, agentes, dados, visão, voz, simulação, robótica, segurança, deploy privado)
- Loader com validação de schema (IDs únicos, campos obrigatórios, motions/complexities válidas)
- ActivationRecommendationRecord com FK AnalysisRun, JSON columns, indexes
- Matching determinístico: gap_type detectado in playbook.target_gap_types
- Confidence score com boosts (mapping, claims) e penalties (coverage, unsupported, degraded)
- Prioridade em 4 níveis
- ActivationRecommendationRepository com replace idempotente
- 3 endpoints: GET playbooks, GET/POST recommendations
- Oportunidades enriquecidas com top_activation_playbook, activation_confidence, activation_next_step
- Auto-generate no lifecycle do analysis run
- 22 testes unitários + 8 testes de integração

## Decisões
- YAML como source (não DB-first) — versionável, diff claro, sem migration para alterações
- Matching determinístico v1 (sem LLM) — testável, auditável, sem dependência externa
- Confidence com fórmula fixa — transparente, sem necessidade de dados históricos
- Idempotência via delete+regenerate — mesmo padrão do Claim Ledger (Epic 32)

## Pendências
- Feedback loop (aceitar/rejeitar recomendação) — v2
- LLM matching — v2
- Atualização automática de playbooks via deploy
