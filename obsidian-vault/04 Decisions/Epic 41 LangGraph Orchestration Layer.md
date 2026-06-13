# Epic 41 — LangGraph Orchestration Layer

**Status:** Implementado (2026-06-13)

## Decisão
Construir um workflow runner sequencial determinístico com LangGraph como extra opcional (`[agent-orchestration]`). Runner executa 11 nodes em sequência com retry (max 1), persiste estado em WorkflowRun/WorkflowNodeRun, e expõe API REST.

## Alternativas consideradas
- LangGraph como core dependency (rejeitado — FPB-029 classifica como P3)
- Pure LangGraph sem fallback (rejeitado — LangGraph pode não ser necessário)
- Reescrever serviços existentes como nodes (rejeitado — "nodes apenas wrappers")

## Rationale
- LangGraph opcional mantém core installation leve
- Nodes wrappam serviços existentes via `@_register` decorator
- Retry policy conservativa evita loops infinitos
- `_dump_state()` helper remove `_session` não-serializável antes de JSON dump

## Riscos
- Execução síncrona bloqueia request thread
- LangGraph extra pode divergir do fallback runner
- Node implementations duplicam session management boilerplate

## Validação
36 testes (24 unit + 12 integration). ruff, black, mypy (1 erro pré-existente). Nenhuma regressão.
