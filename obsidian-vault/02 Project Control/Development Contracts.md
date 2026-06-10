---
title: "Development Contracts"
date: 2026-06-09
tags: [workspace, contracts]
---

# Development Contracts

## O que são

Contratos de desenvolvimento definem o que cada módulo do produto **promete** e o que **não promete**. Eles guiam a IA antes de alterar código.

## Contratos Ativos

| Contrato | Arquivo | Módulo |
|----------|---------|--------|
| Pipeline Output | `docs/contracts/pipeline_output_contract.md` | `src/pipeline/run_pipeline.py` |
| Evidence | `docs/contracts/evidence_contract.md` | `src/extraction/schemas.py` + `src/validation/` |
| Scoring | `docs/contracts/scoring_contract.md` | `src/scoring/` |
| Diagnosis | `docs/contracts/diagnosis_contract.md` | `src/diagnosis/gap_diagnosis.py` |
| Recommendation | `docs/contracts/recommendation_contract.md` | `src/recommendation/` |
| End-of-Epic | `docs/contracts/end_of_epic_contract.md` | Processo de fechamento |

## Regra

Antes de alterar um módulo, leia o contrato correspondente em `docs/contracts/`. Se o contrato não existir, crie um via `prompts/create_adr.md`.

#workspace #contracts
