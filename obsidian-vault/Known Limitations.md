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
- Retrieval puramente lexical — sem embeddings, sem matching semântico.
- Corpus manual em `data/nvidia_corpus/` — sem ingestão automatizada.
- Relevance scoring simples (keyword match) — sem reranking.
- Sem cross-chunk ranking ou query expansion.
- Nenhum teste com corpus real da documentação NVIDIA.

## RAG Evaluation
- Métricas não medem relevância semântica (apenas lexical).
- Golden queries manuais — mudanças no corpus podem exigir atualização.
- Sem métricas agregadas entre queries (ex: mean average precision).

## Geral
- Nenhum teste de integração com dados reais.
- Nenhum teste de avaliação (evals) automatizado.
- Config (src/config/settings.py) sem testes.
- Módulos agents/, database/, evaluation/, interface/ são stubs não implementados.
