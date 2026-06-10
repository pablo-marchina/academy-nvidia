# Decision 023 — Qdrant Persistent Vector Store (Adapter Pattern)

**Epic:** 15
**Date:** 2026-06-10

## Context
O `InMemoryVectorStore` era funcional para desenvolvimento e testes, mas não persistia dados entre sessões. Qdrant já estava no `pyproject.toml` e no `docker-compose.yml`, mas não havia código de integração. As funções de retrieval (`semantic_retrieve`, `hybrid_retrieve`, `run_rag_pipeline`) tipavam `InMemoryVectorStore` diretamente, impedindo substituição por outro backend.

## Decision
Extrair interface `VectorStore(ABC)` de `InMemoryVectorStore`, criar `QdrantStore(VectorStore)` com lazy connection, payload rico (11 campos, incluindo provenance), e filtros server-side. Todas as funções de retrieval passam a aceitar `VectorStore` (polimórficas). Qdrant é opcional — o default continua sendo `InMemoryVectorStore`.

## Alternatives Considered
- Manter `InMemoryVectorStore` como tipo concreto e adicionar conversão ad-hoc (acoplamento maior)
- Usar composição em vez de herança (mais complexo, sem ganho)
- Ignorar Qdrant (corpus continuaria volátil)

## Rationale
Adapter pattern com ABC permite que o restante do código ignore o backend. Lazy connection evita dependência de Qdrant em import time. Payload rico prepara o sistema para ingestão futura automatizada.

## Risks
- QdrantStore não faz fallback automático — caller precisa capturar `QdrantConnectionError`
- Testes de integração requerem `QDRANT_TEST_URL`

## Validation
20 testes unitários (mockam qdrant-client, sem servidor). 9 testes integração (skippable). 306 testes legados passam (retrocompatibilidade total).

## Status
Implementado no Epic 15.
