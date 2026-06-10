# Epic 11 — Product RAG / Playbook Retrieval

**Resumo:** Módulo `src/rag/` implementado com chunking determinístico por headings `##`, índice in-memory lexical por gap_type e technology, scoring por keyword-match, e orquestração via PlaybookRetriever.

## Entregas

- `src/rag/schemas.py` — 6 schemas Pydantic (RagSource, RagDocument, RagChunk, RetrievalQuery, RetrievedContext, PlaybookRetrievalResult)
- `src/rag/ingestion.py` — Markdown → chunks com metadados preservados
- `src/rag/retrieval.py` — ChunkIndex in-memory, retrieve, retrieve_by_gap_type, retrieve_by_technology
- `src/rag/playbook_retriever.py` — PlaybookRetriever (retrieve_for_gaps, retrieve_for_brief)
- `data/nvidia_corpus/` — 10 documentos Markdown mapeados para 15 TechnicalGap × 32 NVIDIA technologies

## Corpus

| Fonte | Gaps | Tecnologia |
|-------|------|------------|
| nim.md | external_api_dependency, high_inference_cost, high_latency | NVIDIA NIM |
| tensorrt_llm.md | high_inference_cost, high_latency | TensorRT-LLM |
| triton.md | high_inference_cost, high_latency | Triton Inference Server |
| nemo_guardrails.md | agent_governance_gap | NeMo Guardrails |
| rapids.md | slow_data_pipeline, heavy_tabular_processing | NVIDIA RAPIDS |
| riva.md | voice_need | NVIDIA Riva |
| omniverse.md | simulation_need | NVIDIA Omniverse |
| isaac.md | robotics_need | NVIDIA Isaac |
| clara_monai.md | healthcare_compliance_need | Clara / MONAI |
| morpheus.md | ai_cybersecurity_need | NVIDIA Morpheus |

## Decisões

- Zero novas dependências (apenas PyYAML 6.0.3, já existente)
- Zero embeddings — retrieval puramente lexical
- Corpus manual, versionado, testável — sem scraping
- RAG enriquece, nunca decide
- Brief funciona sem RAG (sem crash)

## Testes

- 15 testes unitários (4 ingestion + 6 retrieval + 5 playbook)
- Total do projeto: 168 testes, 20 arquivos
