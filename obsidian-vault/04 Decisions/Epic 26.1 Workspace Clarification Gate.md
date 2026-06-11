---
tags: [decision, workspace, clarification-gate, epic-26.1]
date: 2026-06-11
---

# Decision WSD-006 — Workspace Clarification Gate

## Context

O AGENTS.md já regulava planos, contratos, revisão e validação, mas a IA podia gerar código, arquitetura, docs grandes, frontend, API ou prompts baseados em suposição sem verificar ambiguidade com o usuário.

## Decision

Adicionar a seção "Workspace Clarification Gate" no AGENTS.md que instrui a IA a fazer perguntas de esclarecimento antes de gerar algo quando houver ambiguidade relevante.

### Regras

1. **When to ask**: 10 situações (stack, escopo, contrato, formato, comportamento, erro, dependências, ambiente, dados, prioridade) + 9 operações de alto risco (frontend, API, arquitetura, contratos, dependências, CI/CD, docs >50 linhas, épico >3 steps, pipeline/RAG)
2. **When not to ask**: 5 situações (hotfix 1-5 linhas, decisão explícita, padrão claro, pergunta não muda solução, menor escopo óbvio)
3. **Limite**: máximo 3 perguntas por rodada, cada uma com default recomendado
4. **Fallback**: menor escopo seguro se usuário não responder, registrar suposição, evitar mudança irreversível, evitar dependência nova, evitar refatoração ampla
5. **Formato**: prefixo "Perguntas bloqueantes antes de gerar:", cada pergunta com "Recomendado: <default>"
6. **Exemplos**: 7 exemplos (UI, API, Qdrant, dependency, docs, hotfix, passo óbvio)

## Alternatives considered

- Criar ferramenta/script externo (rejeitado — complexidade desnecessária)
- Criar skill separada (rejeitado — AGENTS.md é o lugar canônico)
- Não fazer nada (rejeitado — risco de geração baseada em suposição)

## Consequences

- IA pergunta antes de gerar frontend, API, arquitetura, contratos, dependências, workflows, docs grandes, épicos grandes, pipeline ou RAG
- IA não pergunta para hotfixes, passos óbvios, padrões claros ou decisões já explícitas
- Se usuário não responder, assume menor escopo seguro
- Tarefas simples continuam rápidas

## Status

Implementado no Epic 26.1.
