"""Startup scoring — ai_native_score and nvidia_fit_score with calibration gating.

Produces normalised scores in [0, 1] when all required calibration
decisions are available and calibrated. Blocks otherwise with
``score_status="blocked_uncalibrated_scoring"``.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from src.quality.decision_calibration_registry import (
    DecisionCalibrationRecord,
    get_project_decision_inventory,
    validate_decision_for_production,
)

# ── Decision IDs ──────────────────────────────────────────────────────────────

AI_NATIVE_WEIGHTS_DECISION_ID = "ai_native_score.weights"
AI_NATIVE_THRESHOLD_DECISION_ID = "ai_native_score.production_threshold"
AI_NATIVE_UNCERTAINTY_DECISION_ID = "ai_native_score.uncertainty_penalty"

NVIDIA_FIT_WEIGHTS_DECISION_ID = "nvidia_fit_score.weights"
NVIDIA_FIT_THRESHOLD_DECISION_ID = "nvidia_fit_score.production_threshold"
NVIDIA_FIT_UNCERTAINTY_DECISION_ID = "nvidia_fit_score.uncertainty_penalty"

REQUIRED_DECISIONS_AI_NATIVE: list[str] = [
    AI_NATIVE_WEIGHTS_DECISION_ID,
    AI_NATIVE_THRESHOLD_DECISION_ID,
    AI_NATIVE_UNCERTAINTY_DECISION_ID,
]

REQUIRED_DECISIONS_NVIDIA_FIT: list[str] = [
    NVIDIA_FIT_WEIGHTS_DECISION_ID,
    NVIDIA_FIT_THRESHOLD_DECISION_ID,
    NVIDIA_FIT_UNCERTAINTY_DECISION_ID,
]

REQUIRED_CALIBRATION_DECISIONS: list[str] = list(set(REQUIRED_DECISIONS_AI_NATIVE + REQUIRED_DECISIONS_NVIDIA_FIT))

# ── Keyword lists for ai_native features ─────────────────────────────────────

_AI_SIGNAL_KEYWORDS: list[str] = [
    "inteligencia artificial",
    "inteligência artificial",
    "ia",
    "machine learning",
    "aprendizado de maquina",
    "aprendizado de máquina",
    "aprendizagem de máquina",
    "deep learning",
    "aprendizado profundo",
    "deep learning",
    "neural network",
    "rede neural",
    "redes neurais",
    "nlp",
    "natural language",
    "processamento de linguagem natural",
    "pln",
    "computer vision",
    "visao computacional",
    "visão computacional",
    "modelo de linguagem",
    "language model",
    "llm",
    "gpt",
    "transformer",
    "bert",
    "diffusion",
    "generative ai",
    "ia generativa",
    "genai",
    "rag",
    "retrieval augmented",
    "fine-tuning",
    "fine tuning",
    "transfer learning",
    "treinamento",
    "inferencia",
    "inferência",
    "inference",
    "embedding",
    "vector database",
    "banco vetorial",
    "similaridade semantica",
    "similaridade semântica",
    "semantic similarity",
    "agente de ia",
    "ai agent",
    "autonomo",
    "autonomous ai",
    "modelo proprietario",
    "modelo próprio",
]

_TECHNICAL_AI_TERMS: list[str] = [
    "pytorch",
    "tensorflow",
    "jax",
    "keras",
    "scikit-learn",
    "sklearn",
    "hugging face",
    "transformers",
    "xgboost",
    "xgb",
    "lightgbm",
    "catboost",
    "onnx",
    "tensorrt",
    "cuda",
    "cudnn",
    "triton",
    "mlflow",
    "kubeflow",
    "ray",
    "dask",
    "weaviate",
    "pinecone",
    "qdrant",
    "chroma",
    "milvus",
    "langchain",
    "llamaindex",
    "haystack",
    "spacy",
    "nltk",
    "opencv",
    "yolo",
    "detectron",
    "stable diffusion",
    "whisper",
    "t5",
    "llama",
    "mistral",
    "falcon",
    "gemma",
    "sentence-transformers",
    "tokenizer",
]

_PRODUCT_AI_CLAIM_KEYWORDS: list[str] = [
    "produto baseado em ia",
    "ai-powered",
    "ai-native",
    "ia nativa",
    "plataforma de ia",
    "ai platform",
    "solucao de ia",
    "solução de ia",
    "ai solution",
    "saas com ia",
    "ai saas",
    "automacao inteligente",
    "automação inteligente",
    "intelligent automation",
    "analise preditiva",
    "análise preditiva",
    "predictive analytics",
    "recomendacao inteligente",
    "recomendação inteligente",
    "assistente virtual",
    "chatbot inteligente",
    "analise inteligente",
    "our ai",
    "nossa ia",
]

_MODEL_ML_INFRA_KEYWORDS: list[str] = [
    "gpu",
    "tpu",
    "a100",
    "h100",
    "v100",
    "t4",
    "l4",
    "cluster",
    "treinamento distribuido",
    "treinamento distribuído",
    "distributed training",
    "mlops",
    "ci/cd for ml",
    "model registry",
    "feature store",
    "data pipeline",
    "etl",
    "data lake",
    "data warehouse",
    "model serving",
    "inference server",
    "model deployment",
    "kubernetes",
    "k8s",
    "docker",
    "container",
    "escalabilidade",
    "scalability",
]

# ── Keyword lists for nvidia_fit features ────────────────────────────────────

_NVIDIA_GPU_KEYWORDS: list[str] = [
    "gpu",
    "a100",
    "h100",
    "v100",
    "t4",
    "l4",
    "rtx",
    "quadro",
    "tesla",
    "nvidia gpu",
    "placa de video",
    "placa de vídeo",
    "aceleracao grafica",
    "aceleração gráfica",
]

_NVIDIA_CUDA_KEYWORDS: list[str] = [
    "cuda",
    "cudnn",
    "tensorrt",
    "nvidia",
    "triton inference server",
    "rapids",
    "cudf",
    "cuml",
    "cugraph",
    "nvidia nim",
    "nvidia ai enterprise",
    "nemo",
    "nemo guardrails",
    "nvidia riva",
    "nvidia morpheus",
    "nvidia isaac",
    "nvidia omniverse",
]

_NVIDIA_INFERENCE_KEYWORDS: list[str] = [
    "inferencia",
    "inferência",
    "inference",
    "treinamento",
    "training",
    "batch inference",
    "tempo real",
    "real-time",
    "baixa latencia",
    "baixa latência",
    "low latency",
    "alta taxa",
    "high throughput",
    "model serving",
    "triton",
]

_NVIDIA_CV_KEYWORDS: list[str] = [
    "computer vision",
    "visao computacional",
    "visão computacional",
    "image recognition",
    "reconhecimento de imagem",
    "object detection",
    "deteccao de objetos",
    "detecção de objetos",
    "video analytics",
    "analise de video",
    "análise de vídeo",
    "face recognition",
    "reconhecimento facial",
    "ocr",
    "optical character",
    "yolo",
    "detectron",
    "opencv",
    "classificacao de imagem",
    "classificação de imagem",
    "segmentacao",
    "segmentação",
]

_NVIDIA_GENAI_LLM_KEYWORDS: list[str] = [
    "llm",
    "large language model",
    "modelo de linguagem",
    "gpt",
    "generative ai",
    "ia generativa",
    "genai",
    "text generation",
    "geracao de texto",
    "geração de texto",
    "chatbot",
    "assistente virtual",
    "sumarizacao",
    "sumarização",
    "summarization",
    "traducao automatica",
    "tradução automática",
    "machine translation",
    "rag",
    "retrieval augmented",
    "fine-tuning",
    "instrucao",
    "instrução",
]

_NVIDIA_DATA_KEYWORDS: list[str] = [
    "data pipeline",
    "etl",
    "data lake",
    "data warehouse",
    "streaming",
    "kafka",
    "spark",
    "data processing",
    "processamento de dados",
    "analise de dados",
    "análise de dados",
    "data analytics",
    "big data",
    "banco de dados vetorial",
    "vector database",
    "data integration",
    "integracao de dados",
    "integração de dados",
]

_NVIDIA_KEYWORD_KEYWORDS: list[str] = [
    "nvidia",
    "nvidia gpu",
    "nvidia cuda",
    "tensorrt",
    "nvidia ai",
    "nvidia enterprise",
    "nvidia nim",
]

_NVIDIA_INDUSTRY_KEYWORDS: list[str] = [
    "autonomous vehicles",
    "carro autonomo",
    "carro autônomo",
    "healthcare ai",
    "ia em saude",
    "ia na saúde",
    "ia para saúde",
    "fintech ia",
    "ia fintech",
    "agtech",
    "agritech",
    "ia no agro",
    "ia agro",
    "robotics",
    "robotica",
    "robótica",
    "autonomous machines",
    "maquinas autonomas",
    "máquinas autônomas",
    "digital twin",
    "simulation",
    "simulacao",
    "simulação",
    "cybersecurity",
    "ciberseguranca",
    "cibersegurança",
    "ia para industrias",
    "industrial ai",
]

_EMPTY_BLOCKING_WEIGHTS: dict[str, float] = {}


class ScoreStatus(str, Enum):
    PASSED = "passed"
    NEEDS_REVIEW = "needs_review"
    FAILED = "failed"
    BLOCKED_UNCALIBRATED_SCORING = "blocked_uncalibrated_scoring"


class StartupScoringFeatures(BaseModel):
    ai_signal_count: int = Field(ge=0)
    ai_signal_source_coverage: float = Field(ge=0.0, le=1.0)
    technical_ai_term_count: int = Field(ge=0)
    product_ai_claim_count: int = Field(ge=0)
    accepted_ai_evidence_count: int = Field(ge=0)
    ai_claim_support_ratio: float = Field(ge=0.0, le=1.0)
    evidence_confidence_mean_for_ai_claims: float = Field(ge=0.0, le=1.0)
    source_quality_mean_for_ai_sources: float = Field(ge=0.0, le=1.0)
    technical_depth_signal_count: int = Field(ge=0)
    model_or_ml_infrastructure_signal_count: int = Field(ge=0)
    uncertainty_penalty: float = Field(ge=0.0, le=1.0)


class NvidiaFitFeatures(BaseModel):
    gpu_compute_signal_count: int = Field(ge=0)
    cuda_or_acceleration_signal_count: int = Field(ge=0)
    inference_or_training_signal_count: int = Field(ge=0)
    computer_vision_signal_count: int = Field(ge=0)
    genai_llm_signal_count: int = Field(ge=0)
    data_pipeline_signal_count: int = Field(ge=0)
    nvidia_keyword_signal_count: int = Field(ge=0)
    nvidia_relevant_industry_signal_count: int = Field(ge=0)
    accepted_nvidia_fit_evidence_count: int = Field(ge=0)
    rag_context_alignment_count: int = Field(ge=0)
    evidence_confidence_mean_for_nvidia_claims: float = Field(ge=0.0, le=1.0)
    implementation_complexity_proxy: float = Field(ge=0.0, le=1.0)
    uncertainty_penalty: float = Field(ge=0.0, le=1.0)


class ScoreComponent(BaseModel):
    score_name: str
    score_value: float = Field(ge=0.0, le=1.0)
    score_status: ScoreStatus
    features: dict[str, Any]
    weights: dict[str, float]
    thresholds: dict[str, float]
    calibration_decision_ids: list[str]
    calibration_status: str
    production_allowed: bool
    uncertainty: float = Field(ge=0.0, le=1.0)
    blockers: list[str]
    explanation: str


class StartupScoreResult(BaseModel):
    ai_native: ScoreComponent
    nvidia_fit: ScoreComponent


class StartupScoringSummary(BaseModel):
    scoring_status: str
    score_metrics: dict[str, Any]
    ai_native_score: float = Field(ge=0.0, le=1.0)
    nvidia_fit_score: float = Field(ge=0.0, le=1.0)
    calibration_status: str
    production_allowed: bool
    blockers: list[str]


# ── Feature extraction helpers ────────────────────────────────────────────────


def _text_contains_any(text: str, keywords: list[str]) -> bool:
    lower = text.lower()
    for kw in keywords:
        if kw in lower:
            return True
    return False


def _count_keyword_matches(texts: list[str], keywords: list[str]) -> int:
    count = 0
    for t in texts:
        lower = t.lower()
        for kw in keywords:
            if kw in lower:
                count += 1
                break
    return count


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _extract_texts_from_items(items: list[dict[str, Any]]) -> list[str]:
    texts: list[str] = []
    for item in items:
        text = item.get("text") or item.get("snippet") or ""
        if text:
            texts.append(str(text))
    return texts


def _extract_claim_texts(claims: list[dict[str, Any]]) -> list[str]:
    return [str(c.get("claim_text", "")) for c in claims if isinstance(c, dict)]


# ── ai_native feature extraction ──────────────────────────────────────────────


def extract_ai_native_features(
    claims: list[dict[str, Any]],
    accepted_evidence_items: list[dict[str, Any]],
    evidence_items: list[dict[str, Any]],
) -> StartupScoringFeatures:
    claim_texts = _extract_claim_texts(claims)
    ev_texts = _extract_texts_from_items(evidence_items)
    ac_ev_texts = _extract_texts_from_items(accepted_evidence_items)
    all_texts = claim_texts + ev_texts

    ai_signal_count = _count_keyword_matches(all_texts, _AI_SIGNAL_KEYWORDS)

    source_ids_with_signal: set[str] = set()
    all_source_ids: set[str] = set()
    for item in evidence_items:
        sid = item.get("source_id") or item.get("url", "")
        if sid:
            all_source_ids.add(sid)
            text = str(item.get("text", "") or item.get("snippet", ""))
            if _text_contains_any(text, _AI_SIGNAL_KEYWORDS):
                source_ids_with_signal.add(sid)
    ai_signal_source_coverage = len(source_ids_with_signal) / len(all_source_ids) if all_source_ids else 0.0

    technical_ai_term_count = _count_keyword_matches(all_texts, _TECHNICAL_AI_TERMS)

    product_ai_claim_count = _count_keyword_matches(claim_texts, _PRODUCT_AI_CLAIM_KEYWORDS)

    accepted_ai_evidence_count = _count_keyword_matches(ac_ev_texts, _AI_SIGNAL_KEYWORDS)

    ai_claims_supported = 0
    ai_claims_total = 0
    ai_confidences: list[float] = []
    ai_source_qualities: list[float] = []
    for c in claims:
        if not isinstance(c, dict):
            continue
        ct = str(c.get("claim_text", ""))
        if _text_contains_any(ct, _AI_SIGNAL_KEYWORDS):
            ai_claims_total += 1
            if c.get("support_status") == "supported":
                ai_claims_supported += 1
    ai_claim_support_ratio = ai_claims_supported / ai_claims_total if ai_claims_total > 0 else 0.0

    for item in evidence_items:
        text = str(item.get("text", "") or item.get("snippet", ""))
        if _text_contains_any(text, _AI_SIGNAL_KEYWORDS):
            ec = item.get("evidence_confidence_score")
            if isinstance(ec, (int, float)):
                ai_confidences.append(float(ec))
            sq = item.get("source_quality_score")
            if isinstance(sq, (int, float)):
                ai_source_qualities.append(float(sq))

    evidence_confidence_mean_for_ai_claims = _mean(ai_confidences)
    source_quality_mean_for_ai_sources = _mean(ai_source_qualities)

    technical_depth_signal_count = _count_keyword_matches(all_texts, _MODEL_ML_INFRA_KEYWORDS)

    model_or_ml_infrastructure_signal_count = _count_keyword_matches(all_texts, _MODEL_ML_INFRA_KEYWORDS)

    uncertainty_penalty = _compute_uncertainty(
        evidence_count=ai_claims_total,
        avg_source_quality=source_quality_mean_for_ai_sources,
        avg_evidence_confidence=evidence_confidence_mean_for_ai_claims,
    )

    return StartupScoringFeatures(
        ai_signal_count=ai_signal_count,
        ai_signal_source_coverage=round(ai_signal_source_coverage, 4),
        technical_ai_term_count=technical_ai_term_count,
        product_ai_claim_count=product_ai_claim_count,
        accepted_ai_evidence_count=accepted_ai_evidence_count,
        ai_claim_support_ratio=round(ai_claim_support_ratio, 4),
        evidence_confidence_mean_for_ai_claims=round(evidence_confidence_mean_for_ai_claims, 4),
        source_quality_mean_for_ai_sources=round(source_quality_mean_for_ai_sources, 4),
        technical_depth_signal_count=technical_depth_signal_count,
        model_or_ml_infrastructure_signal_count=model_or_ml_infrastructure_signal_count,
        uncertainty_penalty=round(uncertainty_penalty, 4),
    )


# ── nvidia_fit feature extraction ─────────────────────────────────────────────


def extract_nvidia_fit_features(
    claims: list[dict[str, Any]],
    accepted_evidence_items: list[dict[str, Any]],
    evidence_items: list[dict[str, Any]],
    rag_contexts: list[str] | None = None,
) -> NvidiaFitFeatures:
    claim_texts = _extract_claim_texts(claims)
    ev_texts = _extract_texts_from_items(evidence_items)
    ac_ev_texts = _extract_texts_from_items(accepted_evidence_items)
    all_texts = claim_texts + ev_texts

    gpu_compute_signal_count = _count_keyword_matches(all_texts, _NVIDIA_GPU_KEYWORDS)

    cuda_or_acceleration_signal_count = _count_keyword_matches(all_texts, _NVIDIA_CUDA_KEYWORDS)

    inference_or_training_signal_count = _count_keyword_matches(all_texts, _NVIDIA_INFERENCE_KEYWORDS)

    computer_vision_signal_count = _count_keyword_matches(all_texts, _NVIDIA_CV_KEYWORDS)

    genai_llm_signal_count = _count_keyword_matches(all_texts, _NVIDIA_GENAI_LLM_KEYWORDS)

    data_pipeline_signal_count = _count_keyword_matches(all_texts, _NVIDIA_DATA_KEYWORDS)

    nvidia_keyword_signal_count = _count_keyword_matches(all_texts, _NVIDIA_KEYWORD_KEYWORDS)

    nvidia_relevant_industry_signal_count = _count_keyword_matches(all_texts, _NVIDIA_INDUSTRY_KEYWORDS)

    accepted_nvidia_fit_evidence_count = _count_keyword_matches(ac_ev_texts, _NVIDIA_CUDA_KEYWORDS)

    rag_context_alignment_count = 0
    if rag_contexts:
        for ctx in rag_contexts:
            if isinstance(ctx, str) and _text_contains_any(ctx, _NVIDIA_CUDA_KEYWORDS):
                rag_context_alignment_count += 1

    nvidia_confidences: list[float] = []
    for item in evidence_items:
        text = str(item.get("text", "") or item.get("snippet", ""))
        if _text_contains_any(text, _NVIDIA_CUDA_KEYWORDS):
            ec = item.get("evidence_confidence_score")
            if isinstance(ec, (int, float)):
                nvidia_confidences.append(float(ec))

    evidence_confidence_mean_for_nvidia_claims = _mean(nvidia_confidences)

    implementation_complexity_proxy = _compute_implementation_complexity_proxy(
        nvidia_keyword_signal_count,
        cuda_or_acceleration_signal_count,
    )

    uncertainty_penalty = _compute_uncertainty(
        evidence_count=len(nvidia_confidences),
        avg_source_quality=0.5,
        avg_evidence_confidence=evidence_confidence_mean_for_nvidia_claims,
    )

    return NvidiaFitFeatures(
        gpu_compute_signal_count=gpu_compute_signal_count,
        cuda_or_acceleration_signal_count=cuda_or_acceleration_signal_count,
        inference_or_training_signal_count=inference_or_training_signal_count,
        computer_vision_signal_count=computer_vision_signal_count,
        genai_llm_signal_count=genai_llm_signal_count,
        data_pipeline_signal_count=data_pipeline_signal_count,
        nvidia_keyword_signal_count=nvidia_keyword_signal_count,
        nvidia_relevant_industry_signal_count=nvidia_relevant_industry_signal_count,
        accepted_nvidia_fit_evidence_count=accepted_nvidia_fit_evidence_count,
        rag_context_alignment_count=rag_context_alignment_count,
        evidence_confidence_mean_for_nvidia_claims=round(evidence_confidence_mean_for_nvidia_claims, 4),
        implementation_complexity_proxy=round(implementation_complexity_proxy, 4),
        uncertainty_penalty=round(uncertainty_penalty, 4),
    )


# ── Uncertainty computation ────────────────────────────────────────────────────


def _compute_uncertainty(
    evidence_count: int,
    avg_source_quality: float,
    avg_evidence_confidence: float,
    min_evidence_expected: int = 5,
) -> float:
    if evidence_count == 0:
        return 1.0
    coverage_factor = 1.0 - min(1.0, evidence_count / min_evidence_expected)
    quality_factor = 1.0 - avg_source_quality
    confidence_factor = 1.0 - avg_evidence_confidence
    raw = coverage_factor * 0.5 + quality_factor * 0.25 + confidence_factor * 0.25
    return min(1.0, raw)


def _compute_implementation_complexity_proxy(
    nvidia_keyword_count: int,
    cuda_count: int,
) -> float:
    has_cuda = 1.0 if cuda_count > 0 else 0.0
    has_nvidia = 1.0 if nvidia_keyword_count > 0 else 0.0
    raw = 0.3 + has_cuda * 0.4 + has_nvidia * 0.3
    return min(1.0, raw)


# ── Weighted score computation ────────────────────────────────────────────────


def _compute_weighted_score(
    features: dict[str, float],
    weights: dict[str, float],
) -> float:
    weight_sum = sum(weights.values())
    if weight_sum == 0.0:
        return 0.0
    raw = sum(weights.get(k, 0.0) * v for k, v in features.items() if k in weights)
    raw /= weight_sum
    return max(0.0, min(1.0, raw))


def _features_to_float_dict(
    features: StartupScoringFeatures | NvidiaFitFeatures,
) -> dict[str, float]:
    return features.model_dump(mode="json")  # type: ignore[return-value]


# ── Calibration lookup ────────────────────────────────────────────────────────


def _lookup_calibration_group(
    decision_ids: list[str],
    inventory: list[DecisionCalibrationRecord] | None = None,
) -> tuple[dict[str, Any] | None, bool, list[str]]:
    if inventory is None:
        inventory = get_project_decision_inventory()

    values: dict[str, Any] = {}
    blockers: list[str] = []

    for decision_id in decision_ids:
        found = False
        for rec in inventory:
            if rec.decision_id == decision_id:
                found = True
                validation = validate_decision_for_production(rec)
                if not validation.passed:
                    blockers.append(f"Decision '{decision_id}' blocked for production: {'; '.join(validation.reasons)}")
                elif rec.calibration_status.value in ("uncalibrated", "blocked"):
                    blockers.append(f"Decision '{decision_id}' is {rec.calibration_status.value}")
                else:
                    values[decision_id] = rec.current_value
                break
        if not found:
            blockers.append(f"Decision '{decision_id}' not found in registry")

    if blockers:
        return None, False, blockers

    return values, True, []


def _lookup_weight_dict(
    decision_id: str,
    values: dict[str, Any],
) -> dict[str, float] | None:
    v = values.get(decision_id)
    if isinstance(v, dict):
        result: dict[str, float] = {}
        for k, val in v.items():
            if isinstance(val, (int, float)):
                result[k] = float(val)
        return result
    return None


def _weight_blocker(decision_id: str, weights: dict[str, float] | None) -> str | None:
    if weights is None:
        return f"Decision '{decision_id}' current_value is not a dict"
    if not weights:
        return f"Decision '{decision_id}' current_value is empty"
    if any(value < 0 for value in weights.values()):
        return f"Decision '{decision_id}' has negative weights"
    total = sum(weights.values())
    if total <= 0.0:
        return f"Decision '{decision_id}' weight sum is zero"
    if abs(total - 1.0) > 0.001:
        return f"Decision '{decision_id}' weights must sum to 1.0; observed {round(total, 6)}"
    return None


def _lookup_float(
    decision_id: str,
    values: dict[str, Any],
    default: float | None = None,
) -> float | None:
    v = values.get(decision_id)
    if isinstance(v, (int, float)):
        return float(v)
    return default


# ── Main scoring function ─────────────────────────────────────────────────────


def compute_startup_scoring(
    claims: list[dict[str, Any]],
    accepted_evidence_items: list[dict[str, Any]],
    evidence_items: list[dict[str, Any]],
    unsupported_critical_claims_count: int = 0,
    rag_contexts: list[str] | None = None,
    inventory: list[DecisionCalibrationRecord] | None = None,
) -> StartupScoreResult:
    if inventory is None:
        inventory = get_project_decision_inventory()

    ai_features = extract_ai_native_features(claims, accepted_evidence_items, evidence_items)
    nv_features = extract_nvidia_fit_features(
        claims, accepted_evidence_items, evidence_items, rag_contexts=rag_contexts
    )

    ai_cal_values, ai_cal_ok, ai_blockers = _lookup_calibration_group(REQUIRED_DECISIONS_AI_NATIVE, inventory=inventory)
    nv_cal_values, nv_cal_ok, nv_blockers = _lookup_calibration_group(
        REQUIRED_DECISIONS_NVIDIA_FIT, inventory=inventory
    )

    ai_is_blocked = not ai_cal_ok
    nv_is_blocked = not nv_cal_ok

    ai_component = _build_ai_native_component(ai_features, ai_cal_values, ai_is_blocked, ai_blockers)
    nv_component = _build_nvidia_fit_component(nv_features, nv_cal_values, nv_is_blocked, nv_blockers)

    return StartupScoreResult(ai_native=ai_component, nvidia_fit=nv_component)


def _build_ai_native_component(
    features: StartupScoringFeatures,
    cal_values: dict[str, Any] | None,
    is_blocked: bool,
    blockers: list[str],
) -> ScoreComponent:
    feature_dict = _features_to_float_dict(features)

    if is_blocked:
        return ScoreComponent(
            score_name="ai_native_score",
            score_value=0.0,
            score_status=ScoreStatus.BLOCKED_UNCALIBRATED_SCORING,
            features=feature_dict,
            weights=_EMPTY_BLOCKING_WEIGHTS,
            thresholds={},
            calibration_decision_ids=REQUIRED_DECISIONS_AI_NATIVE,
            calibration_status="uncalibrated",
            production_allowed=False,
            uncertainty=1.0,
            blockers=blockers,
            explanation="ai_native_score blocked: required calibration decisions missing or uncalibrated.",
        )

    assert cal_values is not None
    weights = _lookup_weight_dict(AI_NATIVE_WEIGHTS_DECISION_ID, cal_values)
    threshold = _lookup_float(AI_NATIVE_THRESHOLD_DECISION_ID, cal_values)
    uncertainty_penalty_mult = _lookup_float(AI_NATIVE_UNCERTAINTY_DECISION_ID, cal_values)

    weight_blocker = _weight_blocker(AI_NATIVE_WEIGHTS_DECISION_ID, weights)
    required_float_blockers = []
    if threshold is None:
        required_float_blockers.append(f"Decision '{AI_NATIVE_THRESHOLD_DECISION_ID}' current_value is not numeric")
    if uncertainty_penalty_mult is None:
        required_float_blockers.append(f"Decision '{AI_NATIVE_UNCERTAINTY_DECISION_ID}' current_value is not numeric")

    if weight_blocker or required_float_blockers:
        return ScoreComponent(
            score_name="ai_native_score",
            score_value=0.0,
            score_status=ScoreStatus.BLOCKED_UNCALIBRATED_SCORING,
            features=feature_dict,
            weights=_EMPTY_BLOCKING_WEIGHTS,
            thresholds={},
            calibration_decision_ids=REQUIRED_DECISIONS_AI_NATIVE,
            calibration_status="uncalibrated",
            production_allowed=False,
            uncertainty=1.0,
            blockers=blockers + [b for b in [weight_blocker] if b] + required_float_blockers,
            explanation="ai_native_score blocked: calibration values are invalid.",
        )

    assert weights is not None
    assert threshold is not None
    assert uncertainty_penalty_mult is not None
    raw_score = _compute_weighted_score(feature_dict, weights)

    uncertainty_penalty_value = features.uncertainty_penalty * uncertainty_penalty_mult
    final_score = max(0.0, min(1.0, raw_score - uncertainty_penalty_value))

    calibration_status = "calibrated"
    production_allowed = True
    thresholds: dict[str, float] = {}
    thresholds["production_threshold"] = threshold

    score_status: ScoreStatus
    if final_score < threshold:
        score_status = ScoreStatus.FAILED
    else:
        score_status = ScoreStatus.PASSED

    return ScoreComponent(
        score_name="ai_native_score",
        score_value=round(final_score, 4),
        score_status=score_status,
        features=feature_dict,
        weights=dict(weights),
        thresholds=thresholds,
        calibration_decision_ids=REQUIRED_DECISIONS_AI_NATIVE,
        calibration_status=calibration_status,
        production_allowed=production_allowed,
        uncertainty=round(uncertainty_penalty_value, 4),
        blockers=[],
        explanation=(
            f"ai_native_score={round(final_score, 4)} computed from "
            f"{len(weights)} weighted features with uncertainty penalty "
            f"{round(uncertainty_penalty_value, 4)}."
        ),
    )


def _build_nvidia_fit_component(
    features: NvidiaFitFeatures,
    cal_values: dict[str, Any] | None,
    is_blocked: bool,
    blockers: list[str],
) -> ScoreComponent:
    feature_dict = _features_to_float_dict(features)

    if is_blocked:
        return ScoreComponent(
            score_name="nvidia_fit_score",
            score_value=0.0,
            score_status=ScoreStatus.BLOCKED_UNCALIBRATED_SCORING,
            features=feature_dict,
            weights=_EMPTY_BLOCKING_WEIGHTS,
            thresholds={},
            calibration_decision_ids=REQUIRED_DECISIONS_NVIDIA_FIT,
            calibration_status="uncalibrated",
            production_allowed=False,
            uncertainty=1.0,
            blockers=blockers,
            explanation="nvidia_fit_score blocked: required calibration decisions missing or uncalibrated.",
        )

    assert cal_values is not None
    weights = _lookup_weight_dict(NVIDIA_FIT_WEIGHTS_DECISION_ID, cal_values)
    threshold = _lookup_float(NVIDIA_FIT_THRESHOLD_DECISION_ID, cal_values)
    uncertainty_penalty_mult = _lookup_float(NVIDIA_FIT_UNCERTAINTY_DECISION_ID, cal_values)

    weight_blocker = _weight_blocker(NVIDIA_FIT_WEIGHTS_DECISION_ID, weights)
    required_float_blockers = []
    if threshold is None:
        required_float_blockers.append(f"Decision '{NVIDIA_FIT_THRESHOLD_DECISION_ID}' current_value is not numeric")
    if uncertainty_penalty_mult is None:
        required_float_blockers.append(f"Decision '{NVIDIA_FIT_UNCERTAINTY_DECISION_ID}' current_value is not numeric")

    if weight_blocker or required_float_blockers:
        return ScoreComponent(
            score_name="nvidia_fit_score",
            score_value=0.0,
            score_status=ScoreStatus.BLOCKED_UNCALIBRATED_SCORING,
            features=feature_dict,
            weights=_EMPTY_BLOCKING_WEIGHTS,
            thresholds={},
            calibration_decision_ids=REQUIRED_DECISIONS_NVIDIA_FIT,
            calibration_status="uncalibrated",
            production_allowed=False,
            uncertainty=1.0,
            blockers=blockers + [b for b in [weight_blocker] if b] + required_float_blockers,
            explanation="nvidia_fit_score blocked: calibration values are invalid.",
        )

    assert weights is not None
    assert threshold is not None
    assert uncertainty_penalty_mult is not None
    raw_score = _compute_weighted_score(feature_dict, weights)

    uncertainty_penalty_value = features.uncertainty_penalty * uncertainty_penalty_mult
    final_score = max(0.0, min(1.0, raw_score - uncertainty_penalty_value))

    calibration_status = "calibrated"
    production_allowed = True
    thresholds: dict[str, float] = {}
    thresholds["production_threshold"] = threshold

    score_status: ScoreStatus
    if final_score < threshold:
        score_status = ScoreStatus.FAILED
    else:
        score_status = ScoreStatus.PASSED

    return ScoreComponent(
        score_name="nvidia_fit_score",
        score_value=round(final_score, 4),
        score_status=score_status,
        features=feature_dict,
        weights=dict(weights),
        thresholds=thresholds,
        calibration_decision_ids=REQUIRED_DECISIONS_NVIDIA_FIT,
        calibration_status=calibration_status,
        production_allowed=production_allowed,
        uncertainty=round(uncertainty_penalty_value, 4),
        blockers=[],
        explanation=(
            f"nvidia_fit_score={round(final_score, 4)} computed from "
            f"{len(weights)} weighted features with uncertainty penalty "
            f"{round(uncertainty_penalty_value, 4)}."
        ),
    )


def build_scoring_summary(
    result: StartupScoreResult,
    unsupported_critical_claims_count: int = 0,
    accepted_evidence_count: int = 0,
    rejected_evidence_count: int = 0,
    accepted_claim_count: int = 0,
    average_evidence_confidence: float = 0.0,
    average_source_quality: float = 0.0,
) -> StartupScoringSummary:
    ai = result.ai_native
    nv = result.nvidia_fit

    is_blocked = (
        ai.score_status == ScoreStatus.BLOCKED_UNCALIBRATED_SCORING
        or nv.score_status == ScoreStatus.BLOCKED_UNCALIBRATED_SCORING
    )
    is_failed = unsupported_critical_claims_count > 0

    all_blockers: list[str] = list(ai.blockers) + list(nv.blockers)

    if is_failed:
        scoring_status = "failed"
        msg = f"unsupported_critical_claims_count={unsupported_critical_claims_count} > 0"
        if msg not in all_blockers:
            all_blockers.append(msg)
        production_allowed = False
    elif is_blocked:
        scoring_status = "blocked_uncalibrated_scoring"
        production_allowed = False
    elif ai.score_status == ScoreStatus.FAILED or nv.score_status == ScoreStatus.FAILED:
        scoring_status = "failed"
        production_allowed = False
    else:
        scoring_status = "passed"
        production_allowed = ai.production_allowed and nv.production_allowed

    calibrated_decision_count = 0
    missing_calibration_count = 0
    if ai.calibration_status == "calibrated":
        calibrated_decision_count += len(REQUIRED_DECISIONS_AI_NATIVE)
    else:
        missing_calibration_count += len(REQUIRED_DECISIONS_AI_NATIVE)
    if nv.calibration_status == "calibrated":
        calibrated_decision_count += len(REQUIRED_DECISIONS_NVIDIA_FIT)
    else:
        missing_calibration_count += len(REQUIRED_DECISIONS_NVIDIA_FIT)

    ai_feature_count = sum(1 for v in ai.features.values() if isinstance(v, (int, float)) and v > 0)
    ai_feature_total = max(1, len(ai.features))
    nv_feature_count = sum(1 for v in nv.features.values() if isinstance(v, (int, float)) and v > 0)
    nv_feature_total = max(1, len(nv.features))

    score_metrics: dict[str, Any] = {
        "ai_native_feature_coverage": round(ai_feature_count / ai_feature_total, 4),
        "nvidia_fit_feature_coverage": round(nv_feature_count / nv_feature_total, 4),
        "accepted_evidence_count": accepted_evidence_count,
        "rejected_evidence_count": rejected_evidence_count,
        "accepted_claim_count": accepted_claim_count,
        "unsupported_critical_claims_count": unsupported_critical_claims_count,
        "average_evidence_confidence": round(average_evidence_confidence, 4),
        "average_source_quality": round(average_source_quality, 4),
        "scoring_uncertainty": round(max(ai.uncertainty, nv.uncertainty), 4),
        "calibrated_decision_count": calibrated_decision_count,
        "missing_calibration_count": missing_calibration_count,
    }

    return StartupScoringSummary(
        scoring_status=scoring_status,
        score_metrics=score_metrics,
        ai_native_score=ai.score_value,
        nvidia_fit_score=nv.score_value,
        calibration_status=("calibrated" if calibrated_decision_count > 0 else "uncalibrated"),
        production_allowed=production_allowed,
        blockers=all_blockers,
    )


__all__ = [
    "AI_NATIVE_WEIGHTS_DECISION_ID",
    "AI_NATIVE_THRESHOLD_DECISION_ID",
    "AI_NATIVE_UNCERTAINTY_DECISION_ID",
    "NVIDIA_FIT_WEIGHTS_DECISION_ID",
    "NVIDIA_FIT_THRESHOLD_DECISION_ID",
    "NVIDIA_FIT_UNCERTAINTY_DECISION_ID",
    "REQUIRED_CALIBRATION_DECISIONS",
    "ScoreStatus",
    "StartupScoringFeatures",
    "NvidiaFitFeatures",
    "ScoreComponent",
    "StartupScoreResult",
    "StartupScoringSummary",
    "compute_startup_scoring",
    "extract_ai_native_features",
    "extract_nvidia_fit_features",
    "build_scoring_summary",
]
