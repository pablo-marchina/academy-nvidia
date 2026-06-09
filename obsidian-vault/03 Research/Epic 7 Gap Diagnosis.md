---
type: epic
status: completed
date: 2026-06
---

# Epic 8 — Gap Diagnosis + NVIDIA Mapping

## Objetivo
Diagnosticar production AI gaps tecnicos e mapear tecnologias NVIDIA candidatas.

## Modulos criados
- `src/diagnosis/gap_diagnosis.py` — 15 detectores de gap, 902 linhas
- `src/diagnosis/nvidia_mapping.py` — matriz de mapeamento gap → tecnologias com justificativas
- `src/diagnosis/schemas.py` — GapWithEvidence, NvidiaTechnologyCandidate, GapDiagnosisResult
- `src/diagnosis/__init__.py` — re-exports

## Modulos removidos (duplicados)
- `src/recommendation/nvidia_mapping.py` — versao simplificada sem justificativas (redundante)
- `src/recommendation/gap_taxonomy.py` — apenas `tuple(TechnicalGap)` (redundante)

## Testes
- 14 testes gap diagnosis (10 gaps individuais + e2e + missing evidence + inferred)
- 6 testes nvidia mapping (gap conhecido/desconhecido, cobertura total de 15 gaps)
- 1 teste gap taxonomy
- Total: 21 testes

## Cobertura de gaps testados individualmente
- external_api_dependency ✅
- high_inference_cost ✅
- high_latency ✅ (novo)
- agent_governance_gap ✅
- observability_gap ✅ (novo)
- slow_data_pipeline ✅ (novo)
- voice_need ✅
- computer_vision_need ✅
- robotics_need ✅
- healthcare_compliance_need ✅
- ai_cybersecurity_need ✅ (novo)
- privacy_or_controlled_deployment_gap ✅ (novo)

## Decisoes
- Gap diagnosis NAO integrado ao pipeline (Decisao 014)
- Mapping inclui justificativa textual para cada tecnologia candidata
- Schemas separados em pacote dedicado src/diagnosis/

## Links
- [[../04 Decisions/Decision 014 Gap Diagnosis Independent]]
- [[../../docs/12_gap_taxonomy.md]]
- [[../../docs/13_nvidia_mapping_matrix.md]]
