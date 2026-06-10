# EVALS — Baseline de Testes e Cobertura

## Testes Unitários

| Módulo | Arquivo | Testes | Status |
|---|---|---|---|
| Schemas | `tests/unit/test_schemas.py` | 4 | ✅ |
| Source Policy | `tests/unit/test_source_policy.py` | 3 | ✅ |
| Fetcher | `tests/unit/test_fetcher.py` | 7 | ✅ |
| Parser | `tests/unit/test_parser.py` | 4 | ✅ |
| Extractor | `tests/unit/test_extractor.py` | 14 | ✅ |
| AI Classifier | `tests/unit/test_classifier.py` | 10 | ✅ |
| Evidence Validator | `tests/unit/test_evidence_validator.py` | 14 | ✅ |
| Defensibility Score | `tests/unit/test_defensibility_score.py` | 6 | ✅ |
| Inception Fit Score | `tests/unit/test_inception_fit_score.py` | 6 | ✅ |
| Production Readiness | `tests/unit/test_production_readiness.py` | 6 | ✅ |
| Composite Ranking | `tests/unit/test_composite_ranking.py` | 9 | ✅ |
| Gap Diagnosis | `tests/unit/test_gap_diagnosis.py` | 14 | ✅ |
| NVIDIA Mapping | `tests/unit/test_nvidia_mapping.py` | 6 | ✅ |
| Gap Taxonomy | `tests/unit/test_gap_taxonomy.py` | 1 | ✅ |
| Pipeline | `tests/unit/test_pipeline.py` | 10 | ✅ |
| Recommendation Engine | `tests/unit/test_recommendation_engine.py` | 22 | ✅ |
| Action Brief | `tests/unit/test_action_brief.py` | 10 | ✅ |
| RAG Ingestion | `tests/unit/test_rag_ingestion.py` | 4 | ✅ |
| RAG Retrieval | `tests/unit/test_rag_retrieval.py` | 6 | ✅ |
| Playbook Retriever | `tests/unit/test_playbook_retriever.py` | 5 | ✅ |
| **Total** | **20 arquivos** | **168** | **100% pass** |

## Cobertura por módulo

| Módulo src/ | Implementado? | Testado? | Testes |
|---|---|---|---|
| `extraction/schemas.py` | ✅ REAL | ✅ | 4 |
| `extraction/extractor.py` | ✅ REAL | ✅ | 14 |
| `scraping/source_policy.py` | ✅ REAL | ✅ | 3 |
| `scraping/fetcher.py` | ✅ REAL | ✅ | 7 |
| `scraping/parser.py` | ✅ REAL | ✅ | 4 |
| `classification/ai_native_classifier.py` | ✅ REAL | ✅ | 10 |
| `validation/evidence_validator.py` | ✅ REAL | ✅ | 14 |
| `scoring/defensibility_score.py` | ✅ REAL | ✅ | 6 |
| `scoring/inception_fit_score.py` | ✅ REAL | ✅ | 6 |
| `scoring/production_readiness.py` | ✅ REAL | ✅ | 6 |
| `scoring/composite_ranking.py` | ✅ REAL | ✅ | 9 |
| `pipeline/run_pipeline.py` | ✅ REAL | ✅ | 10 |
| `briefing/action_brief.py` | ✅ REAL | ✅ | 10 |
| `briefing/schemas.py` | ✅ REAL | ✅ | (via action brief) |
| `recommendation/schemas.py` | ✅ REAL | ✅ | (via recommendation engine) |
| `recommendation/recommendation_engine.py` | ✅ REAL | ✅ | 22 |
| `diagnosis/gap_diagnosis.py` | ✅ REAL | ✅ | 9 |
| `diagnosis/nvidia_mapping.py` | ✅ REAL | ✅ | 6 |
| `config/settings.py` | ✅ REAL | ❌ | 0 |
| `agents/` (9 files) | ❌ STUB | ❌ | 0 |
| `rag/` (5 files) | ✅ REAL | ✅ | 15 |
| `database/` (2 files) | ❌ STUB | ❌ | 0 |
| `evaluation/` (2 files) | ❌ STUB | ❌ | 0 |
| `interface/` (1 file) | ❌ STUB | ❌ | 0 |

## Lacunas de cobertura

- **Integração:** `tests/integration/` vazio — zero testes de integração
- **Evals:** `tests/evals/` vazio — zero avaliações automatizadas
- **Config:** `src/config/settings.py` sem testes

## Critérios de aceite por módulo

| Módulo | Critério | Status |
|---|---|---|
| Schemas | Validação de enums e criação de objetos | ✅ |
| Scraping | HTTP mocked, parser com fallback | ✅ |
| Extractor | Perfil completo, parcial, vazio, sinais AI | ✅ |
| Classifier | 5 níveis + evidência fraca | ✅ |
| Evidence Validator | 14 cenários de fonte/tipo/confiança | ✅ |
| Defensibility Score | 5 cenários + shape test | ✅ |
| Inception Fit Score | 5 cenários + shape test | ✅ |
| Production Readiness | 6 cenários (alto/baixo/sem evidência) | ✅ |
| Composite Ranking | Pesos, redistribuição, motion, ranking | ✅ |
| Gap Diagnosis | 7 gaps + inferência + evidência faltante | ✅ |
| NVIDIA Mapping | Gap conhecido/desconhecido, cobertura total | ✅ |
| Recommendation Engine | 22 testes (ação, prioridade, experimento, per-gap, integração) | ✅ |
| Pipeline | 10 testes (5 existentes + 5 integração: diagnóstico, recomendação, evidência fraca, missing_evidence, shape estendido) | ✅ |
| Action Brief | 10 testes (high-fit, evidência fraca, sem gap, missing evidence, tech sem gap, incertezas, markdown, schema, JSON, low confidence) | ✅ |
| RAG Ingestion | 4 testes (sources, corpus load, chunking metadata, source propagation) | ✅ |
| RAG Retrieval | 6 testes (index, gap, tech, empty, keywords, scores) | ✅ |
| Playbook Retriever | 5 testes (inference gap, agent gap, missing, brief dicts, no-rag) | ✅ |

## Critérios de Qualidade do Desenvolvimento

Estes critérios avaliam a **qualidade do processo de desenvolvimento assistido por IA**, não a qualidade do produto.

| Critério | O que verifica | Como medir |
|----------|---------------|------------|
| Plano salvo | Plano foi versionado em `docs/plans/` antes do build | Verificar se existe arquivo .md para o épico/tarefa |
| Escopo respeitado | Mudanças estão dentro do escopo aprovado | Review Diff: nenhum arquivo fora do escopo |
| Contratos consultados | Contratos foram lidos antes de alterar módulos | Agente declara quais contratos leu (ou justifica por que não) |
| Review Diff executado | Diff foi revisado antes do commit | Log da execução do review_diff.md |
| Obsidian atualizado | Notas de decisão, resumo e limitações foram criadas/atualizadas | Verificar existência de notas em 03 Research/, 04 Decisions/, 02 Project Control/ |
| Decisões registradas | Decisões arquiteturais ou de processo foram registradas | DECISIONS.md ou ADR em docs/adr/ |
| Limitações registradas | Known Limitations foi revisado e atualizado | Diff no arquivo Known Limitations |
| Validações executadas | pytest, ruff, black, mypy rodaram sem erros (ou com erros pre-existentes justificados) | Log dos comandos |
| ERROR_LOG atualizado | Erros relevantes foram registrados | Conteúdo de ERROR_LOG.md (não vazio se houve erros) |
| Alucinação zero | Nenhuma fonte, tecnologia ou feature foi inventada | Revisão manual do diff e do reasoning |
| Feature fantasma zero | Nenhuma feature foi documentada sem ser implementada | Comparar docs com código real |

### Alvos
- **Curto prazo:** 100% dos épicos não triviais terão plano salvo, Review Diff executado, Obsidian atualizado
- **Médio prazo:** Review Diff detecta 0 falsos negativos (nada fora de escopo passa)
- **Longo prazo:** Developer RAG implementado com recall@5 ≥90%

## Métricas aspiracionais (futuras)

- Precision@k para ranking de startups
- Recall@k para cobertura de evidências
- Faithfulness de diagnósticos vs julgamento especialista
- Business usefulness score (survey time NVIDIA)
