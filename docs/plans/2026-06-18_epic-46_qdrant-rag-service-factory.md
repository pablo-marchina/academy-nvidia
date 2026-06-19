# Plan: Qdrant RagService Factory — Produção RAG com Vector Store Real

## Objective

Criar `QdrantRagService` — factory que monta `QdrantStore` + `SentenceTransformerProvider` como implementação concreta do protocolo `RagService`, e integrá-la no `retrieve_nvidia_context` via injeção de dependência. Bloquear produção se Qdrant/corpus/embedding não estiver pronto. Manter `ChunkIndex` lexical como fallback para dev/test.

## Context Read

- `.ai/project_context.md`
- `AGENTS.md`
- `docs/contracts/` (verificar se existem contratos RAG)
- `src/agents/interfaces.py` — protocolo `RagService`
- `src/agents/nvidia_rag_agent.py` — implementação atual com `ChunkIndex`
- `src/agents/graph.py` — nó `_retrieve_nvidia_context` e injeção
- `src/rag/qdrant_store.py` — `QdrantStore(VectorStore)` existente
- `src/rag/embeddings.py` — `EmbeddingProvider`, `SentenceTransformerProvider`
- `src/rag/semantic_retrieval.py` — `semantic_retrieve()`
- `src/rag/hybrid_retrieval.py` — `hybrid_retrieve()`
- `src/rag/retrieval.py` — `ChunkIndex`
- `src/rag/vector_store.py` — `VectorStore` ABC, `InMemoryVectorStore`
- `src/rag/rag_pipeline.py` — `run_rag_pipeline()` orquestração existente
- `src/quality/decision_calibration_registry.py` — decisões RAG calibradas

## Relevant Files

### Criar
- `src/rag/rag_service_factory.py` — `QdrantRagService`, `build_rag_service()`

### Modificar
- `src/agents/interfaces.py` — adicionar parâmetros opcionais `vector_store` e `embedding_model` ao `RagService`
- `src/agents/nvidia_rag_agent.py` — usar `vector_store` + `embedding_model` se fornecidos, fallback lexical
- `src/agents/graph.py` — passar `RagService` real via factory no production build
- `tests/unit/test_qdrant_rag_service.py` — testes da factory

## Scope

1. Criar `QdrantRagService` que implementa `RagService` protocol usando `QdrantStore` + `SentenceTransformerProvider`
2. Validar dependências na inicialização (Qdrant reachable, collection exists, embedding model carregável)
3. Bloquear produção (`production_allowed=False`) se dependências não estiverem prontas
4. Modificar `retrieve_nvidia_context` para aceitar `vector_store` + `embedding_model` opcionais
5. Usar `semantic_retrieve()` quando ambos forem fornecidos, `ChunkIndex.retrieve()` como fallback
6. Integrar no `_build_graph_with_services` do `graph.py`
7. Suporte a Docker local (localhost:6333) com fallback lexical quando Qdrant não disponível

## Out of Scope

- Pipeline de ingestão (load → chunk → embed → upsert) — será épico separado
- `hybrid_retrieve` calibrado — ativado depois da ingestão validada
- Testes de integração com Qdrant real (exigem Docker) — apenas testes unitários mockados agora
- Reranking, context packing — já existem em `rag_pipeline.py`, fora do escopo do RAG node

## Proposed Implementation

1. **Criar `rag_service_factory.py`** — `QdrantRagService` class + `build_rag_service()` factory
   - Construtor recebe `QdrantConfig` (ou lê de env vars)
   - `_validate_dependencies()`: conecta Qdrant, verifica collection, carrega embedding model
   - `__call__` implementa `RagService` protocol: usa `semantic_retrieve()` por gap
   - Fallback: se Qdrant vazio ou embedding falha, retorna status `blocked_qdrant_unavailable`
2. **Modificar `interfaces.py`** — adicionar `vector_store` e `embedding_model` opcionais ao protocolo
3. **Modificar `nvidia_rag_agent.py`** — `_retrieve_for_gap` aceita `vector_store` + `embedding_model`, usa `semantic_retrieve()` quando presente
4. **Modificar `graph.py`** — `_build_graph_with_services` detecta `RAG_VECTOR_BACKEND=qdrant` e constrói `QdrantRagService`
5. **Criar `test_qdrant_rag_service.py`** — testes com `MockEmbeddingProvider` + `InMemoryVectorStore`

## Tests/Validations

```bash
python -m pytest tests/unit/test_qdrant_rag_service.py -v
python -m pytest tests/unit/test_langgraph_product_graph.py -v
python -m pytest tests/unit/test_rag_gap_retrieval.py -v
python -m pytest tests/unit/test_decision_calibration_registry.py -v
ruff check src/agents/nvidia_rag_agent.py src/rag/rag_service_factory.py src/agents/graph.py
mypy src
```

## Risks

| Risk | Mitigation |
|------|-----------|
| Qdrant não disponível em dev | Fallback lexical automático. Testes usam InMemoryVectorStore. |
| Embedding model (`SentenceTransformer`) lento para carregar | Lazy loading no `__call__`, não no construtor. Cache de modelo. |
| Mudança no protocolo `RagService` quebra mocks existentes | Parâmetros são opcionais (`=None`), compatibilidade reversa mantida. |
| Dependência `qdrant-client` não instalada | ImportError capturado, retorna blocked com mensagem clara. |

## Definition of Done

- [ ] `QdrantRagService` criado com validação de dependências
- [ ] `retrieve_nvidia_context` aceita `vector_store` + `embedding_model` opcionais
- [ ] Fallback lexical quando Qdrant/embedding não disponível
- [ ] Graph node usa `RagService` real via factory quando configurado
- [ ] Testes unitários da factory com mocks
- [ ] `pytest` passa sem erros
- [ ] `ruff check .` passa sem erros
- [ ] `mypy src` passa sem erros

## End-of-Epic Closure Checklist

- [ ] `pytest` passa sem erros.
- [ ] `ruff check .` passa sem erros.
- [ ] `black --check .` passa sem erros.
- [ ] `mypy src` passa sem erros.
- [ ] `README.md` atualizado com Current Capabilities e Known Limitations.
- [ ] `ROADMAP.md` atualizado com status real do épico.
- [ ] `DECISIONS.md` atualizado com decisões arquiteturais do épico.
- [ ] `EVALS.md` atualizado com baseline de testes e cobertura.
- [ ] `ERROR_LOG.md` revisado e atualizado se houve erros.
- [ ] `docs/` — documentação relevante atualizada ou criada.
- [ ] `obsidian-vault/` — backfill realizado (decisão, resumo, limitações).
- [ ] Nenhuma dependência nova foi adicionada sem justificativa.
- [ ] Nenhuma feature fantasma foi documentada.

---

*Gerado em: 2026-06-18*
*Modo: Plan → Artifact → Build → Review → Commit*
