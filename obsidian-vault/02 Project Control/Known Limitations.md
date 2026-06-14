# Known Limitations

*Ultima revisao: Junho 2026*

## Pipeline

- Pipeline usa heuristicas deterministicas, nao LLM, para scoring e diagnostico
- Scraping coleta de uma unica URL publica — sem crawling em escala
- Gap Diagnosis e NVIDIA Mapping estao integrados ao pipeline.

## RAG e Recomendacao

- Product RAG Epic 13: semantic/hybrid retrieval usa MockEmbeddingProvider nos testes (nao captura relacoes semanticas reais)
- Answer Quality Eval Epic 23 e deterministico e baseado em padroes/cobertura; nao e LLM judge semantico e nao prova entailment completo
- Answer Quality JUnit Epic 23.1 expoe contadores operacionais do pytest; nao adiciona novas metricas semanticas
- SentenceTransformerProvider requer o extra opcional `rag` (`pip install -e ".[rag]"`) para instalar sentence-transformers
- Qdrant ingestion com `sentence-transformers/all-MiniLM-L6-v2` requer `QDRANT_VECTOR_SIZE=384`
- Reranking deterministico usa pesos fixos (RerankingConfig) — pode nao ser otimo para todos os gaps/tecnologias
- Context packing tem limites configurados (per-tech=2, per-gap=3, global=5) — pode descartar contextos relevantes em casos de borda
- Sem cross-encoder reranking (backlog)
- Vector store e in-memory (sem persistencia entre sessoes — Qdrant-ready via QdrantStore adapter opcional no Epic 15)
- Recommendation Engine implementado e integrado ao pipeline (Epic 9.1)
- RAG pipeline integrado como Step 11 opcional — sem suporte a contextos multi-turno ou consultas interativas
- QdrantStore nao faz fallback automatico para in-memory em caso de erro de conexao (caller deve capturar QdrantConnectionError)
- Embeddings reais de RAG requerem sentence-transformers via extra opcional `rag`; testes continuam usando MockEmbeddingProvider sem download de modelo

- Scores dependem da qualidade e cobertura das evidencias publicas disponiveis
- Confianca das evidencias e atribuida heuristicamente, nao por modelo aprendido
- Sistema nao prova uso interno real de AI — apenas estrutura sinais publicos
- `recommended_motion` e sugestao preliminar baseada em regras deterministicas

## Testes

- Product API tem testes de integracao isolados com SQLite temporario.
- 38 golden evals automatizados (Epic 17) — cobrem pipeline completa offline
- 9 answer quality evals automatizados (Epic 23) — cobrem qualidade final do Action Brief/RAG offline
- `config/settings.py` sem testes

## Infraestrutura

- Sem human-in-the-loop implementado
- Analysis runs executam de forma sincrona; nao ha job queue externa.
- Migracoes versionadas (Alembic) e validacao PostgreSQL foram implementadas no Epic 30; SQLite e o padrao local
- CI/CD implementado via GitHub Actions (ruff, black, mypy, pytest), pre-commit hooks e Docker Compose
- Demo artifacts removidos do fluxo produto (Epic 31); produto usa entidades persistidas

## Claim Ledger (Epic 32)

- `evidence_refs` armazenado como JSON column — sem FK enforcement para tabela de evidencias
- Idempotencia via delete+regenerate — pode causar janela de vazio durante regeneracao
- Cobertura de evidencia usa mapping simples (confidence -> float) sem weighted scoring
- Geracao de claims e deterministica (sem LLM extraction) — pode perder claims implicitas em texto livre
- Sem notificacao automatica para baixa cobertura de evidencia
- Sem endpoints para batch review de multiplas claims

## Activation Playbook Library (Epic 33)

- Matching v1 puramente deterministico — nao captura gaps semanticamente similares (ex: "voice_need" vs "audio_processing")
- Confidence usa formula fixa — sem aprendizado de feedback
- Idempotencia via delete+regenerate — possivel janela de vazio
- Auto-generate no lifecycle silencia erros (catch + log)
- Evidence_refs nas recomendacoes e JSON column — sem enforced FK
- Playbooks lidos de YAML (muda apenas via deploy) — sem hot-reload
- Sem feedback loop para aceitar/rejeitar recomendacao
- Sem LLM matching (planejado para v2)

## Activation Dossier (Epic 34)

- Dossier generation is deterministic from persisted records — no LLM extraction or summarization
- Idempotent by default (POST returns existing) — use `?force=true` to regenerate with new version
- Dossier does NOT auto-update when a review decision is submitted; caller must POST with `force=true`
- Export integration deferred — `ExportRecord` can reference `dossier_id` in future but not yet implemented
- No PDF export of dossier Markdown
- Dossier excludes RAG retrieval context — focuses on structured product records only
- Readiness checks are non-blocking — they appear as risks in the dossier JSON but never prevent generation
- Markdown rendering is plain text only — no PDF, no HTML

## Documentacao

- Scoring docs incompletas (inception fit, production readiness, composite ranking sem docs individuais)
- Obsidian vault tem estrutura mas sem conteudo populado (parcialmente resolvido no Epic 7.2)

## Workspace de Desenvolvimento

- Developer RAG implementado apenas como fundacao documental — sem vector DB
- Prompts de workflow criados no Epic 7.2 mas ainda nao testados em uso real
- Plan artifacts obrigatorios a partir do Epic 7.2 — epicos anteriores nao tem planos versionados
- Contratos de desenvolvimento criados no Epic 7.2 — precisam ser mantidos atualizados com o codigo
- Output Validation Gate e estrutural/contratual; nao substitui revisao humana, entailment semantico ou Answer Quality Eval

- Source sync script (Epic 19) only downloads from allowlisted URLs — no automatic discovery of new NVIDIA documentation pages
- Source sync depends on URL stability in source_allowlist.yaml — 404s are detected but not auto-resolved
- Sync script requires explicit manual promote step (`--promote` or `promote_sources=true`); schedule never promotes sources.
- Sync script does not ingest into Qdrant; real ingestion is handled only by explicit corpus maintenance input or manual ingest command.
- Test coverage: 49 mocked tests — real integration with NVIDIA docs is not tested in CI
- Corpus freshness audit now runs in the safe corpus maintenance schedule, but stale content is not yet rendered as an Action Brief warning.
- Existing Qdrant collections must be reingested to receive lifecycle payload fields
- Stale corpus context is audit-visible but not yet rendered as an Action Brief warning

## Epic 44 — Product UI

- Discovery view candidates list limited to first 100 (no pagination)
- Workflow view is read-only (no UI for creating new workflow runs)
- Export view provides curl commands but does not trigger actual export creation from the UI
- No React Router — navigation uses local state in App.tsx (no deep-linking, no browser back/forward)
- No frontend unit tests — only Playwright E2E smoke tests (6 tests) cover the UI
- Quality view wraps existing QualitySummaryPanel — requires /product/quality-report endpoint
