# CLI Demo End-to-End

**Decision:** Criar CLI demo com `argparse`, sem dependências novas, reusando pipeline/briefing/RAG/eval existentes.

**Date:** 2026-06-11

## Context

O sistema já tem pipeline completa, briefing, RAG e eval, mas não há entry point unificado para demonstração. Falta um modo simples de rodar o produto de ponta a ponta sem frontend.

## Decision

- `scripts/run_startup_radar_demo.py` com `argparse` (biblioteca padrão)
- Zero dependências novas (sem Typer/Click)
- CLI é orquestrador fino — toda lógica central está em `src/`
- 6 flags: `--input`, `--output-dir`, `--use-rag`, `--rag-backend`, `--run-answer-quality-eval`, `--offline`, `--format`
- Offline mode usa `MockEmbeddingProvider` + `InMemoryVectorStore`

## Status

Implementado no Epic 24.
