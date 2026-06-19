"""Todos os parâmetros quantitativos do projeto em um único lugar.

Cada constante documenta:
- rationale: por que este valor e não outro
- source: de onde veio (heurística, paper, config, etc.)
- impact: o que acontece se mudar
"""

from __future__ import annotations

from typing import Any

# =========================================================================
# CONFIDENCE → float mapping
# =========================================================================
# rationale: Mapeamento determinístico para operações numéricas.
#   high=1.0 (máximo), medium=0.6 (meio), low=0.3 (mínimo confiável).
# source: Escolha heurística — intervalos iguais de 0.3 entre níveis.
# impact: Afeta todos os scores ponderados por confiança.
CONFIDENCE_FLOAT_MAP: dict[str, float] = {
    "high": 1.0,
    "medium": 0.6,
    "low": 0.3,
}

# =========================================================================
# CONFIDENCE → factor (para scoring com ConfidenceLevel enum)
# =========================================================================
# rationale: Similar a CONFIDENCE_FLOAT_MAP, mas usado nos módulos de score.
#   high=1.0, medium=0.7 (ligeiramente acima do default), low=0.4.
# source: Derivado empiricamente durante primeiros experimentos.
# TODO: Unificar com CONFIDENCE_FLOAT_MAP — diferença de 0.1 em medium.
CONFIDENCE_SCORE_FACTORS: dict[str, float] = {
    "high": 1.0,
    "medium": 0.7,
    "low": 0.4,
}

# =========================================================================
# Confidence thresholds (para classificação high/medium/low)
# =========================================================================
# rationale: >=0.7 é "high" (suficientemente próximo de 1), >=0.4 "medium".
# source: Convenção comum em sistemas de scoring.
CONFIDENCE_THRESHOLDS = {"high_min": 0.7, "medium_min": 0.4}

# =========================================================================
# Classification → base score
# =========================================================================
# rationale: Cada nível AI-native mapeia para score base 0-85.
#   NON_AI=0, AI_ASSISTED=25, AI_ENABLED=50, AI_NATIVE=80, AI_NATIVE_SERVICE=85.
# source: Derivado heuristicamente — gaps regulares de 25-30 entre níveis,
#   com teto em 85 (não 100) para permitir contribuição de outras dimensões.
CLASSIFICATION_TO_BASE_SCORE: dict[str, float] = {
    "non_ai": 0,
    "ai_assisted": 25,
    "ai_enabled": 50,
    "ai_native": 80,
    "ai_native_service": 85,
}

# =========================================================================
# Priority score weights (para recomendações NVIDIA)
# =========================================================================
# rationale: Confiança (30%) e business impact (25%) são os drivers principais.
#   Complexidade reduz score (20%), RAG suporta (15%), evidência (10%).
# source: Pesos determinados heuristicamente — a confiança deve dominar
#   porque recomendações com baixa confiança não devem ser priorizadas.
# weight_sum = 1.0  # validated
PRIORITY_SCORE_WEIGHTS: dict[str, float] = {
    "confidence": 0.30,
    "business_impact": 0.25,
    "implementation_complexity_inverse": 0.20,
    "rag_support": 0.15,
    "evidence_support": 0.10,
}

# =========================================================================
# Opportunity score weights (composite ranking)
# =========================================================================
# rationale: Production readiness (35%) domina porque reflete maturidade real.
#   Defensibilidade (30%) e inception fit (25%) são secundários.
#   Classificação (10%) é o baseline.
# source: Pesos ajustados durante validação com golden dataset.
# weight_sum = 1.0  # validated
OPPORTUNITY_SCORE_WEIGHTS: dict[str, float] = {
    "defensibility": 0.30,
    "inception_fit": 0.25,
    "production_readiness": 0.35,
    "classification": 0.10,
}

# =========================================================================
# Confidence penalty on missing data
# =========================================================================
# rationale: Se faltam dados em um componente, penalizamos o composite em 15%.
# source: Heurístico — penalidade alta o suficiente para ser notada,
#   baixa o suficiente para não zerar o score de startups promissoras.
CONFIDENCE_PENALTY_ON_MISSING: float = 0.15

# =========================================================================
# Production readiness dimension weights
# =========================================================================
# rationale: Real users (30%) e scale inference (30%) têm o mesmo peso porque
#   ambos são indicadores fortes de prontidão. Privacidade (20%) e dados (20%).
# source: Pesos derivados de discussão com domain experts (NVIDIA team).
# weight_sum = 1.0  # validated
PRODUCTION_READINESS_WEIGHTS: dict[str, float] = {
    "real_users": 0.30,
    "scale_inference": 0.30,
    "privacy_governance": 0.20,
    "data_infrastructure": 0.20,
}

# =========================================================================
# Defensibility score dimension weights
# =========================================================================
# rationale: AI core (25%) é o fator mais importante — sem core AI não há
#   defensibilidade. Dados proprietários (20%) e workflow (15%) são barreiras
#   de entrada. Real usage (15%) e replication (15%) mostram tração.
#   NVIDIA fit (10%) é bônus.
# source: Pesos derivados de docs/00_case_plan.md.
# weight_sum = 1.0  # validated
DEFENSIBILITY_WEIGHTS: dict[str, float] = {
    "ai_core": 0.25,
    "proprietary_data": 0.20,
    "workflow_integration": 0.15,
    "real_usage": 0.15,
    "replication_barrier": 0.15,
    "nvidia_fit": 0.10,
}

# =========================================================================
# Inception fit score dimension weights
# =========================================================================
# rationale: Gap taxonomy (35%) domina porque startups com gaps claros
#   têm fit imediato com NVIDIA. Vertical alignment (25%) mostra relevância
#   de mercado. Maturidade técnica (20%) e revenue potential (20%).
# source: Pesos derivados de docs/00_case_plan.md.
# weight_sum = 1.0  # validated
INCEPTION_FIT_WEIGHTS: dict[str, float] = {
    "gap_taxonomy": 0.35,
    "vertical_alignment": 0.25,
    "technical_maturity": 0.20,
    "revenue_potential": 0.20,
}

# =========================================================================
# AI-native keyword boosts (para detecção de sinais em texto)
# =========================================================================
# rationale: Keywords específicas NVIDIA (Triton, TensorRT, RAPIDS, NeMo, CUDA)
#   recebem boost 0.25. LLM, generative AI recebem 0.20.
#   ML, DL, NLP, GPU, inference recebem 0.15. TensorFlow, PyTorch recebem 0.10.
#   Data science keywords recebem 0.05 (sinal fraco).
# source: Valores heuristicamente calibrados — NVIDIA keywords são sinais
#   mais fortes porque indicam adoção direta do ecossistema.
# impact: Cap total de 0.6 (MAX_SIGNAL_BOOST) para evitar dominância de
#   uma única fonte com muitas keywords.
AI_NATIVE_KEYWORD_BOOSTS: dict[str, float] = {
    "nvidia_specific": 0.25,
    "llm_generative": 0.20,
    "ml_dl_nlp_gpu": 0.15,
    "framework_mlops": 0.10,
    "data_science": 0.05,
}

# =========================================================================
# Max signal boost cap
# =========================================================================
# rationale: Nenhuma fonte pode contribuir mais que 0.6 para o confidence score
#   via keywords. Isso garante que mesmo textos com muitas keywords NVIDIA
#   não dominem o score sem outros sinais (nome, website, etc.).
MAX_SIGNAL_BOOST: float = 0.6

# =========================================================================
# Discovery confidence weights (para calculate_confidence)
# =========================================================================
# rationale: Ter nome da startup (0.3) é o sinal mais forte.
#   Ser manual_seed (0.2) adiciona confiança. Website (0.1) e
#   fonte confiável (0.1) complementam. Signal_contribution é variável.
# source: Heurístico — nome + website + fonte confiável = base 0.5,
#   signal_contribution pode adicionar até 0.6 (cap).
DISCOVERY_CONFIDENCE_WEIGHTS: dict[str, float] = {
    "has_name": 0.3,
    "has_website": 0.1,
    "is_manual_seed": 0.2,
    "source_reliable": 0.1,
}

# =========================================================================
# Source quality scores (para source_quality_score)
# =========================================================================
# rationale: Official_site (1.0) é a fonte mais confiável.
#   News (0.8) tem credibilidade jornalística. Founder_profile (0.7).
#   Blog (0.6) é menos confiável. Job_post (0.5) e directory (0.4).
# source: Heurístico baseado em confiabilidade relativa de tipos de fonte.
SOURCE_QUALITY_SCORES: dict[str, float] = {
    "official_site": 1.0,
    "news": 0.8,
    "founder_profile": 0.7,
    "blog": 0.6,
    "job_post": 0.5,
    "directory": 0.4,
}

# =========================================================================
# Gap business impact map
# =========================================================================
# rationale: Privacy gaps (0.9) têm maior impacto porque bloqueiam indústrias
#   reguladas. Inference cost (0.8) e governance (0.8) são críticos para
#   produção. Latency (0.7), external API (0.7), cybersecurity (0.7).
#   Data pipeline (0.6), computer vision (0.6). Heavy tabular (0.5),
#   voice (0.5), robotics (0.5), simulation (0.5), observability (0.5).
#   Model evaluation (0.4) é o menor porque é pós-produção.
# source: Heurístico — priorização NVIDIA baseada em impacto no negócio.
GAP_BUSINESS_IMPACT_MAP: dict[str, float] = {
    "external_api_dependency": 0.7,
    "high_inference_cost": 0.8,
    "high_latency": 0.7,
    "slow_data_pipeline": 0.6,
    "heavy_tabular_processing": 0.5,
    "computer_vision_need": 0.6,
    "voice_need": 0.5,
    "agent_governance_gap": 0.8,
    "privacy_or_controlled_deployment_gap": 0.9,
    "ai_cybersecurity_need": 0.7,
    "healthcare_compliance_need": 0.8,
    "robotics_need": 0.5,
    "simulation_need": 0.5,
    "model_evaluation_gap": 0.4,
    "observability_gap": 0.5,
}

# =========================================================================
# Keyword lists per gap type
# =========================================================================
# rationale: Cada gap tem keywords associadas para detecção heurística.
# source: Compilado de documentação técnica NVIDIA e análise de startups.
GAP_KEYWORD_DICT: dict[str, list[str]] = {
    "external_api_dependency": ["gpt", "openai", "api dependency", "api wrapper", "llm api"],
    "high_inference_cost": [
        "high volume inference", "inference cost", "gpu cost", "expensive inference"
    ],
    "high_latency": ["low latency", "real-time", "throughput", "latency"],
    "agent_governance_gap": ["agent", "autonomous", "multi-agent", "ai agent", "agentic"],
    "privacy_or_controlled_deployment_gap": [
        "privacy", "on-prem", "controlled deployment", "data residency"
    ],
    "ai_cybersecurity_need": ["cybersecurity", "threat detection", "security"],
    "healthcare_compliance_need": ["healthcare", "compliance", "hipaa"],
    "robotics_need": ["robot", "robotics"],
    "simulation_need": ["simulation", "digital twin"],
    "computer_vision_need": ["computer vision", "image", "video"],
    "voice_need": ["voice", "speech", "audio"],
    "slow_data_pipeline": ["data pipeline", "data processing", "etl"],
    "heavy_tabular_processing": ["tabular", "structured data"],
    "model_evaluation_gap": ["evaluation", "model eval", "benchmark"],
    "observability_gap": ["monitoring", "observability", "telemetry"],
}

# =========================================================================
# Knowledge base signal boosts (para detect_ai_native_signals agrupado)
# =========================================================================
# rationale: Mesmo racional de AI_NATIVE_KEYWORD_BOOSTS, mas estruturado
#   como lista de (regex, label, boost) para uso direto em signals.py.
# source: Derivado de AI_NATIVE_KEYWORD_BOOSTS + associação de keywords.
KNOWLEDGE_BASE_SIGNAL_BOOSTS: list[tuple[str, str, float]] = [
    (r"\bAI\b", "Mentions AI/Artificial Intelligence", 0.15),
    (r"\bIA\b", "Mentions IA (Inteligência Artificial)", 0.15),
    (r"\binteligência artificial\b", "Mentions Inteligência Artificial", 0.15),
    (r"\binteligencia artificial\b", "Mentions Inteligência Artificial", 0.15),
    (r"\bmachine learning\b", "Mentions Machine Learning", 0.15),
    (r"\baprendizado de máquina\b", "Mentions Aprendizado de Máquina", 0.15),
    (r"\bLLM\b", "Mentions LLM (Large Language Model)", 0.20),
    (r"\blarge language model", "Mentions Large Language Model", 0.20),
    (r"\bgenerative AI\b", "Mentions Generative AI", 0.20),
    (r"\bIA generativa\b", "Mentions IA Generativa", 0.20),
    (r"\bdeep learning\b", "Mentions Deep Learning", 0.15),
    (r"\bcomputer vision\b", "Mentions Computer Vision", 0.15),
    (r"\bvisão computacional\b", "Mentions Visão Computacional", 0.15),
    (r"\bNLP\b", "Mentions NLP", 0.15),
    (r"\bprocessamento de linguagem natural\b", "Mentions PLN", 0.15),
    (r"\bneural network", "Mentions Neural Networks", 0.15),
    (r"\bredes neurais\b", "Mentions Redes Neurais", 0.15),
    (r"\bmodel serving\b", "Mentions Model Serving", 0.20),
    (r"\binference\b", "Mentions Inference", 0.15),
    (r"\bGPU\b", "Mentions GPU", 0.20),
    (r"\btensorflow\b", "Mentions TensorFlow", 0.10),
    (r"\bpytorch\b", "Mentions PyTorch", 0.10),
    (r"\btransformers?\b", "Mentions Transformer Architecture", 0.15),
    (r"\bautomação inteligente\b", "Mentions Intelligent Automation", 0.10),
    (r"\bintelligent automation\b", "Mentions Intelligent Automation", 0.10),
    (r"\bTriton\b", "Mentions NVIDIA Triton Inference Server", 0.25),
    (r"\bTensorRT\b", "Mentions NVIDIA TensorRT", 0.25),
    (r"\bRAPIDS\b", "Mentions NVIDIA RAPIDS", 0.25),
    (r"\bNeMo\b", "Mentions NVIDIA NeMo", 0.25),
    (r"\bcuda\b", "Mentions CUDA", 0.20),
    (r"\bdata science\b", "Mentions Data Science", 0.05),
    (r"\bciência de dados\b", "Mentions Ciência de Dados", 0.05),
]

# =========================================================================
# NVIDIA tech keywords (para has_nvidia_tech)
# =========================================================================
NVIDIA_KEYWORD_BOOSTS: dict[str, float] = {
    "NVIDIA TensorRT": 0.25,
    "NVIDIA Triton Inference Server": 0.25,
    "NVIDIA RAPIDS": 0.25,
    "NVIDIA NeMo": 0.25,
    "CUDA": 0.20,
}

# =========================================================================
# Discovery thresholds
# =========================================================================
DISCOVERY_MAX_SOURCES: int = 10
MAX_SEARCH_DEPTH: int = 2

# =========================================================================
# Rate limiting (para scraping)
# =========================================================================
# rationale: 2 requests/sec, 1 concorrente — conservador para evitar bloqueio.
# source: Política padrão de polite crawling.
DISCOVERY_RATE_LIMIT: dict[str, int] = {
    "requests_per_second": 2,
    "concurrent_requests": 1,
}

# =========================================================================
# Workflow thresholds (para agent orchestration)
# =========================================================================
WORKFLOW_THRESHOLDS: dict[str, Any] = {
    "max_evidence_retries": 3,
    "min_rag_contexts": 1,
    "min_evidence_items": 1,
    "min_recommendations": 1,
    "min_supported_claims": 1,
    "rag_required": True,
}

# =========================================================================
# Quality gate thresholds
# =========================================================================
QUALITY_GATE_THRESHOLDS: dict[str, Any] = {
    "unsupported_critical_claims_max": 0,
    "blockers_max": 0,
    "evidence_items_min": 1,
    "rag_contexts_min": 1,
    "recommendations_min": 1,
}

# =========================================================================
# Inception fit — no evidence factor
# =========================================================================
NO_EVIDENCE_FACTOR: float = 0.3

# =========================================================================
# Validation
# =========================================================================

_WEIGHT_SETS: dict[str, dict[str, float]] = {
    "PRIORITY_SCORE_WEIGHTS": PRIORITY_SCORE_WEIGHTS,
    "OPPORTUNITY_SCORE_WEIGHTS": OPPORTUNITY_SCORE_WEIGHTS,
    "PRODUCTION_READINESS_WEIGHTS": PRODUCTION_READINESS_WEIGHTS,
    "DEFENSIBILITY_WEIGHTS": DEFENSIBILITY_WEIGHTS,
    "INCEPTION_FIT_WEIGHTS": INCEPTION_FIT_WEIGHTS,
}


def validate_all_weight_sets() -> dict[str, float]:
    """Validate that all weight sets sum to 1.0 (±1e-6 tolerance).

    Returns a dict mapping set name to its sum for inspection.
    """
    results: dict[str, float] = {}
    for name, weights in _WEIGHT_SETS.items():
        total = sum(weights.values())
        results[name] = round(total, 6)
        if abs(total - 1.0) > 1e-6:
            raise ValueError(
                f"Weight set '{name}' sums to {total}, expected 1.0. "
                f"Values: {weights}"
            )
    return results
