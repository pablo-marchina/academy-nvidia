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
| Gap Diagnosis | `tests/unit/test_gap_diagnosis.py` | 9 | ✅ |
| NVIDIA Mapping | `tests/unit/test_nvidia_mapping.py` | 6 | ✅ |
| Gap Taxonomy | `tests/unit/test_gap_taxonomy.py` | 1 | ✅ |
| Pipeline | `tests/unit/test_pipeline.py` | 5 | ✅ |
| **Total** | **15 arquivos** | **112** | **100% pass** |

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
| `pipeline/run_pipeline.py` | ✅ REAL | ✅ | 5 |
| `diagnosis/gap_diagnosis.py` | ✅ REAL | ✅ | 9 |
| `diagnosis/nvidia_mapping.py` | ✅ REAL | ✅ | 6 |
| `recommendation/gap_taxonomy.py` | ✅ REAL | ✅ | 1 |
| `config/settings.py` | ✅ REAL | ❌ | 0 |
| `agents/` (9 files) | ❌ STUB | ❌ | 0 |
| `rag/` (4 files) | ❌ STUB | ❌ | 0 |
| `database/` (2 files) | ❌ STUB | ❌ | 0 |
| `evaluation/` (2 files) | ❌ STUB | ❌ | 0 |
| `interface/` (1 file) | ❌ STUB | ❌ | 0 |

## Lacunas de cobertura

- **Integração:** `tests/integration/` vazio — zero testes de integração
- **Evals:** `tests/evals/` vazio — zero avaliações automatizadas
- **Config:** `src/config/settings.py` sem testes
- **Pipeline não chama gap_diagnosis:** módulo existe mas não integrado

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
| Pipeline | Ordem, evidência fraca, raw text, shape | ✅ |

## Métricas aspiracionais (futuras)

- Precision@k para ranking de startups
- Recall@k para cobertura de evidências
- Faithfulness de diagnósticos vs julgamento especialista
- Business usefulness score (survey time NVIDIA)
