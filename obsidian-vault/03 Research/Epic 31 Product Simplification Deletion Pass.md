---
tags: [research, epic-31, architecture, cleanup]
date: 2026-06-12
---

# Epic 31 — Product Simplification & Deletion Pass

## Resumo

Removeu artefatos demo legados após produto estar completo (Epics 29-30). Demo não é mais o fluxo principal.

## Checklist

- [x] DELETE_NOW — 17 generated artifacts removidos
- [x] .gitignore — 3 novas regras
- [x] ARCHIVE_HISTORY — 26+ docs/planos arquivados
- [x] README reestruturado
- [x] ROADMAP atualizado
- [x] DECISIONS.md — Decision 034 adicionada
- [x] Regression test adicionado
- [x] Known Limitations.md atualizado
- [x] Obsidian notes criados

## Items preservados (justificados)

- examples/demo/sample_startup_input.json — fixture de teste
- examples/golden/, examples/rag_eval/, examples/answer_quality/, examples/validation/ — fixtures de eval
- Demo API routes, schemas, service — DELETE_AFTER_TEST_UPDATE
- CLI demo script, frontend — REPLACE_BEFORE_DELETE
