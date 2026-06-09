# NVIDIA Mapping Matrix

Matriz deterministica que mapeia cada `TechnicalGap` para tecnologias NVIDIA candidatas.
Cada mapeamento inclui justificativa tecnica explicando por que a tecnologia endereca o gap.

## Matriz completa (15 gaps, 32 technology candidates)

| Gap | Tecnologias NVIDIA | Justificativa |
|---|---|---|
| `external_api_dependency` | NVIDIA NIM, NVIDIA AI Enterprise | NIM oferece microservicos otimizados para inferencia; AI Enterprise da suporte enterprise para substituir APIs de terceiros |
| `high_inference_cost` | TensorRT-LLM, Triton Inference Server, NVIDIA NIM | TensorRT-LLM otimiza inferencia LLM em GPUs NVIDIA; Triton gerencia multi-modelo eficientemente; NIM empacota modelos otimizados |
| `high_latency` | TensorRT-LLM, Triton Inference Server, NVIDIA NIM | TensorRT-LLM reduz latencia via kernel fusion e quantizacao; Triton permite execucao concorrente e batching dinamico |
| `agent_governance_gap` | NeMo Guardrails, NVIDIA NeMo | NeMo Guardrails prove guardrails programaveis para agentes LLM; NeMo oferece ferramentas para construir e governar agentes |
| `observability_gap` | NVIDIA AI Enterprise | AI Enterprise inclui ferramentas de monitoramento e observabilidade para producao |
| `model_evaluation_gap` | NVIDIA NeMo | NeMo fornece harnesses de avaliacao para benchmarking e teste de LLMs |
| `privacy_or_controlled_deployment_gap` | NVIDIA AI Enterprise, NVIDIA NIM | AI Enterprise suporta deploys seguros on-premise para setores regulados; NIM pode ser deployado on-prem com soberania de dados |
| `slow_data_pipeline` | NVIDIA RAPIDS, cuDF, cuML | RAPIDS (cuDF, cuML) acelera pipelines de dados em GPU para ETL mais rapido |
| `heavy_tabular_processing` | NVIDIA RAPIDS, cuML | RAPIDS acelera processamento tabular e ML em GPU; cuML oferece implementacoes GPU-aceleradas de algoritmos ML |
| `voice_need` | NVIDIA Riva, NVIDIA NIM | Riva oferece speech-to-text e text-to-speech GPU-acelerados; NIM inclui microservicos de voz otimizados |
| `simulation_need` | NVIDIA Omniverse | Omniverse permite simulacao fisicamente precisa e criacao de digital twins |
| `computer_vision_need` | NVIDIA AI Enterprise, NVIDIA TensorRT, NVIDIA NIM | AI Enterprise inclui pipelines CV otimizados com TensorRT; TensorRT otimiza inferencia CV em tempo real; NIM fornece microservicos CV pre-construidos |
| `robotics_need` | NVIDIA Isaac, NVIDIA Omniverse | Isaac oferece simulacao, treinamento e deploy roboticos; Omniverse permite simulacao fotorrealista para treinamento |
| `healthcare_compliance_need` | NVIDIA Clara, MONAI, NVIDIA AI Enterprise | Clara fornece frameworks de IA para saude com compliance; MONAI oferece imagem medica com suporte regulatorio; AI Enterprise garante deploys HIPAA-compliant |
| `ai_cybersecurity_need` | NVIDIA Morpheus | Morpheus oferece pipeline de ciberseguranca AI GPU-acelerado |

## Implementacao

A matriz esta definida em `src/diagnosis/nvidia_mapping.py` como o dicionario `_TECH_MATRIX`.

## Evolucao

Esta matriz e um ponto de partida controlado e deve evoluir com fontes NVIDIA validadas.
Cada nova tecnologia NVIDIA ou alteracao de mapeamento deve ser registrada em DECISIONS.md.
