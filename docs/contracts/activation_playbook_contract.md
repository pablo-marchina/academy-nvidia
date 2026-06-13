# Contract: Activation Playbook

## Versão
1.0.0 — 2026-06-12

## Propósito
Gerenciar playbooks de ativação NVIDIA, fazer match determinístico com gaps detectados,
ranquear por confiança, persistir recomendações e expor via API REST.

## Dependências
- `src/playbook/loader.py` (load_playbooks)
- `src/playbook/schemas.py` (ActivationPlaybook, ActivationPlaybookMatch, ActivationRecommendationSchema)
- `src/repositories/activation.py` (ActivationRecommendationRepository)
- `src/database/models.py` (ActivationRecommendationRecord)
- `src/services/product/degraded.py` (playbook readiness checks)
- `src/services/product/activation_service.py` (ActivationPlaybookService)

## Inputs
### load_playbooks(path: Optional[Path]) -> list[ActivationPlaybook]
- path: caminho para arquivo YAML (default: `src/config/playbooks/nvidia_activation_playbooks.yaml`)
- Valida: playbook_id único, target_gap_types não vazio, recommended_motion válido, etc.

### ActivationPlaybookService.generate_recommendations_for_run(analysis_run_id: str)
- Lê GapDiagnosisRecord, NvidiaMappingRecord, ClaimRecord, ScoreRecord, ProductReadinessCheck do analysis_run
- Retorna lista de dicts com match, confidence, priority, reasoning

### ActivationPlaybookService.persist_recommendations_for_run(analysis_run_id: str)
- Chama generate_recommendations_for_run e persiste via ActivationRecommendationRepository.replace_recommendations_for_analysis_run
- Retorna lista de dicts persistidos

## Outputs
### GET /activation-playbooks
```json
{
  "playbooks": [
    {
      "playbook_id": "str",
      "name": "str",
      "description": "str",
      "target_gap_types": ["str"],
      "nvidia_technologies": ["str"],
      "recommended_motion": "str",
      "implementation_complexity": "str",
      "expected_value": "str",
      "prerequisites": ["str"]
    }
  ],
  "total": 10
}
```

### GET /analysis-runs/{id}/activation-recommendations
```json
{
  "items": [
    {
      "id": "str",
      "analysis_run_id": "str",
      "playbook_id": "str",
      "playbook_name": "str",
      "matched_gap_types": ["str"],
      "matched_claim_ids": ["str"],
      "nvidia_technologies": ["str"],
      "technical_experiment": "str",
      "success_metrics": ["str"],
      "recommended_motion": "str",
      "priority": 1,
      "confidence": "high",
      "reasoning": "str",
      "evidence_refs": [{}],
      "risks": ["str"],
      "next_step": "str",
      "created_at": "ISO datetime",
      "updated_at": "ISO datetime"
    }
  ],
  "total": 3,
  "offset": 0,
  "limit": 50
}
```

### POST /analysis-runs/{id}/activation-recommendations/generate
```json
{
  "recommendations": [<mesmo schema do GET>],
  "total": 3
}
```

## Regras de Negócio

### Matching
- Um playbook matcha se pelo menos um `target_gap_type` está presente entre os gaps detectados (detected=True) do analysis_run
- Gaps não detectados (detected=False) são ignorados

### Confidence
- Base: average dos confidence_to_float dos gaps matchados
- Boost +0.10 se existe NvidiaMappingRecord para ao menos um gap matchado
- Boost +0.10 se existe ClaimRecord com used_in_mapping=True para ao menos um gap matchado
- Penalty -0.15 se evidence_coverage < min_evidence_coverage (default 0.5)
- Penalty -0.20 se existem unsupported claims (UNSUPPORTED_CRITICAL_CLAIM readiness)
- Penalty -0.10 * min(degraded_count, 3) para outros readiness checks degradados
- Clamping final: [0.0, 1.0]
- Conversão para string: >= 0.7 → high, >= 0.4 → medium, else low

### Priority
- 1: confidence high AND (high_or_very_high_value OR implementation_complexity in (low, medium))
- 2: confidence high AND not priority 1, OR (medium/very_high/high value AND not low confidence)
- 3: confidence medium AND not priority 2
- 4: confidence low

### Recommended Motion
Valores válidos: technical_workshop, proof_of_concept, architecture_review, training_acceleration, hackathon, nvidia_inception, deep_dive_assessment, scalability_assessment, migration_plan

### Implementation Complexity
Valores válidos: low, medium, high, very_high

## Evidência
- matched_gap_types: preenchido com gap_types detectados que triggeram o match
- matched_claim_ids: preenchido com claim_ids relacionados
- nvidia_technologies: herdado do playbook source (interpolado com mapping real se disponível)
- evidence_refs: referências para gaps, scores, mappings usados no match
- reasoning: explicação textual de por que o playbook foi recomendado

## Erros
- 404: analysis_run não encontrado
- 422: parâmetros inválidos (offset/limit)
- 500: erro interno durante geração (logado, não propaga)

## Limitações Conhecidas
- Matching v1 puramente determinístico; sem LLM ou embedding similarity
- Confidence usa regras fixas; sem aprendizado de feedback
- Idempotência via delete+regenerate (possível janela de vazio)
- Auto-generate no lifecycle silencia erros (catch + log)
- Evidence_refs é JSON column; sem enforced FK
- Playbooks lidos de YAML (muda apenas via deploy); sem hot-reload

## Playbooks Disponíveis (v1)
| ID | Nome | Gaps Alvo | Tecnologias NVIDIA |
|----|------|-----------|-------------------|
| inference_cost_optimization | Inference Cost Optimization | high_inference_cost | NIM, Triton Inference Server, TensorRT |
| latency_optimization | Latency Optimization | high_latency, slow_model_loading | TensorRT, Triton, TensorRT-LLM |
| agent_governance | Agent Governance & Guardrails | production_readiness_gap, security_gap | NeMo Guardrails, NeMo Evaluator |
| data_pipeline_acceleration | Data Pipeline Acceleration | slow_data_pipeline, heavy_tabular_processing | RAPIDS, cuDF, cuML |
| computer_vision_acceleration | Computer Vision Acceleration | low_defensibility, no_moat | CV-CUDA, DALI, VPI |
| voice_ai | Voice AI & Audio | voice_need | NeMo, Riva, Parakeet |
| simulation_digital_twins | Simulation & Digital Twins | simulation_gap | Isaac Sim, Omniverse, Modulus |
| robotics | Robotics & Autonomous Machines | robotics_gap | Isaac ROS, Isaac Perceptor, JetPack |
| cybersecurity_ai | Cybersecurity AI | security_gap | Morpheus, cuDF, DALI |
| private_controlled_deployment | Private & Controlled Deployment | data_privacy_gap, production_readiness_gap | NeMo, NIM, Fleet Commander |
