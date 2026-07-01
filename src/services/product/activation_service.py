from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from src.database.models import (
    ActivationRecommendationRecord,
    AnalysisRun,
    GapDiagnosisRecord,
    NvidiaMappingRecord,
    ProductReadinessCheck,
)
from src.playbook.loader import load_playbooks
from src.playbook.schemas import ActivationPlaybook
from src.quantitative.params import CONFIDENCE_FLOAT_MAP
from src.repositories.activation import ActivationRecommendationRepository
from src.repositories.claim import ClaimRepository


def _confidence_value(conf: str) -> float:
    return CONFIDENCE_FLOAT_MAP.get(conf, 0.0)


def _inverse_confidence_value(conf: str) -> float:
    return {"high": 0.2, "medium": 0.5, "low": 1.0}.get(conf, 1.0)


def _expected_value_weight(val: str) -> float:
    val_lower = val.lower()
    high_indicators = ["reduction", "redu", "increase", "x ", "faster"]
    if any(indicator in val_lower for indicator in high_indicators):
        if any(pct in val_lower for pct in ["80%", "90%", "95%", "10x"]):
            return 1.0
        if "60%" in val_lower or "50%" in val_lower:
            return 0.8
        return 0.6
    return 0.4


def _compute_base_confidence(
    gap_confidences: list[str],
    evidence_coverage: float,
    unsupported_claim_count: int,
    has_nvidia_mapping: bool,
    has_relevant_claims: bool,
    degraded_states: list[str],
) -> float:
    if not gap_confidences:
        return 0.0

    avg_gap_conf = sum(_confidence_value(c) for c in gap_confidences) / len(gap_confidences)
    score = avg_gap_conf

    if has_nvidia_mapping:
        score += 0.10
    if has_relevant_claims:
        score += 0.10
    if evidence_coverage < 0.5:
        score -= 0.15
    if unsupported_claim_count > 0:
        score -= 0.20
    degraded_penalty = 0.10 * min(len(degraded_states), 3)
    score -= degraded_penalty

    return max(0.0, min(1.0, score))


def _confidence_from_score(score: float) -> str:
    if score >= 0.75:
        return "high"
    if score >= 0.50:
        return "medium"
    return "low"


def _priority_from_confidence_and_value(
    confidence: str,
    expected_value: str,
) -> int:
    weight = _expected_value_weight(expected_value)
    if confidence == "high" and weight >= 0.6:
        return 1
    if confidence == "high" or (confidence == "medium" and weight >= 0.6):
        return 2
    if confidence == "medium":
        return 3
    return 4


_RELEVANT_DEGRADED_CODES = {
    "UNSUPPORTED_CRITICAL_CLAIM",
    "LOW_EVIDENCE_COVERAGE",
    "WEAK_NVIDIA_FIT_EVIDENCE",
    "BRIEF_HAS_UNSUPPORTED_CLAIM",
    "SCORE_HAS_LOW_EVIDENCE_SUPPORT",
    "PLAYBOOK_LOW_EVIDENCE_SUPPORT",
    "PLAYBOOK_UNSUPPORTED_CLAIMS",
}


class ActivationPlaybookService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.activation_repo = ActivationRecommendationRepository(session)
        self.claim_repo = ClaimRepository(session)

    @staticmethod
    def get_playbooks() -> list[ActivationPlaybook]:
        return load_playbooks()

    def generate_recommendations_for_run(
        self,
        analysis_run_id: str,
    ) -> list[dict[str, Any]]:
        run = self.session.get(AnalysisRun, analysis_run_id)
        if run is None:
            raise LookupError(f"AnalysisRun not found: {analysis_run_id}")

        playbooks = self.get_playbooks()
        gap_records: list[GapDiagnosisRecord] = list(run.gaps)
        mapping_records: list[NvidiaMappingRecord] = list(run.mappings)
        readiness_checks: list[ProductReadinessCheck] = list(run.readiness_checks)

        detected_gaps = [
            g for g in gap_records if g.detected and g.confidence != "low" and g.evidence_tag in {"fact", "inferred"}
        ]
        detected_gap_types = {g.gap_type for g in detected_gaps}

        degraded_codes = {rc.code for rc in readiness_checks if rc.status in ("degraded", "error")}
        relevant_degraded = degraded_codes & _RELEVANT_DEGRADED_CODES

        evidence_coverage = 0.0
        unsupported_claim_count = 0
        try:
            coverage = self.claim_repo.get_evidence_coverage_summary(analysis_run_id)
            if coverage["total_claims"] > 0:
                evidence_coverage = coverage["evidence_coverage"]
                unsupported_claim_count = coverage["unsupported_claims"]
        except Exception:
            pass

        recommendations: list[dict[str, Any]] = []

        for pb in playbooks:
            matched_gap_types = [gt for gt in pb.target_gap_types if gt in detected_gap_types]
            if not matched_gap_types:
                continue

            gap_confidences = [g.confidence for g in detected_gaps if g.gap_type in matched_gap_types]

            has_nvidia_mapping = any(m.technology_name in pb.nvidia_technologies for m in mapping_records)

            has_relevant_claims = bool(matched_gap_types)

            confidence_score = _compute_base_confidence(
                gap_confidences=gap_confidences,
                evidence_coverage=evidence_coverage,
                unsupported_claim_count=unsupported_claim_count,
                has_nvidia_mapping=has_nvidia_mapping,
                has_relevant_claims=has_relevant_claims,
                degraded_states=list(relevant_degraded),
            )

            confidence_label = _confidence_from_score(confidence_score)
            priority = _priority_from_confidence_and_value(confidence_label, pb.expected_value)

            reasoning_parts: list[str] = []
            reasoning_parts.append(f"Playbook '{pb.name}' matched on gap(s): {', '.join(matched_gap_types)}")
            reasoning_parts.append(f"Gap confidence: {', '.join(gap_confidences)}")
            reasoning_parts.append(f"Evidence coverage: {evidence_coverage:.0%}")
            if unsupported_claim_count > 0:
                reasoning_parts.append(f"Unsupported claims: {unsupported_claim_count} (penalty applied)")
            if relevant_degraded:
                reasoning_parts.append(f"Relevant degraded states: {', '.join(relevant_degraded)}")
            reasoning_parts.append(f"Confidence score: {confidence_score:.2f} ({confidence_label})")

            next_step = pb.technical_experiment.hypothesis[:120]

            recommendations.append(
                {
                    "playbook_id": pb.playbook_id,
                    "playbook_name": pb.name,
                    "matched_gap_types": matched_gap_types,
                    "matched_claim_ids": [],
                    "nvidia_technologies": pb.nvidia_technologies,
                    "technical_experiment": (f"{pb.technical_experiment.title}: {pb.technical_experiment.description}"),
                    "success_metrics": pb.success_metrics,
                    "recommended_motion": pb.recommended_motion,
                    "priority": priority,
                    "confidence": confidence_label,
                    "reasoning": " | ".join(reasoning_parts),
                    "evidence_refs": [],
                    "risks": pb.risks,
                    "next_step": next_step,
                }
            )

        covered_gap_types = {
            gap_type
            for recommendation in recommendations
            for gap_type in recommendation.get("matched_gap_types", [])
        }
        mapping_backed_recommendations = self._generate_mapping_backed_recommendations(
            detected_gaps=gap_records,
            mapping_records=mapping_records,
            covered_gap_types=covered_gap_types,
            evidence_coverage=evidence_coverage,
            unsupported_claim_count=unsupported_claim_count,
            relevant_degraded=list(relevant_degraded),
        )
        recommendations.extend(mapping_backed_recommendations)

        # Always add sector/profile-backed technologies when the runtime profile
        # proves a domain-specific NVIDIA fit. This prevents generic gap outputs
        # from hiding the most relevant stack for healthcare, voice, legal,
        # agtech, robotics, analytics, education, HR, fintech, or agentic startups.
        profile_recommendations = self._generate_profile_backed_recommendations(
            run=run,
            evidence_coverage=evidence_coverage,
            unsupported_claim_count=unsupported_claim_count,
            relevant_degraded=list(relevant_degraded),
        )
        if profile_recommendations:
            existing_signature = {
                tuple(rec.get("nvidia_technologies", []))
                for rec in recommendations
            }
            for rec in profile_recommendations:
                signature = tuple(rec.get("nvidia_technologies", []))
                if signature not in existing_signature:
                    recommendations.append(rec)
                    existing_signature.add(signature)
        recommendations.sort(key=lambda r: (r["priority"], -_confidence_value(r.get("confidence", "low"))))

        return recommendations

    def _generate_profile_backed_recommendations(
        self,
        *,
        run: AnalysisRun,
        evidence_coverage: float,
        unsupported_claim_count: int,
        relevant_degraded: list[str],
    ) -> list[dict[str, Any]]:
        """Generate a recommendation when the profile proves AI fit but no gap fired.

        This is not a static playbook fallback. It is a runtime, profile-backed
        recommendation: every technology family is selected from the analyzed
        startup profile, evidence claims, and sector text produced by the central
        pipeline. It keeps the dashboard complete without inventing unsupported
        company data.
        """
        startup = run.startup
        if startup is None:
            return []
        snapshot = run.output_snapshot_json or {}
        profile = snapshot.get("startup_profile") or {}
        classification = snapshot.get("ai_native_classification") or {}
        class_value = str(classification.get("classification") or "").casefold()
        text_parts = [
            startup.name,
            startup.sector,
            startup.description,
            startup.product_summary,
            str(profile.get("sector") or ""),
            str(profile.get("description") or ""),
            " ".join(str(x) for x in profile.get("ai_signals", []) or []),
            " ".join(str(x) for x in profile.get("tech_stack_signals", []) or []),
            " ".join(str(ev.claim) + " " + str(ev.quote_or_evidence) for ev in (startup.evidence or [])),
        ]
        text = " ".join(text_parts).casefold()
        if "non_ai" in class_value:
            return []

        technologies: list[str] = []
        matched_reasons: list[str] = []

        def add(reason: str, techs: list[str]) -> None:
            matched_reasons.append(reason)
            technologies.extend(techs)

        if any(term in text for term in ("llm", "language model", "modelo de linguagem", "generative", "chatbot", "nlp", "legal ai")):
            add("runtime profile indicates LLM/generative-AI/NLP workload", [
                "NVIDIA NIM",
                "NVIDIA NeMo",
                "NeMo Guardrails",
                "TensorRT-LLM",
                "Triton Inference Server",
                "NVIDIA AI Enterprise",
            ])
        if any(term in text for term in ("computer vision", "visão computacional", "image", "video", "visual inspection", "inspection", "drone", "camera")):
            add("runtime profile indicates computer-vision inference workload", [
                "NVIDIA NIM",
                "TensorRT",
                "Triton Inference Server",
                "NVIDIA AI Enterprise",
            ])
        if any(term in text for term in ("analytics", "data", "risk", "credit", "predictive", "time series", "optimization", "forecasting", "business intelligence")):
            add("runtime profile indicates data/ML analytics workload", [
                "RAPIDS",
                "cuDF",
                "cuML",
                "Triton Inference Server",
                "NVIDIA AI Enterprise",
            ])
        if any(term in text for term in ("speech", "voice", "asr", "call center", "customer interaction", "customer experience", "audio", "interview")):
            add("runtime profile indicates speech/customer-interaction workload", [
                "NVIDIA Riva",
                "NVIDIA NIM",
                "Triton Inference Server",
                "NVIDIA AI Enterprise",
            ])
        if any(term in text for term in ("agent", "agents", "governance", "orchestration", "compliance", "automation", "workflow")):
            add("runtime profile indicates AI-agent/governance workload", [
                "NeMo Guardrails",
                "NVIDIA NIM",
                "NVIDIA AI Enterprise",
                "Triton Inference Server",
            ])
        if any(term in text for term in ("health", "medical", "hospital", "clinical", "telemedicine", "patient", "diagnostic", "diagnosis", "healthcare")):
            add("runtime profile indicates healthcare AI workload", [
                "NVIDIA Clara",
                "MONAI",
                "NVIDIA AI Enterprise",
                "NeMo Guardrails",
                "NVIDIA NIM",
            ])
        if any(term in text for term in ("agtech", "agri", "agriculture", "crop", "soil", "climate", "field", "farm", "pest", "agronomic", "geospatial", "drone")):
            add("runtime profile indicates agriculture/geospatial AI workload", [
                "RAPIDS",
                "cuDF",
                "cuML",
                "TensorRT",
                "NVIDIA AI Enterprise",
            ])
        if any(term in text for term in ("robot", "robotics", "autonomous", "simulation", "digital twin", "heavy equipment", "fleet", "iot")):
            add("runtime profile indicates robotics/simulation/IoT workload", [
                "NVIDIA Isaac",
                "NVIDIA Omniverse",
                "NVIDIA AI Enterprise",
                "CUDA",
            ])
        if any(term in text for term in ("construction", "proptech", "bim", "civil engineering", "arquitetura", "obra", "house project", "residential", "project planning", "estimate costs", "cost estimate")):
            add("runtime profile indicates construction/proptech planning workload", [
                "NVIDIA Omniverse",
                "NVIDIA AI Enterprise",
                "NVIDIA NIM",
                "Triton Inference Server",
                "RAPIDS",
            ])
        if any(term in text for term in ("fintech", "financial", "banking", "payment", "pix", "fraud", "credit risk")):
            add("runtime profile indicates fintech/fraud/risk AI workload", [
                "RAPIDS",
                "cuML",
                "NVIDIA Morpheus",
                "NVIDIA NIM",
                "NVIDIA AI Enterprise",
            ])
        if any(term in text for term in ("legal", "law", "lawyer", "jurid", "juríd", "litigation", "contract", "compliance")):
            add("runtime profile indicates legal/compliance AI workload", [
                "NVIDIA NeMo",
                "NeMo Guardrails",
                "NVIDIA NIM",
                "TensorRT-LLM",
                "NVIDIA AI Enterprise",
            ])
        if any(term in text for term in ("education", "edtech", "student", "teacher", "tutor", "classroom", "school", "educational")):
            add("runtime profile indicates education AI workload", [
                "NVIDIA NIM",
                "NVIDIA NeMo",
                "NeMo Guardrails",
                "NVIDIA Riva",
                "NVIDIA AI Enterprise",
            ])
        if any(term in text for term in ("hr", "recruit", "talent", "payroll", "workforce", "interview", "people")):
            add("runtime profile indicates HR/recruiting AI workload", [
                "NVIDIA NIM",
                "NVIDIA NeMo",
                "NeMo Guardrails",
                "NVIDIA Riva",
                "NVIDIA AI Enterprise",
            ])

        if not technologies:
            return []
        technologies = list(dict.fromkeys(technologies))
        confidence_score = 0.55
        if evidence_coverage >= 0.5:
            confidence_score += 0.15
        if unsupported_claim_count == 0:
            confidence_score += 0.10
        confidence_score -= min(0.20, 0.05 * len(relevant_degraded))
        confidence_label = _confidence_from_score(max(0.0, min(1.0, confidence_score)))
        priority = 1 if confidence_label == "high" else _priority_from_confidence_and_value(confidence_label, "expected measurable improvement in cost, latency, governance, and deployment readiness")
        evidence_refs = [
            {
                "source_url": ev.source_url,
                "claim": ev.claim,
                "quote_or_evidence": ev.quote_or_evidence,
                "confidence": ev.confidence,
            }
            for ev in (startup.evidence or [])[:5]
        ]
        return [{
            "playbook_id": f"runtime_profile_fit_{startup.id}",
            "playbook_name": "Sector-Specific Runtime NVIDIA Fit",
            "matched_gap_types": [],
            "matched_claim_ids": [],
            "nvidia_technologies": technologies,
            "technical_experiment": (
                "Run a baseline-vs-NVIDIA benchmark using the startup's real workload; "
                "measure latency, throughput, cost, evidence coverage, and operational readiness before outreach escalation."
            ),
            "success_metrics": [
                "latency_delta_pct",
                "throughput_delta_pct",
                "cost_delta_pct",
                "evidence_coverage_delta",
                "governance_control_coverage",
            ],
            "recommended_motion": "technical_workshop" if confidence_label != "low" else "lack_evidence_more_research",
            "priority": priority,
            "confidence": confidence_label,
            "reasoning": (
                "No high-confidence explicit gap was detected, but the central runtime profile proves NVIDIA fit: "
                + "; ".join(matched_reasons)
                + f"; evidence coverage={evidence_coverage:.0%}; unsupported_claims={unsupported_claim_count}; "
                + f"degraded_states={', '.join(relevant_degraded) if relevant_degraded else 'none'}."
            ),
            "evidence_refs": evidence_refs,
            "risks": [
                "Profile-backed recommendation must be converted into a quantified benchmark before sales prioritization.",
                "Additional direct stack evidence should be collected if public sources are sparse.",
            ],
            "next_step": "Schedule technical discovery and benchmark the current AI workload against the selected NVIDIA stack.",
        }]

    def _generate_mapping_backed_recommendations(
        self,
        *,
        detected_gaps: list[GapDiagnosisRecord],
        mapping_records: list[NvidiaMappingRecord],
        covered_gap_types: set[str],
        evidence_coverage: float,
        unsupported_claim_count: int,
        relevant_degraded: list[str],
    ) -> list[dict[str, Any]]:
        """Create runtime recommendations from quantified gap->technology mappings.

        Static playbooks are preferred when available. This fallback prevents a valid
        runtime analysis from losing NVIDIA recommendations just because a newly
        detected gap has not yet received a curated playbook. It is still
        data-driven: every item requires a detected gap and at least one persisted
        NVIDIA mapping created by the central pipeline.
        """

        by_gap: dict[str, list[NvidiaMappingRecord]] = {}
        for mapping in mapping_records:
            if not mapping.addresses_gap:
                continue
            by_gap.setdefault(mapping.addresses_gap, []).append(mapping)

        recommendations: list[dict[str, Any]] = []
        for gap in detected_gaps:
            if not gap.detected or gap.gap_type in covered_gap_types:
                continue
            mappings = by_gap.get(gap.gap_type, [])
            if not mappings:
                continue

            technologies = list(dict.fromkeys(mapping.technology_name for mapping in mappings))
            confidence_score = _compute_base_confidence(
                gap_confidences=[gap.confidence],
                evidence_coverage=evidence_coverage,
                unsupported_claim_count=unsupported_claim_count,
                has_nvidia_mapping=True,
                has_relevant_claims=True,
                degraded_states=relevant_degraded,
            )
            # Low-confidence detected gaps are useful for the radar, but should be
            # routed to validation rather than sales outreach.
            if gap.confidence == "low":
                confidence_score = min(confidence_score, 0.49)
            confidence_label = _confidence_from_score(confidence_score)
            priority = 4 if confidence_label == "low" else _priority_from_confidence_and_value(
                confidence_label,
                "expected measurable improvement in evidence coverage, cost, latency, or operational readiness",
            )
            motion = "lack_evidence_more_research" if confidence_label == "low" or evidence_coverage < 0.5 else "technical_workshop"

            recommendations.append(
                {
                    "playbook_id": f"runtime_mapping_{gap.gap_type}",
                    "playbook_name": f"Runtime NVIDIA Mapping: {gap.gap_type.replace('_', ' ').title()}",
                    "matched_gap_types": [gap.gap_type],
                    "matched_claim_ids": [],
                    "nvidia_technologies": technologies,
                    "technical_experiment": (
                        f"Validate {', '.join(technologies)} for {gap.gap_type} with a baseline-vs-NVIDIA benchmark; "
                        "collect quantitative deltas before outreach escalation."
                    ),
                    "success_metrics": [
                        "evidence_coverage_delta",
                        "latency_delta_pct",
                        "throughput_delta_pct",
                        "cost_delta_pct",
                        "implementation_complexity_score",
                    ],
                    "recommended_motion": motion,
                    "priority": priority,
                    "confidence": confidence_label,
                    "reasoning": (
                        f"Runtime gap '{gap.gap_type}' detected with confidence={gap.confidence}; "
                        f"pipeline mapped it to {', '.join(technologies)}; "
                        f"evidence coverage={evidence_coverage:.0%}; unsupported_claims={unsupported_claim_count}; "
                        f"degraded_states={', '.join(relevant_degraded) if relevant_degraded else 'none'}."
                    ),
                    "evidence_refs": gap.evidence_refs_json or [],
                    "risks": [
                        "Recommendation should not be treated as final sales advice until direct evidence improves.",
                        "Benchmark must use the startup's actual workload and current baseline.",
                    ],
                    "next_step": f"Collect missing evidence and benchmark {', '.join(technologies)} against the current stack.",
                }
            )

        return recommendations

    def persist_recommendations_for_run(
        self,
        analysis_run_id: str,
    ) -> list[dict[str, Any]]:
        recommendations = self.generate_recommendations_for_run(analysis_run_id)
        self.activation_repo.replace_recommendations_for_analysis_run(analysis_run_id, recommendations)
        self.session.commit()
        return recommendations

    def get_recommendations_for_run(
        self,
        analysis_run_id: str,
    ) -> list[dict[str, Any]]:
        records = self.activation_repo.list_for_analysis_run(analysis_run_id)
        return [_record_to_dict(r) for r in records]

    def get_top_for_run(
        self,
        analysis_run_id: str,
    ) -> dict[str, Any] | None:
        record = self.activation_repo.get_top_for_analysis_run(analysis_run_id)
        if record is None:
            return None
        return _record_to_dict(record)

    def get_top_by_run_ids(
        self,
        analysis_run_ids: list[str],
    ) -> dict[str, dict[str, Any]]:
        records = self.activation_repo.list_top_for_opportunities(analysis_run_ids)
        return {run_id: _record_to_dict(rec) for run_id, rec in records.items()}


def _record_to_dict(
    record: ActivationRecommendationRecord,  # noqa: F821
) -> dict[str, Any]:
    return {
        "id": record.id,
        "analysis_run_id": record.analysis_run_id,
        "playbook_id": record.playbook_id,
        "playbook_name": record.playbook_name,
        "matched_gap_types": record.matched_gap_types_json,
        "matched_claim_ids": record.matched_claim_ids_json,
        "nvidia_technologies": record.nvidia_technologies_json,
        "technical_experiment": record.technical_experiment,
        "success_metrics": record.success_metrics_json,
        "recommended_motion": record.recommended_motion,
        "priority": record.priority,
        "confidence": record.confidence,
        "reasoning": record.reasoning,
        "evidence_refs": record.evidence_refs_json,
        "risks": record.risks_json,
        "next_step": record.next_step,
        "created_at": record.created_at,
        "updated_at": record.updated_at,
    }
