# ruff: noqa: E501

from __future__ import annotations

from src.classification.ai_native_classifier import ClassificationResult
from src.diagnosis.schemas import EvidenceTag, GapDiagnosisResult, GapWithEvidence
from src.extraction.schemas import (
    ConfidenceLevel,
    ImplementationComplexity,
    RecommendationPriority,
    StartupProfile,
    TechnicalGap,
)
from src.recommendation.schemas import (
    PerGapRecommendation,
    RecommendationResult,
    RecommendedNextAction,
    SuggestedTechnicalExperiment,
)
from src.scoring.composite_ranking import CompositeResult
from src.scoring.defensibility_score import DefensibilityScoreResult
from src.scoring.inception_fit_score import InceptionFitScoreResult
from src.scoring.production_readiness import ProductionReadinessResult
from src.validation.evidence_validator import ValidatedEvidence

_COMPLEXITY_MAP: dict[str, ImplementationComplexity] = {
    "NVIDIA NIM": ImplementationComplexity.LOW,
    "cuDF": ImplementationComplexity.LOW,
    "cuML": ImplementationComplexity.LOW,
    "TensorRT-LLM": ImplementationComplexity.MEDIUM,
    "Triton Inference Server": ImplementationComplexity.MEDIUM,
    "NVIDIA RAPIDS": ImplementationComplexity.MEDIUM,
    "NVIDIA Riva": ImplementationComplexity.MEDIUM,
    "NVIDIA NeMo": ImplementationComplexity.MEDIUM,
    "NeMo Guardrails": ImplementationComplexity.MEDIUM,
    "NVIDIA TensorRT": ImplementationComplexity.MEDIUM,
    "MONAI": ImplementationComplexity.MEDIUM,
    "NVIDIA Omniverse": ImplementationComplexity.HIGH,
    "NVIDIA Isaac": ImplementationComplexity.HIGH,
    "NVIDIA Clara": ImplementationComplexity.HIGH,
    "NVIDIA Morpheus": ImplementationComplexity.HIGH,
    "NVIDIA AI Enterprise": ImplementationComplexity.HIGH,
}

_EXPERIMENT_TEMPLATES: dict[TechnicalGap, dict[str, str]] = {
    TechnicalGap.HIGH_INFERENCE_COST: {
        "title": "Benchmark inference cost with TensorRT-LLM",
        "hypothesis": "TensorRT-LLM reduz custo por 1k requests em pelo menos 40% vs solucao atual",
        "metric": "custo por 1k requests (USD)",
        "duration": "2-4 semanas",
        "step": "Agendar acesso ao NVIDIA LaunchPad para TensorRT-LLM",
    },
    TechnicalGap.HIGH_LATENCY: {
        "title": "Benchmark latency p50/p95 with Triton Inference Server",
        "hypothesis": "Triton Inference Server reduz latencia p50 em 50% e p95 em 60% vs solucao atual",
        "metric": "latencia p50 e p95 (ms)",
        "duration": "2-4 semanas",
        "step": "Configurar Triton Inference Server com modelo atual da startup",
    },
    TechnicalGap.EXTERNAL_API_DEPENDENCY: {
        "title": "Benchmark NIM self-hosted inference cost vs external API",
        "hypothesis": "NIM auto-hospedado reduz custo de inferencia em 60% vs API externa (ex.: OpenAI)",
        "metric": "custo por 1k requests, latencia p50",
        "duration": "3-5 semanas",
        "step": "Solicitar acesso ao NVIDIA NIM para o modelo de maior uso da startup",
    },
    TechnicalGap.AGENT_GOVERNANCE_GAP: {
        "title": "Evaluate NeMo Guardrails for agent safety",
        "hypothesis": "NeMo Guardrails detecta e bloqueia pelo menos 90% dos comportamentos nao autorizados em agentes LLM",
        "metric": "taxa de deteccao de violacoes, false positive rate",
        "duration": "4-6 semanas",
        "step": "Workshop de integracao NeMo Guardrails com arquiteto NVIDIA",
    },
    TechnicalGap.SLOW_DATA_PIPELINE: {
        "title": "Benchmark ETL throughput with RAPIDS cuDF",
        "hypothesis": "cuDF acelera pipeline ETL em pelo menos 5x vs CPU para datasets > 10GB",
        "metric": "throughput (GB/s), tempo total de ETL",
        "duration": "2-4 semanas",
        "step": "Portar pipeline ETL atual para cuDF com suporte NVIDIA",
    },
    TechnicalGap.HEAVY_TABULAR_PROCESSING: {
        "title": "Benchmark ML training speed with cuML",
        "hypothesis": "cuML reduz tempo de treinamento em pelo menos 3x vs sklearn para datasets tabulares",
        "metric": "tempo de treinamento (segundos), accuracy comparada",
        "duration": "2-4 semanas",
        "step": "Executar benchmark cuML vs sklearn com dataset representativo da startup",
    },
    TechnicalGap.PRIVACY_OR_CONTROLLED_DEPLOYMENT_GAP: {
        "title": "Validate on-prem deployment with NVIDIA AI Enterprise",
        "hypothesis": "NVIDIA AI Enterprise suporta deploy on-prem com soberania de dados e compliance regulatorio",
        "metric": "tempo de setup, conformidade com requisitos de privacidade",
        "duration": "4-8 semanas",
        "step": "Reuniao com arquiteto NVIDIA para definir requisitos de deploy controlado",
    },
    TechnicalGap.VOICE_NEED: {
        "title": "Benchmark Riva STT/TTS accuracy and latency",
        "hypothesis": "Riva oferece STT com WER < 5% e latencia < 200ms para audio em portugues brasileiro",
        "metric": "WER (Word Error Rate), latencia STT/TTS",
        "duration": "3-5 semanas",
        "step": "Avaliar Riva com amostras de audio da aplicacao da startup",
    },
    TechnicalGap.COMPUTER_VISION_NEED: {
        "title": "Benchmark CV inference throughput with TensorRT",
        "hypothesis": "TensorRT otimiza inferencia CV para throughput 3x maior vs framework original",
        "metric": "throughput (fps), latencia por frame",
        "duration": "2-4 semanas",
        "step": "Otimizar modelo CV da startup com TensorRT",
    },
    TechnicalGap.OBSERVABILITY_GAP: {
        "title": "Evaluate AI Enterprise monitoring for production ML",
        "hypothesis": "NVIDIA AI Enterprise fornece monitoramento de modelos com deteccao de drift em tempo real",
        "metric": "tempo de deteccao de drift, cobertura de metricas",
        "duration": "4-6 semanas",
        "step": "Workshop de observabilidade ML com NVIDIA AI Enterprise",
    },
    TechnicalGap.MODEL_EVALUATION_GAP: {
        "title": "Evaluate NeMo evaluation harness for LLM benchmarking",
        "hypothesis": "NeMo fornece harness de avaliacao comparavel a padroes da industria para LLMs",
        "metric": "accuracy, precision, recall em benchmark set",
        "duration": "3-5 semanas",
        "step": "Configurar NeMo evaluation harness com dataset de validacao da startup",
    },
    TechnicalGap.SIMULATION_NEED: {
        "title": "Prototype digital twin with Omniverse",
        "hypothesis": "Omniverse permite criar digital twin funcional em 4 semanas para simulacao fisica",
        "metric": "tempo de prototipagem, fidelidade da simulacao",
        "duration": "4-8 semanas",
        "step": "Workshop Omniverse com equipe de engenharia da startup",
    },
    TechnicalGap.ROBOTICS_NEED: {
        "title": "Evaluate Isaac Sim for robotics training pipeline",
        "hypothesis": "Isaac Sim reduz tempo de treinamento de modelos roboticos em 50% via simulacao",
        "metric": "tempo de treinamento, transfer learning success rate",
        "duration": "6-10 semanas",
        "step": "Avaliacao tecnica Isaac Sim com caso de uso robotico da startup",
    },
    TechnicalGap.HEALTHCARE_COMPLIANCE_NEED: {
        "title": "Validate Clara/MONAI compliance for healthcare deployment",
        "hypothesis": "Clara e MONAI fornecem ferramentas compliance-ready para IA em saude com suporte HIPAA",
        "metric": "cobertura de compliance, tempo de auditoria",
        "duration": "4-8 semanas",
        "step": "Consultoria de compliance NVIDIA Clara com time regulatorio da startup",
    },
    TechnicalGap.AI_CYBERSECURITY_NEED: {
        "title": "Benchmark Morpheus threat detection throughput",
        "hypothesis": "Morpheus processa deteccao de ameacas em tempo real com throughput 10x maior vs CPU",
        "metric": "throughput (eventos/segundo), latencia de deteccao",
        "duration": "4-6 semanas",
        "step": "Prova de conceito Morpheus com dados de rede da startup",
    },
}


def _determine_action(
    gap: GapWithEvidence,
    recommended_motion: str,
) -> RecommendedNextAction:
    if recommended_motion == "not_recommended":
        return RecommendedNextAction.NOT_RECOMMENDED

    if not gap.detected:
        return RecommendedNextAction.MONITOR

    if gap.confidence == ConfidenceLevel.LOW:
        return RecommendedNextAction.VALIDATE_MANUALLY

    if recommended_motion in ("lack_evidence_more_research",):
        return RecommendedNextAction.VALIDATE_MANUALLY

    if recommended_motion in ("monitor_and_nurture",) and gap.confidence in (
        ConfidenceLevel.LOW,
        ConfidenceLevel.MEDIUM,
    ):
        return RecommendedNextAction.MONITOR

    if gap.confidence == ConfidenceLevel.HIGH and recommended_motion in (
        "immediate_outreach",
        "high_priority_outreach",
    ):
        return RecommendedNextAction.APPROACH_NOW

    return RecommendedNextAction.VALIDATE_MANUALLY


def _determine_priority(
    action: RecommendedNextAction,
    gap_confidence: ConfidenceLevel,
) -> RecommendationPriority:
    if action == RecommendedNextAction.APPROACH_NOW:
        if gap_confidence == ConfidenceLevel.HIGH:
            return RecommendationPriority.HIGH
        return RecommendationPriority.MEDIUM

    if action == RecommendedNextAction.VALIDATE_MANUALLY:
        if gap_confidence == ConfidenceLevel.HIGH:
            return RecommendationPriority.MEDIUM
        return RecommendationPriority.LOW

    return RecommendationPriority.LOW


def _compute_overall_priority(
    recommendations: list[PerGapRecommendation],
) -> RecommendationPriority:
    priorities = {r.priority for r in recommendations if r.detected}
    if RecommendationPriority.HIGH in priorities:
        return RecommendationPriority.HIGH
    if RecommendationPriority.MEDIUM in priorities:
        return RecommendationPriority.MEDIUM
    return RecommendationPriority.LOW


def _compute_overall_confidence(
    recommendations: list[PerGapRecommendation],
) -> ConfidenceLevel:
    detected = [r for r in recommendations if r.detected]
    if not detected:
        return ConfidenceLevel.LOW

    confidences = [r.confidence for r in detected]
    if all(c == ConfidenceLevel.HIGH for c in confidences):
        return ConfidenceLevel.HIGH
    if any(c == ConfidenceLevel.HIGH for c in confidences):
        return ConfidenceLevel.MEDIUM
    return ConfidenceLevel.LOW


def _determine_complexity(tech_name: str) -> ImplementationComplexity:
    return _COMPLEXITY_MAP.get(tech_name, ImplementationComplexity.MEDIUM)


def _build_technical_justification(
    gap: GapWithEvidence,
    tech_names: list[str],
) -> str:
    if not tech_names:
        return ""
    tech_list = ", ".join(tech_names)
    tag = gap.evidence_tag.value
    return (
        f"Gap '{gap.gap.value}' was {tag} (confidence: {gap.confidence.value}). "
        f"Recommended technologies: {tech_list}. "
        f"{gap.reasoning}"
    )


def _build_business_justification(
    gap: GapWithEvidence,
    profile: StartupProfile,
    classification: ClassificationResult,
    recommended_motion: str,
) -> str:
    sector = profile.sector
    ai_level = classification.classification.value
    return (
        f"Startup {profile.startup_name} ({sector}, {ai_level}) presents "
        f"a {gap.confidence.value}-confidence {gap.evidence_tag.value} gap "
        f"in '{gap.gap.value}'. "
        f"NVIDIA recommended motion: {recommended_motion}. "
        f"Addressing this gap creates opportunity for NVIDIA technology adoption."
    )


def _suggest_experiment(
    gap: TechnicalGap,
    top_tech: str,
) -> SuggestedTechnicalExperiment | None:
    template = _EXPERIMENT_TEMPLATES.get(gap)
    if template is None:
        return None
    return SuggestedTechnicalExperiment(
        title=template["title"],
        target_gap=gap,
        hypothesis=template["hypothesis"],
        success_metric=template["metric"],
        estimated_duration=template["duration"],
        nvidia_technology=top_tech,
        next_step=template["step"],
    )


def build_per_gap_recommendation(
    gap: GapWithEvidence,
    tech_names: list[str],
    profile: StartupProfile,
    classification: ClassificationResult,
    recommended_motion: str,
) -> PerGapRecommendation:
    action = _determine_action(gap, recommended_motion)
    priority = _determine_priority(action, gap.confidence)

    max_complexity = ImplementationComplexity.LOW
    for t in tech_names:
        c = _determine_complexity(t)
        if c.value > max_complexity.value:
            max_complexity = c

    missing: list[str] = []
    if gap.evidence_tag == EvidenceTag.INFERRED:
        missing.append(
            f"Gap '{gap.gap.value}' detected by inference only — "
            "collect direct evidence to confirm."
        )

    experiment = None
    if action == RecommendedNextAction.APPROACH_NOW and tech_names:
        experiment = _suggest_experiment(gap.gap, tech_names[0])

    next_action = ""
    if action == RecommendedNextAction.APPROACH_NOW:
        if experiment:
            next_action = experiment.next_step
        else:
            next_action = f"Contact startup to discuss {', '.join(tech_names)} adoption"
    elif action == RecommendedNextAction.VALIDATE_MANUALLY:
        next_action = (
            f"Manually validate gap '{gap.gap.value}' — "
            f"current evidence is {gap.evidence_tag.value} with {gap.confidence.value} confidence"
        )
    elif action == RecommendedNextAction.MONITOR:
        next_action = f"Monitor startup for signals related to '{gap.gap.value}'"
    else:
        next_action = "No action recommended at this time"

    return PerGapRecommendation(
        diagnosed_gap=gap.gap,
        detected=gap.detected,
        recommended_nvidia_technologies=tech_names,
        technical_justification=_build_technical_justification(gap, tech_names),
        business_justification=_build_business_justification(
            gap, profile, classification, recommended_motion
        ),
        priority=priority,
        implementation_complexity=max_complexity,
        suggested_experiment=experiment,
        action=action,
        next_action_for_nvidia_team=next_action,
        evidence_used=gap.evidence_used,
        missing_evidence=missing,
        confidence=gap.confidence,
    )


def build_recommendations(
    startup_name: str,
    profile: StartupProfile,
    classification: ClassificationResult,
    validated_evidence: list[ValidatedEvidence],
    defensibility: DefensibilityScoreResult | None,
    inception_fit: InceptionFitScoreResult | None,
    production_readiness: ProductionReadinessResult | None,
    composite: CompositeResult | None,
    final_priority_score: float,
    recommended_motion: str,
    gap_diagnosis: GapDiagnosisResult,
) -> RecommendationResult:
    recommendations: list[PerGapRecommendation] = []

    for gap in gap_diagnosis.diagnosed_gaps:
        tech_names = [
            c.technology_name
            for c in gap_diagnosis.nvidia_technology_candidates
            if c.addresses_gap == gap.gap
        ]

        rec = build_per_gap_recommendation(
            gap=gap,
            tech_names=tech_names,
            profile=profile,
            classification=classification,
            recommended_motion=recommended_motion,
        )
        recommendations.append(rec)

    overall_priority = _compute_overall_priority(recommendations)
    overall_confidence = _compute_overall_confidence(recommendations)

    top: PerGapRecommendation | None = None
    for r in recommendations:
        if r.action == RecommendedNextAction.APPROACH_NOW:
            if top is None or r.priority.value > top.priority.value:
                top = r

    all_evidence: list[ValidatedEvidence] = list(validated_evidence)
    all_missing: list[str] = list(gap_diagnosis.missing_evidence)
    for r in recommendations:
        if r.detected:
            all_missing.extend(r.missing_evidence)

    lines: list[str] = [
        f"Recommendations for {startup_name}",
        f"Overall priority: {overall_priority.value}",
        f"Overall confidence: {overall_confidence.value}",
        f"Gaps diagnosed: {len([r for r in recommendations if r.detected])}",
        f"Recommendations generated: {len(recommendations)}",
    ]
    for r in recommendations:
        lines.append(
            f"  [{r.action.value}] {r.diagnosed_gap.value}: "
            f"priority={r.priority.value}, "
            f"confidence={r.confidence.value}, "
            f"techs={len(r.recommended_nvidia_technologies)}"
        )

    return RecommendationResult(
        startup_name=startup_name,
        overall_priority=overall_priority,
        overall_confidence=overall_confidence,
        recommendations=recommendations,
        top_recommendation=top,
        reasoning="\n".join(lines),
        evidence_used=all_evidence,
        missing_evidence=all_missing,
    )
