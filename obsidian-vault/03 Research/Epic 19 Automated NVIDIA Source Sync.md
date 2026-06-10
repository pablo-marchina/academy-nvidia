---
tags: [research, epic-19]
status: completed
date: 2026-06-10
---

# Epic 19 — Automated NVIDIA Corpus Source Sync

## Resumo
Script de sync automatizado que baixa documentos NVIDIA permitidos para staging, valida metadata/hash, gera relatorio e promove ao corpus local com --promote.

## Arquivos Criados
- scripts/sync_nvidia_sources.py — script principal (675 linhas)
- data/nvidia_corpus/source_allowlist.yaml — allowlist versionada (11 fontes)
- 	ests/unit/test_sync_nvidia_sources.py — 49 testes unitarios

## Arquivos Alterados
- README.md, EVALS.md, ROADMAP.md, Makefile, docs/contracts/rag_contract.md

## CLI
`
--dry-run | --source-id | --product | --promote | --staging-only
--report-path | --fail-on-validation-error | --max-documents | --rate-limit-seconds
`

## Seguranca
Timeout 30s, max 5MB, robots.txt, rate limit 2s, user-agent claro, sem cookies/login/follow

## Testes
49 testes, zero chamadas externas (tudo mockado)
