---
type: decision
date: 2026-06
area: diagnosis
status: implemented
---

# Decision 014 — Gap Diagnosis como modulo independente

## Contexto
Gap diagnosis (902 linhas, 15 detectores) depende de todos os 3 scores e da classificacao. Integrar agora criaria acoplamento prematuro.

## Decisao
Manter gap diagnosis como modulo chamavel sob demanda, NAO integrado ao pipeline principal.

## Alternativas consideradas
- Integrar imediatamente (acoplamento prematuro)
- Fundir com scoring (responsabilidade unica violada)

## Consequencias
- Pipeline expoe dados necessarios para consumo futuro
- 9 testes unitarios para detectores individuais
- Coverage mapping: 15 gaps com ao menos 1 tecnologia NVIDIA

## Links
- [[../03 Research/Epic 7 Gap Diagnosis]]
- [DECISIONS.md](../../DECISIONS.md)
