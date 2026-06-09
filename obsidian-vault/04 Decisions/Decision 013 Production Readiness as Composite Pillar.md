---
type: decision
date: 2026-06
area: scoring
status: implemented
---

# Decision 013 — Production AI Readiness como quarto pilar do Composite Score

## Contexto
Composite Score original considerava apenas defensibility (alpha) e inception fit (beta). Production readiness adicionada como dimensao independente.

## Decisao
4 pilares com pesos fixos: defensibility 30%, inception fit 25%, production readiness 35%, classification 10%.

## Alternativas consideradas
- Manter 2 scores (perde maturidade operacional)
- Adicionar como bonus (sem peso real)
- Media simples (sem diferenciacao)

## Consequencias
- Production readiness e o maior peso (melhor preditor de adocao NVIDIA)
- Startup early-stage penalizada — mitigado por confidence penalty

## Links
- [[../03 Research/Epic 5 Production Readiness]]
- [DECISIONS.md](../../DECISIONS.md)
