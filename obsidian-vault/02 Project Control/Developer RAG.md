---
title: "Developer RAG"
date: 2026-06-09
tags: [workspace, rag, documentation]
---

# Developer RAG

## Objetivo

O Developer RAG fornece contexto recuperável para o agente IA sobre o workspace de desenvolvimento — regras, planos, contratos, prompts, decisões e limitações.

## Diferença do Product RAG

| Developer RAG | Product RAG |
|---------------|-------------|
| Ajuda o agente a seguir regras do workspace | Recomenda tecnologias NVIDIA para startups |
| Fontes: AGENTS.md, planos, ADRs, contratos, prompts | Fontes: playbooks NVIDIA, documentação técnica |
| Fundação documental apenas (sem vector DB) | Futuro épico do produto |

## Fontes Indexáveis

AGENTS.md, README.md, ROADMAP.md, DECISIONS.md, EVALS.md, ERROR_LOG.md, docs/plans/, docs/adr/, docs/contracts/, prompts/, obsidian-vault/02/, obsidian-vault/03/, obsidian-vault/04/

## Fontes Proibidas

src/, tests/, arquivos gerados, templates vazios, prompts archived

## Decisão

Vector DB não será implementado nesta etapa. Fontes estão estruturadas e prontas para indexação futura.

#workspace #rag
