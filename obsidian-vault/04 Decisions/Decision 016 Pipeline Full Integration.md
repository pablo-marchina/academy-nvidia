---
title: "Decision 016: Pipeline Full Integration"
date: 2026-06-09
status: accepted
tags: [decision, pipeline, diagnosis, recommendation]
---

# Decision 016: Pipeline Full Integration

## Context

Gap Diagnosis (Epic 7) e Recommendation Engine (Epic 8) foram implementados como modulos independentes — nao integrados ao pipeline. O pipeline orquestrador (`run_full_pipeline`) parava no composite ranking.

## Decision

Integrar ambos os modulos no pipeline principal, adicionando 3 novos steps apos o composite ranking:

1. Step 8: Gap Diagnosis (15 detectores deterministicos)
2. Step 9: NVIDIA Technology Mapping (matriz deterministico)
3. Step 10: Recommendation Engine (4 acoes: approach_now → not_recommended)

O `PipelineResult` agora inclui `gap_diagnosis` e `recommendation`.

## Consequences

- Pipeline: 7 → 11 steps
- Output final contem diagnosed_gaps, nvidia_technology_candidates, recommendations, suggested_technical_experiments
- missing_evidence propagado de todos os modulos
- Nenhuma tecnologia NVIDIA e recomendada sem gap diagnosticado
- Evidencia fraca reduz forca da recomendacao (action != APPROACH_NOW)
- 10 pipeline tests (5 existentes + 5 novos)

## Alternatives Considered

- Manter modulos separados: exigiria chamada manual
- Integrar via LangGraph: complexidade prematura
- Pipeline separado de diagnostico: duplicacao com pipeline principal

## Links

- Epic 7: Gap Diagnosis
- Epic 8: Recommendation Engine
- Decision 014: Gap Diagnosis como modulo independente
