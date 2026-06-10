# Documento 39 — Qdrant Persistent Vector Store

**Data:** 2026-06-10
**Épico:** 15 — Persistent Vector Store with Qdrant
**Status:** Implementado e validado

## Objetivo

Adicionar suporte opcional a Qdrant local como vector store persistente para chunks do corpus NVIDIA, mantendo fallback in-memory/lexical e preservando todos os quality gates.

## Arquitetura

```
src/rag/
├── vector_store.py      # VectorStore (ABC) + InMemoryVectorStore (existente)
├── qdrant_store.py      # QdrantStore(VectorStore) + QdrantConfig + factory
├── semantic_retrieval.py # usa VectorStore (polimórfico)
└── hybrid_retrieval.py   # usa VectorStore (polimórfico)
```

### VectorStore (ABC)

Interface abstrata que define o contrato para add/remove/clear/search com filtros opcionais por `product`, `gap_type`, `source_id`, `version`, `document_type`.

### InMemoryVectorStore (herda de VectorStore)

Implementação dict-backed existente — inalterada funcionalmente, apenas passa a herdar de `VectorStore`.

### QdrantStore (herda de VectorStore)

Implementação via `qdrant-client` com lazy connection, criação automática de collection, e payload rico com proveniência.

## Configuração

| Variável | Default | Descrição |
|---|---|---|
| `RAG_VECTOR_BACKEND` | `in_memory` | `in_memory` ou `qdrant` |
| `QDRANT_URL` | `http://localhost:6333` | URL do servidor Qdrant |
| `QDRANT_API_KEY` | (vazio) | API key |
| `QDRANT_COLLECTION` | `nvidia_corpus` | Nome da collection |
| `QDRANT_VECTOR_SIZE` | `384` | Dimensão dos vetores |
| `RAG_EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Modelo local de embeddings RAG |

## Collection Schema

| Propriedade | Valor |
|---|---|
| `collection_name` | `nvidia_corpus` (configurável) |
| `vectors.size` | 384 (configurável, deve bater com o embedding provider) |
| `vectors.distance` | Cosine |
| `hnsw_config` | Default Qdrant |

## Payload Schema

| Campo | Tipo | Indexado | Origem |
|---|---|---|---|
| `chunk_id` | `str` | ✅ keyword | `RagChunk.chunk_id` |
| `source_id` | `str` | ✅ keyword | `RagChunk.source_id` |
| `source_title` | `str` | ❌ | `RagChunk.title` |
| `source_url` | `str` | ❌ | `RagChunk.url` |
| `product` | `str` | ✅ keyword | `RagChunk.product` |
| `gap_types` | `list[str]` | ✅ keyword | `RagChunk.gap_types` |
| `version` | `str` | ✅ keyword | Fixo `"1.0"` |
| `content_hash` | `str` | ❌ | `hashlib.md5(content)` |
| `collected_at` | `str` (ISO 8601) | ❌ | `datetime.now(UTC)` |
| `document_type` | `str` | ✅ keyword | Fixo `"nvidia_corpus"` |
| `provenance` | `dict` | ❌ | `{"source_url": ..., "source_title": ...}` |

## Estratégia de Fallback

```
Pipeline → run_rag_pipeline()
  ├── vector_store=QdrantStore
  │   ├── Qdrant disponível → busca semântica Qdrant
  │   └── QdrantConnectionError → NOT IMPLEMENTED YET (futuro: InMemory fallback)
  ├── vector_store=InMemoryVectorStore (size>0) → semantic/hybrid normal
  ├── vector_store=InMemoryVectorStore (size==0) → lexical puro
  └── vector_store=None → lexical puro
```

Atualmente o QdrantStore não faz fallback automático — se configurado e indisponível, levanta `QdrantConnectionError`. O calling code pode capturar e trocar para `InMemoryVectorStore`.

## Testes

### Unitários (20 testes, sem Qdrant)

`tests/unit/test_qdrant_store.py`:
- lazy connection
- connection error
- add_entry / add_entries (payload serialization, provenance)
- remove_entry, clear, get_entry
- size property
- search basic, empty, all filter types, combined filters, no filters
- payload round-trip provenance
- factory defaults

### Integração (9 testes, skippable)

`tests/integration/test_qdrant_rag_pipeline.py`:
- upsert + search round-trip
- filter by product, gap_type, source_id
- remove_entry, clear, get_entry
- provenance preservation
- connection error when unavailable

Skip: todos pulam quando `QDRANT_TEST_URL` não está definida.

## Como Habilitar Qdrant

1. Instalar dependencias opcionais de embeddings RAG:
   ```bash
   pip install -e ".[rag]"
   ```
2. Iniciar Qdrant: `docker compose up qdrant -d`
3. Configurar ambiente:
   ```bash
   set RAG_VECTOR_BACKEND=qdrant
   set QDRANT_URL=http://localhost:6333
   set QDRANT_COLLECTION=nvidia_corpus
   set QDRANT_VECTOR_SIZE=384
   set RAG_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
   ```
   `QDRANT_VECTOR_SIZE=384` deve bater com o modelo padrao
   `sentence-transformers/all-MiniLM-L6-v2`, que gera vetores de 384 dimensoes.
4. Rodar ingestão manual (futuro script):
   ```python
   from src.rag.qdrant_store import build_qdrant_store
   from src.rag.ingestion import load_and_chunk_corpus
   from src.rag.embeddings import SentenceTransformerProvider
   store = build_qdrant_store()
   emb = SentenceTransformerProvider()
   chunks = load_and_chunk_corpus()
   entries = [VectorEntry(...embedding=emb.embed(c.content)...) for c in chunks]
   store.add_entries(entries)
   ```
5. Pipeline usará Qdrant automaticamente quando `vector_store=QdrantStore(...)` for passado.

## Limitações

- QdrantStore não faz fallback automático para in-memory em caso de erro de conexão
- Nenhum script de ingestão automatizada incluído
- Testes de integração requerem `QDRANT_TEST_URL`
- Payload version fixo em `"1.0"` (sem versionamento incremental)
- Embeddings reais exigem o extra opcional `rag`; o core continua instalavel sem `sentence-transformers`
