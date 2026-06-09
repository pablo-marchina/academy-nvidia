---
type: epic
status: completed
date: 2026-06
---

# Epic 3 — Evidence Validation

## Objetivo
Separar FATOS de INFERENCIAS e HIPOTESES nas evidencias coletadas, recalibrando confianca por tipo de fonte.

## Modulos criados
- `src/validation/evidence_validator.py` — validador deterministico com 3 niveis (FACT/INFERENCE/HYPOTHESIS)

## Testes
- 14 testes cobrindo tipos de fonte, quotes vazios, batch validation

## Decisoes
- Validacao sem LLM — regras heuristicas
- Confianca recalibrada por tipo de fonte e quote

## Links
- [[../04 Decisions]]
