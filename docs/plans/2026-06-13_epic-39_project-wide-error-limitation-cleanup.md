# Epic 39 — Project-Wide Error & Limitation Cleanup

**Data:** 2026-06-13
**Status:** Aprovado

## Objetivo
Resolver, classificar ou fechar todos os erros, limitações e dívidas técnicas do projeto inteiro, sem adicionar features novas.

## Escopo
- Corrigir mypy (5 errors), ruff (73 errors), black (6 files)
- Adicionar pytest markers (unit, e2e, slow, optional, external_service)
- Dividir `make validate` em targets (validate-fast, validate-full, etc.)
- Corrigir sentence-transformers version em pyproject.toml
- Atualizar ERROR_LOG.md, DECISIONS.md, ROADMAP.md, README.md, EVALS.md, AGENTS.md
- Documentar Playwright setup
- Adicionar exclusões para black (node_modules, .pytest_tmp, .git)

## Fora de Escopo
- Nenhuma feature nova
- Nenhuma alteração em scoring, RAG retrieval, Qdrant ingestion, recommendation central
- Nenhuma implementação de auth, PDF, MCP, TOON/JTON

## Entregáveis
1. `pyproject.toml` corrigido
2. `Makefile` com novos targets
3. `src/evaluation/structured_outputs.py` mypy corrigido
4. `src/quality/service.py` mypy corrigido
5. `src/services/product/claim_ledger.py` ruff corrigido
6. `tests/integration/test_postgres_migration.py` ruff corrigido
7. `tests/unit/test_review_repository.py` ruff corrigido
8. `scripts/validate.sh` atualizado
9. `ERROR_LOG.md` atualizado
10. `DECISIONS.md` atualizado
11. `ROADMAP.md` atualizado
12. `README.md` atualizado
13. `EVALS.md` atualizado
14. `docs/66_project_wide_error_limitation_cleanup.md`
