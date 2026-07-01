# Motor de Recomendação e Ranking de Oportunidades

## Objetivo

O motor de recomendação transforma evidência, score, gaps técnicos e contexto RAG NVIDIA em recomendações priorizadas e em um score global de oportunidade por startup. O produto final deve ser uma lista ranqueada de startups/oportunidades com score, tier, justificativa e próxima ação.

## Posição no workflow

```text
diagnose_gaps
→ retrieve_nvidia_context
→ enhance_contexts_with_techniques
→ map_nvidia_technologies
→ rank_recommendations
→ rank_with_expected_utility
→ generate_brief
→ run_quality_gates
→ generate_claims
→ match_activation_playbooks
→ generate_activation_dossier
→ run_product_quality
→ write_decision_ledger
```

## Componentes

| Componente | Arquivo | Papel |
|---|---|---|
| Gap mapping | `src/recommendation/nvidia_technology_mapping.py` | transformar gaps em tecnologias candidatas |
| Recommendation engine | `src/recommendation/recommendation_engine.py` | gerar recomendação estruturada |
| Next action enrichment | `src/recommendation/next_action_enrichment.py` | sugerir próxima ação técnica |
| Adaptive ranker | `src/decisioning/adaptive_recommendation_ranker.py` | ranquear recomendações candidatas |
| Expected utility | `src/decisioning/expected_utility_ranker.py` | ordenar por utilidade esperada |
| Evidence-weighted scorer | `src/decisioning/evidence_weighted_scorer.py` | score com incerteza e cobertura |
| Opportunity score | `src/services/product/opportunity_score_service.py` | score global usado no ranking de startups |
| Decision ledger | `src/decisioning/decision_ledger_writer.py` | auditoria de ranking e decisões |

## Tecnologias NVIDIA cobertas

O catálogo ativo deve mapear gaps para tecnologias como:

```text
NVIDIA Inception
NVIDIA API Catalog
CUDA
TensorRT
TensorRT-LLM
Triton Inference Server
NVIDIA NIM
NVIDIA NeMo
NeMo Guardrails
RAPIDS
cuDF
cuML
NVIDIA Riva
NVIDIA Omniverse
NVIDIA Isaac
NVIDIA Clara
MONAI
NVIDIA Morpheus
NVIDIA AI Enterprise
NVIDIA AI Blueprints
```

## Entradas

```text
startup_profile
evidence_items
classification_result
evidence_weighted_scores
gap_diagnosis_summary
nvidia_contexts
rag_contexts_by_gap
claims
quality_gates_result
review_decision/feedback_counts quando houver revisão
```

## Saída por recomendação

Cada recomendação deve preservar:

```text
recommendation_id
gap_id
gap_type
nvidia_technology / technology
technology_category
mapping_score
mapping_confidence
recommendation_priority_score
business_impact
implementation_complexity
risk
confidence
uncertainty
evidence_support
supporting_evidence_ids
supporting_rag_context_ids
production_allowed
blockers
next_best_action
expected_utility
expected_utility_rank
expected_utility_breakdown
```

## Mapeamento gap → tecnologia

O mapeamento usa:

```text
gap_type
gap severity
gap confidence
gap uncertainty
evidence support
RAG topic match
NVIDIA corpus context match
source quality
calibration_decision_ids
production_allowed
```

Uma recomendação não deve ser promovida se:

```text
não houver gap detectado
não houver contexto RAG suficiente
não houver evidência mínima
mapping_confidence estiver abaixo do threshold
uncertainty for alta
decisão de calibração estiver bloqueada
```

## Ranking inicial

O ranking preliminar considera:

```text
business_impact
confidence
implementation_complexity inversa
rag_support
evidence_support
uncertainty penalty
source quality
```

Pesos principais vêm de `config/scoring.yaml`:

```text
priority_score.weights.confidence = 0.30
priority_score.weights.business_impact = 0.25
priority_score.weights.implementation_complexity_inverse = 0.20
priority_score.weights.rag_support = 0.15
priority_score.weights.evidence_support = 0.10
```

## Ranking por utilidade esperada

A etapa `rank_with_expected_utility` converte recomendações e mappings em candidatos com:

```text
technology
business_impact
confidence
implementation_complexity
risk
uncertainty
evidence_support
```

A utilidade esperada deve premiar impacto e confiança e penalizar incerteza, risco e complexidade. A decomposição fica em `expected_utility_breakdown` e no decision ledger.

## Score global de oportunidade

`OpportunityScoreService` calcula um score por `analysis_run` e grava `OpportunityScoreRecord`. Esse score é a base para:

```text
GET /opportunities/ranked
```

Componentes e pesos:

| Componente | Peso |
|---|---:|
| `composite_ranking` | 0.20 |
| `evidence_coverage` | 0.15 |
| `gap_resolution` | 0.12 |
| `nvidia_mapping` | 0.10 |
| `activation_readiness` | 0.10 |
| `dossier_completeness` | 0.10 |
| `quality_score` | 0.08 |
| `claim_support` | 0.07 |
| `review_status` | 0.05 |
| `production_readiness` | 0.03 |

Tiers:

```text
critical: score >= 0.85
high:     score >= 0.70
medium:   score >= 0.50
low:      score >= 0.30
not_recommended: score < 0.30 ou contraindicação forte
```

Penalidades:

```text
unsupported_claims
low_evidence_coverage
critical_unsupported
degraded_states
low_confidence
contraindication
incomplete_data
non_ai_classification
```

## Ranking global de startups

Fluxo correto:

```text
AnalysisRun concluído
→ POST /analysis-runs/{analysis_run_id}/opportunity-score
→ OpportunityScoreRecord persistido
→ GET /opportunities/ranked?limit=50
```

Filtros do ranking global:

```text
min_score
tier
recommended_action
offset
limit
```

A UI não deve exibir apenas uma startup selecionada como resultado principal. O painel de oportunidades deve consumir `GET /opportunities/ranked` para mostrar todas as startups analisadas com seus scores.

## Decision ledger

`write_decision_ledger` escreve decisões em:

```text
data/decision_ledger.csv
```

Decisões gravadas:

```text
score_{run_id}
rank_{run_id}_{idx}
```

Campos importantes:

```text
decision_id
area
decision
alternatives_considered
metrics_used
data_source
benchmark_file
chosen_option
expected_value
confidence
uncertainty
risks
owner
date
status
```


## Técnicas de decisão usadas e como entram no ranking

| Técnica | Implementação | Como entra na decisão |
|---|---|---|
| Gap-to-technology mapping | `src/recommendation/nvidia_technology_mapping.py` | Converte cada gap técnico em tecnologias NVIDIA candidatas e exige suporte por evidência/contexto RAG. |
| Evidence-weighted scoring | `src/decisioning/evidence_weighted_scorer.py` | Calcula score ponderado por valor da feature, peso, qualidade de evidência, cobertura e diversidade de fontes. |
| Uncertainty estimation | saída do scoring e classification | Transforma baixa evidência/alta variância em incerteza explícita, que reduz utilidade esperada. |
| Expected utility | `src/decisioning/expected_utility_ranker.py` | Reordena recomendações penalizando risco, complexidade e incerteza. |
| Feedback learner | `src/decisioning/feedback_learner.py` | Ajusta pesos depois de revisão humana quando há feedback positivo/negativo. |
| Opportunity score | `src/services/product/opportunity_score_service.py` | Consolida análise, evidência, gaps, mappings, dossier, qualidade e claims em um score comparável entre startups. |
| Penalidades | `OpportunityScoreService` | Reduz score por claims sem suporte, baixa cobertura de evidência, estado degradado, non-AI, baixa confiança e dados incompletos. |

Fórmula de utilidade esperada implementada:

```text
utility = clamp(
  expected_value * confidence * (1 - uncertainty) * (0.5 + 0.5 * evidence_support)
  - mean(implementation_complexity, risk)
)
```

Fórmula de scoring ponderado por evidência:

```text
score = sum(clamp(value,0,1) * max(weight,0) * clamp(evidence_quality,0,1))
        / sum(max(weight,0) * clamp(evidence_quality,0,1))

confidence = 0.45*evidence_coverage
           + 0.20*source_diversity
           + 0.25*evidence_quality_mean
           + 0.10*(1 - value_variance)
```

Na prática, isso evita que uma startup seja ranqueada alto apenas por parecer interessante. Ela precisa ter evidência suficiente, gap compatível com tecnologia NVIDIA, recomendação acionável, qualidade mínima e baixo risco relativo.

## Critérios de aceite

1. Há pelo menos uma recomendação por análise concluída quando existe gap validado.
2. Cada recomendação tem suporte de evidência e/ou contexto RAG.
3. `ranked_recommendations` está ordenado e contém decomposição de utilidade.
4. `OpportunityScoreRecord` é criado para cada análise que deve aparecer no ranking.
5. `GET /opportunities/ranked` retorna lista ordenada sem depender de startup hardcoded.
6. Claims críticos sem suporte reduzem score ou bloqueiam recomendação.
7. Decision ledger é escrito ao final do workflow.

## Testes e validação

```bash
pytest -q tests/unit/test_recommendation_engine.py
pytest -q tests/unit/test_nvidia_mapping.py
pytest -q tests/unit/test_nvidia_technology_mapping.py
pytest -q tests/unit/test_workflow_rag_recommendations.py
python scripts/rank_value_candidates.py
python scripts/build_candidate_decision_matrix.py
```
