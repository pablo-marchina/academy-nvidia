# Known Limitations

## Briefing
- Startup Action Brief é gerado a partir de dados sintéticos (PipelineResult construído com perfis de teste). Nenhum teste com dados reais de startup brasileira foi executado.
- Seção "Suggested Technical Experiment" só aparece quando há APPROACH_NOW — briefs de baixa confiança omitem essa seção.
- Markdown renderer não suporta customização de template (template fixo).
- Nenhuma exportação PDF implementada.

## Pipeline
- Pipeline usa dados sintéticos nos testes. Validação com dados reais de scraping é futura.
- missing_evidence é populado mas nem sempre cobre todos os módulos (alguns módulos não reportam missing_evidence).
- recommended_motion pode ser "lack_evidence_more_research" mesmo para startups com sinais fortes se o perfil tiver confidence_score baixo.

## RAG
- Corpus manual em `data/nvidia_corpus/` — sem ingestão automatizada.
- Semantic/hybrid retrieval usa `MockEmbeddingProvider` nos testes (não captura relações semânticas reais).
- `SentenceTransformerProvider` requer `sentence-transformers` (~500MB) — não instalado por padrão.
- Sem cross-encoder reranking (deferred para backlog).
- Sem query expansion ou sinônimos.
- Nenhum teste com corpus real da documentação NVIDIA.
- Vector store é in-memory (sem persistência entre sessões — Qdrant-ready).

## RAG Evaluation
- Golden queries manuais — mudanças no corpus podem exigir atualização.
- Sem métricas agregadas entre queries (ex: mean average precision).
- Comparação multi-modo usa mock embeddings — não valida qualidade semântica real.

## Geral
- Nenhum teste de integração com dados reais.
- Nenhum teste de avaliação (evals) automatizado.
- Config (src/config/settings.py) sem testes.
- Módulos agents/, database/, evaluation/, interface/ são stubs não implementados.
