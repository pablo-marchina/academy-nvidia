---
type: epic
status: completed
date: 2026-06
---

# Epic 2 — AI-native Classification

## Objetivo
Classificar startups em 5 niveis de AI-native (NON_AI a AI_NATIVE_SERVICE) com confianca explicita.

## Modulos criados
- `src/classification/ai_native_classifier.py` — classificador heuristico com 4 listas de padroes

## Testes
- 10 testes cobrindo todos os 5 niveis + evidencia fraca

## Decisoes
- Classificacao deterministica (sem LLM)
- Confianca derivada da quantidade e qualidade dos sinais

## Links
- [[../04 Decisions]]
