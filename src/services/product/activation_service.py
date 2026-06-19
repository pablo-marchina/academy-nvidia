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

        detected_gaps = [g for g in gap_records if g.detected]
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

            gap_confidences = [
                g.confidence for g in detected_gaps if g.gap_type in matched_gap_types
            ]

            has_nvidia_mapping = any(
                m.technology_name in pb.nvidia_technologies for m in mapping_records
            )

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
            reasoning_parts.append(
                f"Playbook '{pb.name}' matched on gap(s): {', '.join(matched_gap_types)}"
            )
            reasoning_parts.append(f"Gap confidence: {', '.join(gap_confidences)}")
            reasoning_parts.append(f"Evidence coverage: {evidence_coverage:.0%}")
            if unsupported_claim_count > 0:
                reasoning_parts.append(
                    f"Unsupported claims: {unsupported_claim_count} (penalty applied)"
                )
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
                    "technical_experiment": (
                        f"{pb.technical_experiment.title}: {pb.technical_experiment.description}"
                    ),
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

        recommendations.sort(key=lambda r: r["priority"])

        return recommendations

    def persist_recommendations_for_run(
        self,
        analysis_run_id: str,
    ) -> list[dict[str, Any]]:
        recommendations = self.generate_recommendations_for_run(analysis_run_id)
        self.activation_repo.replace_recommendations_for_analysis_run(
            analysis_run_id, recommendations
        )
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
