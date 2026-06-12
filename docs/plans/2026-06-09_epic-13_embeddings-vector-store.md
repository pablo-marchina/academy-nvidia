> **ARCHIVED:** Historical plan artifact. Preserved for reference only. Current product direction is in Epics 28-31 and docs/54_final_product_backlog.md.

# Epic 13 — Embeddings + Vector Store Retrieval

**Data**: 2026-06-09
**Status**: Aprovado e implementado

## Objetivo

Evoluir o Product RAG de retrieval puramente lexical para **híbrido (lexical + semântico)** com fallback, mantendo o retrieval determinístico existente intacto.

## Arquitetura

```
src/rag/
├── embeddings.py           # EmbeddingProvider abstrato + MockEmbeddingProvider + SentenceTransformerProvider
├── vector_store.py         # InMemoryVectorStore com cosine similarity e filtros
├── semantic_retrieval.py   # semantic_retrieve() — embedding + vector search + filtros
├── hybrid_retrieval.py     # hybrid_retrieve() — RRF fusion lexical + semântico
├── schemas.py              # EmbeddingConfig (opcional)
├── retrieval.py            # Inalterado (lexical fallback mantido)
└── playbook_retriever.py   # Inalterado (Action Brief funciona sem vector store)

src/evaluation/
├── rag_eval_schemas.py     # + RetrievalMode, ModeEvalResult, RagEvalComparison
└── rag_eval.py             # + run_mode_eval(), run_comparison_eval(), format_comparison_summary()
```

## Decisões

| Decisão | Escolha | Justificativa |
|---------|---------|---------------|
| Vector store | In-memory (dict + cosine similarity) | Zero dependências externas; testes rápidos; Qdrant-client já instalado mas não exigido |
| Embedding provider | Abstrato com mock para testes | Testes determinísticos sem API key ou download de modelo |
| Modelo default | `all-MiniLM-L6-v2` (sentence-transformers) | Leve (384d, ~80MB), boa relação qualidade/performance |
| Fusão híbrida | RRF (Reciprocal Rank Fusion) | Simples, robusta, não requer calibração de pesos |
| Fallback | Lexical puro se vector store vazio | Action Brief funciona sem vector store |

## Arquivos criados/modificados

### Criados
- `src/rag/embeddings.py`
- `src/rag/vector_store.py`
- `src/rag/semantic_retrieval.py`
- `src/rag/hybrid_retrieval.py`
- `tests/unit/test_rag_embeddings.py`
- `tests/unit/test_semantic_retrieval.py`
- `tests/unit/test_hybrid_retrieval.py`
- `tests/unit/test_rag_eval_semantic.py`
- `docs/37_embeddings_vector_store.md`

### Modificados
- `src/evaluation/rag_eval_schemas.py` — + RetrievalMode, ModeEvalResult, RagEvalComparison
- `src/evaluation/rag_eval.py` — + run_mode_eval, run_comparison_eval, format_comparison_summary
- `src/rag/__init__.py` — exportar novas classes
- `docs/contracts/rag_contract.md` — atualizar invariantes
- `ROADMAP.md` — Epic 13 como concluída
- `EVALS.md` — novo baseline
- `DECISIONS.md` — Decision 020
- `obsidian-vault/` — backfill

## Critério de pronto

- [x] semantic retrieval funciona offline nos testes
- [x] hybrid retrieval funciona com fallback lexical
- [x] provenance é preservado
- [x] filtros por gap/product/source_id funcionam
- [x] quality gates comparam lexical/semantic/hybrid
- [x] nenhuma chamada externa necessária nos testes
- [x] docs e evals foram atualizados
- [x] recommended_motion não é alterado por RAG
- [x] pytest passa
- [x] ruff check . passa
- [x] black --check . passa
- [x] mypy src passa

