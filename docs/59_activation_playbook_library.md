# Activation Playbook Library

## Objetivo
Biblioteca de playbooks de ativação NVIDIA que mapeia gaps técnicos detectados em startups
para ações concretas de aceleração (workshops, POCs, architecture reviews, etc.).

## Arquitetura

### Fluxo
```
YAML Source → load_playbooks() → ActivationPlaybook[]
                                         ↓
GapDiagnosisRecord ──────────────────→ ActivationPlaybookService
NvidiaMappingRecord ────────────────→   .generate_recommendations_for_run()
ClaimRecord ────────────────────────→         ↓
ScoreRecord ────────────────────────→   list[ActivationRecommendationSchema]
ProductReadinessCheck ──────────────→         ↓
                                         .persist_recommendations_for_run()
                                         ActivationRecommendationRecord (DB)
                                         ↓
                                   GET /activation-playbooks
                                   GET /analysis-runs/{id}/activation-recommendations
                                   POST /analysis-runs/{id}/activation-recommendations/generate
```

### Componentes

1. **Playbook Source** (`src/config/playbooks/nvidia_activation_playbooks.yaml`)
   - 10 playbooks cobrindo inferência, latência, agentes, dados, visão, voz, simulação, robótica, segurança, deploy privado
   - Cada playbook: target_gap_types, nvidia_technologies, recommended_motion, implementation_complexity, confidence_rules, output_template

2. **Loader** (`src/playbook/loader.py`)
   - `load_playbooks(path=None)` — carrega e valida YAML; retorna `list[ActivationPlaybook]`
   - Validações: playbook_id único, campos obrigatórios, motions válidos, complexities válidas

3. **Service** (`src/services/product/activation_service.py`)
   - `ActivationPlaybookService` com matching determinístico, confidence scoring, ranking, persist
   - Matching: gap_type detectado está em target_gap_types do playbook
   - Confidence: fórmula com boosts e penalties baseada em gap confidence + mapping + claims + evidencia + degraded
   - Priority: 4 níveis baseados em confidence + expected_value + complexity

4. **Repository** (`src/repositories/activation.py`)
   - `ActivationRecommendationRepository` com CRUD padrão + replace_recommendations_for_analysis_run (delete + bulk create)

5. **API** (`src/api/product_routes.py`)
   - `GET /activation-playbooks` — lista todos os playbooks disponíveis
   - `GET /analysis-runs/{id}/activation-recommendations` — recomendações persistidas
   - `POST /analysis-runs/{id}/activation-recommendations/generate` — gera e persiste recomendações

## Matching Determinístico (v1)

- Um playbook matcha se **pelo menos um** target_gap_type está entre os gaps detectados (detected=True)
- Gaps não detectados são ignorados (não contribuem para match nem confidence)
- Playbook sem match → não é recomendado

## Confidence Score

```
base = avg(confidence_float(gap.confidence) for each matched gap)
+ 0.10 (has_nvidia_mapping)
+ 0.10 (has_supporting_claims)
- 0.15 (evidence_coverage < 0.5)
- 0.20 (has_unsupported_claims)
- 0.10 * min(degraded_count, 3)
= clamp [0.0, 1.0]
```

Map para string: >= 0.7 high, >= 0.4 medium, < 0.4 low.

## Prioridade

- **1**: confidence high AND (expected_value high/very_high OR complexity low/medium)
- **2**: confidence high restante, OR (high value NOT low confidence)
- **3**: confidence medium restante
- **4**: confidence low

## Integração com Analysis Run Lifecycle

Em `ProductService.create_analysis_run_for_startup()`, após o claim ledger:
```python
try:
    act_service = ActivationPlaybookService(session)
    act_service.persist_recommendations_for_run(new_run.id)
except Exception:
    logger.warning(...)
```

Erros são logados e não bloqueiam o fluxo principal.

## Formatos

### Playbook YAML
```yaml
playbooks:
  - playbook_id: latency_optimization
    name: Latency Optimization
    target_gap_types: [high_latency, slow_model_loading]
    nvidia_technologies: [TensorRT, Triton Inference Server, TensorRT-LLM]
    recommended_motion: architecture_review
    implementation_complexity: medium
    confidence_rules:
      requires_gap_match: true
      evidence_coverage_boost: true
      unsupported_claim_penalty: true
      min_evidence_coverage: 0.3
```

## Próximos Passos
- Feedback loop (aceitar/rejeitar recomendação)
- LLM matching (além do determinístico)
- Atualização automática de playbooks via deploy
