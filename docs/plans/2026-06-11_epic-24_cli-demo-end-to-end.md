> **ARCHIVED:** Historical plan artifact. Preserved for reference only. Current product direction is in Epics 28-31 and docs/54_final_product_backlog.md.

# Plan — Épico 24: CLI Demo End-to-End

**Date:** 2026-06-11
**Status:** Aprovado e implementado

## Objetivo

Criar uma CLI end-to-end mínima, offline-friendly, que execute o pipeline
principal do NVIDIA Startup AI Radar e exporte:

- Brief Markdown
- Brief JSON
- Relatório de execução
- Answer quality eval (opcional)

## Escopo

### Criar
- `scripts/run_startup_radar_demo.py`
- `examples/demo/sample_startup_input.json`
- `examples/demo/README.md`
- `docs/49_cli_demo_end_to_end.md`
- `tests/integration/test_cli_demo.py`

### Atualizar
- `README.md`, `ROADMAP.md`, `EVALS.md`, `DECISIONS.md`
- `Makefile`
- `obsidian-vault/`

## Decisões Técnicas

1. **argparse** — mesmo padrão dos scripts existentes (`ingest_nvidia_corpus.py`)
2. **Sem lógica duplicada** — CLI chama `run_full_pipeline()`, `build_action_brief()`, etc.
3. **Offline mode** — `MockEmbeddingProvider` + `InMemoryVectorStore` (mesmo dos golden tests)
4. **Qdrant mode** — `QdrantStore` com mensagem de erro clara se indisponível
5. **Answer quality eval** — caso genérico inline (não golden cases)

## Arquivos

Ver docs/49_cli_demo_end_to_end.md para documentação completa.

