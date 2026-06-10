---
title: "Decision 017: Startup Action Brief Module"
date: 2026-06-09
status: accepted
tags: [decision, briefing, consolidation, pydantic]
---

# Decision 017: Startup Action Brief Module

## Context

PipelineResult continha todos os dados brutos mas nao havia formato executivo consolidado. Template existente era esqueleto de 8 linhas.

## Decision

Criar `src/briefing/` com schemas Pydantic e funcoes deterministicas. O brief e uma projecao do PipelineResult — nenhuma nova logica de scoring, diagnosis ou recommendation.

## Consequences

- Brief e evidence-aware (preserva missing_evidence, uncertainties, evidence tags)
- Verdict deterministico evita alucinacao
- Serializavel para JSON e Markdown
- 10 novos testes

## Alternatives Considered

- Estender PipelineResult: acoplamento excessivo
- Apenas Markdown sem schema: sem validacao
- Consolidar no pipeline: mistura responsabilidades

## Links

- Decision 016: Pipeline Full Integration
- Epic 10: Startup Action Brief
