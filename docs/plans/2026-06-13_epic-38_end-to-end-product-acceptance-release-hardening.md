# Epic 38 — End-to-End Product Acceptance & Release Hardening

**Data:** 2026-06-13
**Modo:** Build
**Status:** Aprovado

## Objetivo

Criar uma camada de aceitação end-to-end e hardening de release para validar o fluxo completo do produto: setup/readiness → capabilities → startup creation → analysis run → claims/evidence coverage → activation playbook → dossier → quality run → opportunities → export readiness → UI smoke/E2E.

## Escopo

### Criar
- `docs/65_end_to_end_product_acceptance.md` — design doc
- `docs/contracts/product_acceptance_contract.md` — contrato
- `tests/fixtures/product_golden_path/startup.json`
- `tests/fixtures/product_golden_path/expected.json`
- `tests/acceptance/__init__.py`
- `tests/acceptance/test_product_golden_path.py`
- `tests/acceptance/test_no_demo_dependency.py`
- `scripts/product_acceptance_report.py`

### Alterar
- `Makefile` — adicionar acceptance targets
- `pyproject.toml` — adicionar marker acceptance
- `README.md` — seção Quickstart
- `ROADMAP.md` — status Epic 38
- `EVALS.md` — acceptance entries
- `DECISIONS.md` — Decision 044
- `AGENTS.md` — release validation commands
- `tests/e2e/test_product_ui.spec.ts` — expandir E2E

### Fora de escopo
- auth, PDF, MCP, TOON/JTON, router, novas features
- alterações em scoring, RAG retrieval, Qdrant ingestion, recommendation central
- transformar Playwright em make validate padrão
- dados demo como fonte principal

## Product Golden Path

Fluxo de 17 steps validado via FastAPI TestClient. Ver docs/65.

## Critério de pronto

- Product Golden Path implementado e passando
- Fixture de aceitação criada
- No demo dependency guard implementado
- README quickstart atualizado
- Release checklist criada
- Known limitations atualizadas
- Frontend build passa
- Playwright E2E separado implementado
- make validate rápido não roda E2E pesado
- Nenhuma feature nova grande adicionada
