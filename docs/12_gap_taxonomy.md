# Gap Taxonomy

A taxonomia de gaps técnicos representa os problemas de production AI que o Radar consegue
diagnosticar deterministicamente a partir de sinais públicos.

## Gaps suportados (15)

| Gap | Descricao | Exemplo de sinal |
|---|---|---|
| `external_api_dependency` | Startup depende de API externa (ex.: OpenAI) sem propria infra de inferencia | "gpt", "openai", "api wrapper" |
| `high_inference_cost` | Custo de inferencia elevado sem otimizacao NVIDIA | "high volume inference", "gpu cost" |
| `high_latency` | Latencia alta em tempo real sem aceleracao | "low latency", "real-time", "throughput" |
| `agent_governance_gap` | Falta de guardrails para agentes autonomos | "agent", "autonomous", "multi-agent" |
| `observability_gap` | Ausencia de monitoramento/observabilidade em producao | "monitoring", "observability", "telemetry" |
| `model_evaluation_gap` | IA em producao sem avaliacao sistematica de modelos | "evaluation", "benchmark", "a/b test" |
| `privacy_or_controlled_deployment_gap` | Necessidade de deploy controlado/privacidade sem solucao | "on-prem", "data residency", "air-gapped" |
| `slow_data_pipeline` | Pipeline de dados lenta sem aceleracao GPU | "data pipeline", "etl", "batch processing" |
| `heavy_tabular_processing` | Processamento tabular pesado sem RAPIDS | "tabular", "structured data", "predictive model" |
| `voice_need` | Processamento de voz/fala sem GPU | "voice", "speech", "call center", "stt/tts" |
| `simulation_need` | Necessidade de simulacao/digital twin sem GPU | "simulation", "digital twin", "3d simulation" |
| `computer_vision_need` | Visao computacional sem aceleracao | "computer vision", "image", "object detection" |
| `robotics_need` | Robotica/veiculos autonomos sem NVIDIA | "robot", "robotics", "drone", "ros" |
| `healthcare_compliance_need` | IA em saude sem compliance regulatorio | "healthcare", "hipaa", "medical", "clinical" |
| `ai_cybersecurity_need` | Ciberseguranca com IA sem aceleracao | "cybersecurity", "threat detection", "anomaly detection" |

## Origem

Definido em `src/extraction/schemas.py` como enum `TechnicalGap`.

## Como um gap e diagnosticado

1. Extrator produz `StartupProfile` com sinais do texto coletado
2. Classificador define o nivel AI-native
3. Validador classifica evidencias como FACT/INFERENCE/HYPOTHESIS
4. Cada detector de gap combina:
   - Keywords no texto do perfil
   - Evidencias validadas filtradas por relevancia
   - Cross-reference com scoring (production readiness, defensibility, inception fit)
5. Gap e marcado como:
   - `FACT` se ha evidencia direta + keyword match
   - `INFERRED` se ha keyword match sem evidencia direta
   - `HYPOTHESIS` se nao ha sinal (gap nao detectado)
