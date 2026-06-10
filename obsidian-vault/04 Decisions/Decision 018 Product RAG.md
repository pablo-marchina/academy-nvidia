# Decision 018 — Product RAG minimalista e determinístico

**Status:** Implementado no Epic 11
**Data:** 2026-06-09

## Contexto

O Epic 11 requeria um módulo de RAG para recuperar snippets de documentação NVIDIA para enriquecer Startup Action Briefs. Restrições: zero novas dependências, zero embeddings, zero chamadas externas, zero alterações nos módulos existentes.

## Decisão

Criar `src/rag/` como módulo independente com:
- Chunking determinístico por headings `##`
- Índice in-memory lexical por gap_type e technology name
- Scoring baseado em keyword match ratio
- Orquestração via PlaybookRetriever
- Corpus manual de 10 documentos Markdown em `data/nvidia_corpus/`

Regra fundamental: RAG enriquece mas nunca decide. O Action Brief funciona normalmente sem contexto RAG.

## Alternativas consideradas

- **Qdrant + embeddings:** Rejeitado por excesso de complexidade para MVP
- **LangGraph:** Rejeitado por zero novas dependências
- **Scraping docs.nvidia.com:** Rejeitado por risco de violação de robots.txt
- **Integração no pipeline principal:** Rejeitado para preservar separação de responsabilidades

## Riscos

- Corpus manual pode desatualizar
- Retrieval lexical perde contexto semântico
- Sem embeddings, não há matching difuso (sinônimos, paráfrases)

## Validação

- 15 testes unitários (4 ingestion + 6 retrieval + 5 playbook)
- Corpus verificado contra `_TECH_MATRIX` (15 gaps) e `_EXPERIMENT_TEMPLATES` (14 templates)
- Brief funciona sem RAG (testado: `test_brief_continues_without_rag`)
