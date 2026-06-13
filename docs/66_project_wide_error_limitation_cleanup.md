# Project-Wide Error & Limitation Cleanup

**Epic:** 39
**Versão:** 1.0
**Data:** 2026-06-13

## Propósito

Resolver, classificar ou fechar todos os erros, limitações e dívidas técnicas do projeto, transformando o pipeline de validação em algo rápido, confiável e preparado para release.

## O que foi feito

### 1. Type Checking (mypy)

**Antes:** 5 errors em 2 files
**Depois:** 0 errors

| Arquivo | Erro | Correção |
|---------|------|----------|
| `src/evaluation/structured_outputs.py:77,95,102` | `json.loads()` retorna Any, não `dict[str, Any]` | Adicionado `isinstance(result, dict)` guard |
| `src/evaluation/structured_outputs.py:129` | `parsed` type mismatch (`dict[str, Any] \| None` vs `dict[str, Any]`) | `parsed_or_none` temporária com guard |
| `src/quality/service.py:98` | `str \| None` passado onde `str` esperado | `degraded_reason=reason or ""` |

### 2. Code Style (ruff)

**Antes:** 73 errors
**Depois:** 0 errors

| Categoria | Correção |
|-----------|----------|
| Migrations auto-geradas (I001, UP035, UP007, E501) | Adicionado `migrations/*.py` ao extend-exclude do ruff |
| `tests/unit/test_review_repository.py:58` (F841) | Removida variável `r2` não utilizada |
| `src/services/product/claim_ledger.py:156,284` (E501) | Strings longas quebradas em múltiplas linhas |
| `tests/integration/test_postgres_migration.py:77` (E501) | SQL query quebrada em múltiplas linhas |

### 3. Formatação (black)

**Antes:** 5 files would be reformatted (bloqueado por PermissionError no `.pytest_tmp`)
**Depois:** 0 files need reformatting

| Ação | Detalhe |
|------|---------|
| Adicionado `extend-exclude` para `.pytest_tmp*`, `node_modules/`, `.git/` | Evita PermissionError |
| Reformatados 6 arquivos (5 migrations + 1 acceptance test) | `black .` sem alterar semântica |

### 4. Makefile Targets

| Target | Comando | Inclusão |
|--------|---------|----------|
| `test` / `test-unit` | `pytest -m "not (integration or acceptance or e2e or slow or optional or external_service)"` | validate-fast |
| `validate-fast` | lint + format-check + typecheck + test | validate-full |
| `validate-backend` | validate-fast | - |
| `validate-frontend` | ui-lint + ui-build | validate-full |
| `validate-docs` | check_scope.py + check_docs_closure.py | validate-full |
| `validate-full` | validate-fast + validate-docs + validate-frontend | prepare-release |
| `prepare-release` | validate-full + acceptance | - |

### 5. Pytest Markers

Novos markers adicionados ao `pyproject.toml`:

- `unit` — testes isolados (default)
- `integration` — testes de integração
- `acceptance` — Product Golden Path
- `e2e` — Playwright E2E
- `slow` — testes lentos (>5s)
- `optional` — dependências opcionais (rag, llm-judge)
- `external_service` — serviços externos (Qdrant, PostgreSQL)

### 6. Optional Dependencies

`pyproject.toml`:
- `sentence-transformers`: corrigido de `>=5.5.1` (não existe) para `>=2.2.0`
- `migrations/` adicionado ao extend-exclude do ruff

### 7. Playwright E2E Setup

- Documentado em README: `npx playwright install`
- Target `ui-e2e-product` mantido separado (não entra em validate-fast/validate-full)
- Mensagem clara de erro se browser não instalado

## Validação Final

- **mypy**: 0 errors (110 source files)
- **ruff**: 0 errors
- **black**: 217 files left unchanged
- **check_scope.py**: All checks passed
- **check_docs_closure.py**: All closure checks passed
- **Unit tests**: 12 passed (test_output_validation)

## Known Limitations (novas)

- `make validate-full` executa teste unitários que podem levar >60s em Windows — aceitável para validação completa
- Migrations auto-geradas excluídas do ruff (E501, I001, UP007, UP035) por serem código gerado pelo Alembic
- Playwright E2E separado do validate-full por exigir browser binaries
- Python 3.14+ warnings de deprecação do `asyncio.iscoroutinefunction` no pytest-asyncio (não bloqueante)
