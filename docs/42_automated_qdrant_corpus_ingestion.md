# Automated Qdrant Corpus Ingestion

**Epic 18** | **Data:** 2026-06-10

## Objetivo

Criar um script de ingestão automatizada (`scripts/ingest_nvidia_corpus.py`) que lê o corpus local versionado em `data/nvidia_corpus/`, valida, chunka, gera embeddings e faz upsert no Qdrant com payload completo (provenance, hashes, versão, filtros).

## Arquitetura

```
scripts/ingest_nvidia_corpus.py
  ├── 1. Load sources (sources.yaml)
  ├── 2. Scan corpus files
  ├── 3. Validate documents
  ├── 4. Chunk documents (via src/rag/ingestion)
  ├── 5. Generate embeddings (MockEmbeddingProvider | SentenceTransformerProvider)
  ├── 6. Build VectorEntry objects
  ├── 7. Upsert to vector store (Qdrant | InMemory)
  └── 8. Generate ingestion report
```

## CLI

```
scripts/ingest_nvidia_corpus.py [OPCOES]

  --dry-run                    Valida e chunka, nao faz upsert
  --recreate-collection        Drop + recreate collection + indexes
  --skip-existing              Verifica chunk_hash antes de upsert
  --source-id SOURCE_ID       Filtrar por source_id (ex: nim triton)
  --product PRODUCT            Filtrar por product
  --fail-on-validation-error   Exit 1 se validation falhar
  --backend {qdrant,in_memory} Backend (default: qdrant)
  --collection-name NAME       Nome da collection (default: nvidia_corpus)
  --batch-size N               Chunks por batch (default: 32)
  --mock-embeddings            Usar MockEmbeddingProvider
  --report-path PATH           Salvar relatorio em JSON
```

## Dependencias RAG Opcionais

Para gerar embeddings reais durante a ingestao Qdrant, instale o extra RAG:

```bash
pip install -e ".[rag]"
```

O extra e opcional porque `sentence-transformers` so e necessario para
embeddings/RAG. O core do projeto, os testes offline e o modo
`--mock-embeddings` continuam sem essa dependencia.

Modelo padrao: `sentence-transformers/all-MiniLM-L6-v2`.
Esse modelo gera vetores de 384 dimensoes; portanto a collection Qdrant usada
por essa ingestao deve manter `QDRANT_VECTOR_SIZE=384`.

## Payload Schema (por chunk no Qdrant)

| Campo | Tipo | Origem |
|-------|------|--------|
| `chunk_id` | string | `{source_id}_{index:03d}` |
| `source_id` | string | Nome do arquivo `.md` |
| `source_title` | string | `sources.yaml` ou heading `#` |
| `source_url` | string | `sources.yaml` |
| `product` | string | `sources.yaml` |
| `gap_types` | string[] | `sources.yaml` |
| `version` | string | `sources.yaml` (default "1.0") |
| `content_hash` | string | MD5 do `raw_text` completo do documento |
| `chunk_hash` | string | MD5 do conteudo do chunk |
| `collected_at` | string (ISO) | Timestamp da ingestao |
| `document_type` | string | `sources.yaml` (default "nvidia_corpus") |
| `provenance` | object | `{source_url, source_title}` |
| `ingestion_run_id` | string | `run_{timestamp}` |

## Payload Indexes

Criados automaticamente em `QdrantStore._ensure_payload_indexes()`:

- `product` (keyword)
- `gap_types` (keyword)
- `source_id` (keyword)
- `version` (keyword)
- `document_type` (keyword)
- `content_hash` (keyword)

## Estrategia de Idempotencia

- `chunk_id` deterministico: `{source_id}_{indice:03d}` (derivado da ordenacao estavel do corpus)
- `content_hash`: MD5 do `raw_text` completo do documento. Mesmo texto → mesmo hash
- `chunk_hash`: MD5 do conteudo do chunk. Se o chunk nao mudou, o hash e o mesmo
- `--skip-existing`: Antes do upsert, verifica se ja existe ponto com mesmo `chunk_hash`. Se existir, skip
- `--recreate-collection`: Drop + recreate, insere tudo. 100% idempotente
- Sem `--skip-existing` sem `--recreate-collection`: upsert sempre (Qdrant upsert e idempotente por `chunk_id`)

## Schema Extensions (Epic 18)

### VectorEntry (dataclass)
Novos campos opcionais com defaults (backward-compatible):
- `version: str = "1.0"`
- `document_type: str = "nvidia_corpus"`
- `content_hash: str | None = None`
- `chunk_hash: str | None = None`
- `ingestion_run_id: str | None = None`

### RagChunk (Pydantic)
- `version: str = "1.0"`
- `document_type: str = "nvidia_corpus"`
- `content_hash: str | None = None`

### RagSource (Pydantic)
- `version: str = "1.0"`
- `document_type: str = "nvidia_corpus"`

## Relatorio de Ingestao

```json
{
  "ingestion_run_id": "run_20260610_120000",
  "documents_seen": 10,
  "documents_valid": 10,
  "documents_skipped": 0,
  "chunks_created": 50,
  "chunks_upserted": 50,
  "sources_failed": [],
  "validation_errors": [],
  "collection_name": "nvidia_corpus",
  "backend": "qdrant",
  "started_at": "2026-06-10T12:00:00",
  "finished_at": "2026-06-10T12:00:05"
}
```

## Testes

### Unitarios (17)
- `test_content_hash_stable`: Mesmo texto → mesmo hash
- `test_content_hash_different`: Textos diferentes → hashes diferentes
- `test_content_hash_is_md5`: Hash e MD5 de 32 caracteres
- `test_chunk_hash_stable`: Mesmo chunk → mesmo chunk_hash
- `test_chunk_hash_different`: Chunks diferentes → hashes diferentes
- `test_defaults`: Valores padrao do CLI
- `test_dry_run_flag`: Flag --dry-run
- `test_source_id_filter`: Filtro por source-id
- `test_loads_yaml_with_new_fields`: sources.yaml com version/document_type
- `test_all_sources_have_version_and_doc_type`: Todos os sources tem campos obrigatorios
- `test_dry_run_does_not_upsert`: Dry-run nao faz upsert
- `test_ingest_to_in_memory`: Ingestao completa com backend in_memory
- `test_ingest_recreate_collection`: Recreate + ingestao
- `test_payload_contains_provenance`: Payload com campos obrigatorios
- `test_report_counters`: Relatorio com contadores corretos
- `test_report_has_all_fields`: Relatorio tem todos os campos
- `test_report_saved_to_path`: Relatorio salvo em JSON

### Integracao (3, skippable)
- `test_ingest_to_qdrant`: Ingestao em Qdrant real
- `test_ingest_recreate_collection`: Recreate + ingestao em Qdrant
- `test_ingest_idempotent`: Duas execucoes → mesma contagem

## Seguranca

- O script nao executa conteudo do corpus
- O corpus e tratado como dado, nunca como instrucao
- Nenhuma chamada externa durante execucao
- Embeddings sao locais (`sentence-transformers` via extra `rag` ou mock)
- Sem secrets em logs (Qdrant URL pode ter API key, mas nao e logada)
- Sem dependencia de internet

## Manutencao

Para adicionar um novo documento ao corpus:
1. Criar arquivo `.md` em `data/nvidia_corpus/`
2. Adicionar entrada em `sources.yaml` com `version` e `document_type`
3. Para ingestao real em Qdrant, garantir `pip install -e ".[rag]"`,
   `RAG_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2` e
   `QDRANT_VECTOR_SIZE=384`
4. Executar `python scripts/ingest_nvidia_corpus.py` (ou `--source-id <novo_id>`)
