---
type: epic
status: completed
date: 2026-06
---

# Epic 6 — Composite Ranking + Motion Hints

## Objetivo
Agregar todos os scores em ranking unico ponderado por confianca, com sinalizacao de acao.

## Modulos criados
- `src/scoring/composite_ranking.py` — `compute_composite_score()` + `build_ranked_list()`

## Testes
- 9 testes (pesos, redistribuicao, confidence penalty, motion hints, empty list)

## Decisoes
- 4 pilares com pesos fixos (defensibility 30%, inception fit 25%, production readiness 35%, classification 10%)
- Motion hints: immediate_outreach, high_priority, monitor, lack_evidence, not_recommended
- Confidence penalty: ate 15% por componente ausente

## Links
- [[../04 Decisions]]
