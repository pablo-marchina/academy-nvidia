---
tags: [research, epic-26.1, workspace, clarification-gate]
date: 2026-06-11
---

# Epic 26.1 — Workspace Clarification Gate

## Resumo

Adicionada seção "Workspace Clarification Gate" no AGENTS.md para instruir a IA a fazer perguntas de esclarecimento antes de gerar algo quando houver ambiguidade relevante.

## Problema

O projeto tem 42+ módulos (pipeline, RAG, Qdrant, evals, dashboard, CLI, API, UI, docs, workflows). A IA podia gerar código grande assumindo decisões que deveriam ser confirmadas antes, especialmente em frontend, API, arquitetura, contratos, workflows, dependências e mudanças de escopo.

## Solução

Workspace rule no AGENTS.md com:

- **When to ask**: 10 situações + 9 operações de alto risco
- **When not to ask**: 5 situações (hotfix, padrão, explícito, etc.)
- **Maximum 3 questions**: cada uma com default recomendado
- **Fallback seguro**: menor escopo se usuário não responder
- **Formato padronizado**: "Perguntas bloqueantes antes de gerar:"
- **7 exemplos**: cobrindo UI, API, Qdrant, dependency, docs, hotfix, passo óbvio

## Arquivos alterados

- `AGENTS.md` — seção principal (~100 linhas)
- `DECISIONS.md` — WSD-006
- `ROADMAP.md` — Epic 26.1 concluído
- `EVALS.md` — critério de qualidade
- `README.md` — menção nas regras de workspace
- `docs/52_workspace_clarification_gate.md` — documentação de referência
- `obsidian-vault/04 Decisions/` e `03 Research/` — notas

## Próximo passo sugerido

Nenhum — Epic 26.1 é auto-contido. Próximo épico deve respeitar o Clarification Gate.
