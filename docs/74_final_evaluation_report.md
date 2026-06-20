# Final Evaluation Report — NVIDIA Startup AI Radar

## Readiness Branch Update - 2026-06-19

The evaluation target is now strict product readiness. Verified in the branch:

- Python lint, format, and `mypy src` are green.
- Full `pytest -q --basetemp .pytest_tmp_full` is green with `2085 passed`, `27 skipped`, and `166 warnings`.
- The targeted product test battery passed with `1585 passed, 124 warnings`.
- Focused regression runs after final readiness fixes pass for acceptance, workflow API, product workflow API, workflow runner, pipeline golden evals, answer quality golden evals, and NVIDIA corpus ingestion unit tests.
- Demo dependency, scope, docs-closure, and magic-value guards pass.
- `scripts/scan_magic_values.py --check` reports 0 unregistered productive values; evaluation-only findings are explicitly classified.
- Frontend reproducible install and production build pass.
- Docker Compose PostgreSQL + Qdrant validation passed with product readiness healthy and Qdrant collection `nvidia_corpus` populated with 53 real-embedding points.
- Product Playwright E2E passed against the live local backend (`6 passed`) and screenshots were stored in `docs/screenshots/`.

Remaining before declaring the best-case final product:

- Run `make validate-full` on an environment with GNU Make installed, or publish a Windows-native equivalent target.

**Versão:** 1.0
**Data:** 2026-06-13
**Épico:** 45

## Case Criteria Mapping

### Critério 1: Identificação de Startups Brasileiras AI-Native

**Como o produto atende:**
- Discovery Engine com 6 fontes de dados públicos brasileiros
- AI-native classifier com 5 níveis (NON_AI → AI_NATIVE_SERVICE)
- 30+ keywords de detecção de sinais AI-native
- Signal detection com confidence scoring e evidence excerpts

**Evidências:**
- `tests/unit/test_discovery_signals.py` — 11 testes
- `tests/unit/test_discovery_dedup.py` — 15 testes
- `tests/unit/test_discovery_repository.py` — 15 testes
- `tests/integration/test_discovery_api.py` — 14 testes
- Discovery API endpoints: `/discovery/sources`, `/discovery/manual-seed`, `/discovery/url-list`

### Critério 2: Coleta e Estruturação de Dados Públicos

**Como o produto atende:**
- Scraping policy-compliant (robots.txt, rate-limit, allowlist)
- Extrator estruturado com Pydantic schemas
- Suporte a múltiplas fontes: site oficial, tech blog, LinkedIn, imprensa
- Evidence validation com FACT/INFERENCE/HYPOTHESIS tagging

**Evidências:**
- `tests/unit/test_source_policy.py` — 3 testes
- `tests/unit/test_fetcher.py` — 7 testes
- `tests/unit/test_parser.py` — 4 testes
- `tests/unit/test_extractor.py` — 14 testes
- `tests/unit/test_evidence_validator.py` — 14 testes

### Critério 3: Evidências Rastreáveis

**Como o produto atende:**
- Claim Ledger determinístico com evidence_refs por claim
- Evidence coverage metrics (total/supported/unsupported)
- Human review com append-only audit log
- Provenance tracking em todos os níveis (RAG chunks, evidence, claims)

**Evidências:**
- `tests/unit/test_claim_repository.py` — 12 testes
- `tests/unit/test_claim_ledger.py` — 9 testes
- `tests/integration/test_claim_api.py` — 9 testes
- Claim API endpoints: `GET /analysis-runs/{id}/claims`, `GET /analysis-runs/{id}/evidence-coverage`

### Critério 4: RAG com Documentação NVIDIA

**Como o produto atende:**
- Hybrid RAG: dense embeddings + BM25 sparse + RRF fusion
- Deterministic reranking (composite score + provenance/duplicate/irrelevant penalties)
- Context packing com dedup e limites configuráveis
- Qdrant opcional com payload rico (provenance, version, content hash)
- Corpus versionado com freshness audit
- Citation packaging com source coverage

**Evidências:**
- `tests/unit/test_hybrid_rag.py` — 31 testes
- `tests/unit/test_rag_reranking.py` — 9 testes
- `tests/unit/test_context_packing.py` — 13 testes
- `tests/unit/test_rag_eval_reranking.py` — 11 testes
- `tests/unit/test_corpus_freshness_audit.py` — 11 testes
- `tests/unit/test_qdrant_store.py` — 20 testes

### Critério 5: Recomendação Personalizada

**Como o produto atende:**
- 15 deterministic gap detectors com confidence
- NVIDIA Technology Mapping (gap → tecnologia NVIDIA)
- Recommendation Engine com 4 ações (approach_now → not_recommended)
- Suggested Technical Experiment com hipótese, métrica, duração
- Activation Playbooks com matching por gap_type

**Evidências:**
- `tests/unit/test_gap_diagnosis.py` — 14 testes
- `tests/unit/test_nvidia_mapping.py` — 6 testes
- `tests/unit/test_recommendation_engine.py` — 22 testes
- `tests/unit/test_activation_playbook_loader.py` — 13 testes
- `tests/unit/test_activation_playbook_matcher.py` — 9 testes

### Critério 6: Priorização de Oportunidades

**Como o produto atende:**
- Opportunity Score com 10 componentes ponderados
- 8 tipos de penalidade (claims, evidence, degraded, contraindication, etc.)
- Score tiers: critical, high, medium, low, not_recommended
- Ranked pipeline com filtros, ordenação e paginação
- Evidence coverage e unsupported claim count no ranking

**Evidências:**
- `tests/unit/test_opportunity_score.py` — 43 testes
- `tests/evals/test_pipeline_golden.py` — 38 golden evals
- Opportunity API endpoint: `GET /opportunities`

### Critério 7: Interface Web

**Como o produto atende:**
- 10 views consolidadas: Setup, Capabilities, Discovery, Startups, Opportunities, Workflow, Export, Quality
- Vite + React + TypeScript
- Consome Product API real
- Playwright E2E smoke tests (6 testes)
- Frontend build passa com `npm run build`

**Evidências:**
- `frontend/` — 15+ componentes React
- `tests/e2e/test_product_ui.spec.ts` — 6 Playwright tests
- `npm run build` — tsc + vite build sem erros

### Critério 8: Robustez e Validação

**Como o produto atende:**
- 775+ testes Python (unit, integration, acceptance, golden evals)
- CI/CD: GitHub Actions (ruff, black, mypy, pytest)
- Pre-commit hooks
- Scope check e docs closure validation
- Structured Output Reliability Layer
- Degraded state handling para todos os serviços

**Evidências:**
- `EVALS.md` — baseline completo de testes e cobertura
- `tests/unit/test_structured_outputs.py` — 30 testes
- `tests/unit/test_capability_registry.py` — 6 testes
- `tests/unit/test_config_registry.py` — 9 testes
- `tests/unit/test_readiness_service.py` — 10 testes
- `tests/acceptance/` — Product Golden Path

### Critério 9: Diferencial Competitivo

**Como o produto atende:**
- AI-Native Defensibility Score (6 dimensões) — único no mercado
- Dual Scoring: Defensibility + Inception Fit
- Evidence-backed Opportunity Score com confiança explícita
- Determinístico e auditável (zero alucinação de LLM)
- Activation Dossier com playbooks NVIDIA
- Startups brasileiras como foco primário

**Evidências:**
- `DECISIONS.md` — Decision 009 (Dual Scoring), Decision 007 (Defensibility)
- `docs/11_defensibility_score.md`
- `src/scoring/` — 4 módulos de scoring

## Diferenciais

1. **Determinístico e auditável** — todo score, gap e recomendação tem rastreabilidade explícita. Zero alucinação de LLM.
2. **Dual Scoring** — combina defensibilidade técnica com fit comercial NVIDIA
3. **Evidence-backed** — nada é aceito sem fonte; confiança explícita em cada evidência
4. **Foco Brasil** — fontes brasileiras, classificação AI-native adaptada ao ecossistema local
5. **Modular e testável** — 775+ testes, 19 contratos formais, CI/CD automatizado
6. **RAG híbrido** — dense + sparse + reranking + context packing sem dependência de API externa
7. **Degraded states explícitos** — produto funciona mesmo com serviços opcionais offline

## Limitações

[Lista consolidada no README — Known Limitations section]

## Riscos

| Risco | Impacto | Mitigação |
|---|---|---|
| Qualidade depende de evidência pública | Startups com pouca presença online têm scores baixos | Confidence penalty explicita incerteza |
| Sem validação Windows/macOS | Compatibilidade não testada | CI usa Ubuntu, documentado |
| Sem LLM no core scoring | Menos flexível que julgamento humano | Determinístico = auditável, LLM opcional no futuro |
| Pesos do Opportunity Score fixos | Podem não refletir prioridades reais | Documentados para ajuste futuro |

## Próximos Passos

1. **Human-in-the-loop review** — workflow de revisão humana integrado
2. **Cross-encoder reranking** — alternativa ao reranking determinístico
3. **Professional PDF exports** — além de JSON/Markdown
4. **CI matrix multi-OS** — Windows/macOS/Linux em CI
5. **Auth/roles** — autenticação e autorização multi-usuário
6. **CRM integration** — export para Salesforce/HubSpot
7. **Richer source connectors** — mais fontes de dados brasileiras
8. **LLM judge opcional** — avaliação semântica de qualidade
