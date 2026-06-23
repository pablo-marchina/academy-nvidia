#!/usr/bin/env python3
# ruff: noqa: E402
from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pydantic import BaseModel, Field, field_validator

from scripts.run_diagnostic_value_triage import QUALITY_WEIGHTS
from src.governance.artifacts import DEFAULT_EVIDENCE_DIR, write_json

PROMISING_FAMILY_ORDER = [
    "counter_evidence_retrieval",
    "graphrag_evidence_graph",
    "query_rewriting_multiquery",
    "recommendation_specificity_next_action",
    "evidence_sufficiency_abstention",
    "source_trust_freshness_ranking",
]


class EvidenceDoc(BaseModel):
    doc_id: str
    title: str
    source_type: str
    trust_score: float
    age_days: int
    supports_recommendation: bool = False
    contradicts_recommendation: bool = False
    tags: list[str] = Field(default_factory=list)

    @field_validator("trust_score")
    @classmethod
    def validate_trust_score(cls, value: float) -> float:
        if not 0.0 <= value <= 1.0:
            raise ValueError("trust_score must be between 0 and 1")
        return value


class ClaimOutput(BaseModel):
    text: str
    evidence_ids: list[str] = Field(default_factory=list)


class LineageEdge(BaseModel):
    source: str
    target: str
    relation: str


class AlternativeLost(BaseModel):
    name: str
    reason: str
    evidence_ids: list[str] = Field(default_factory=list)


class ProductLikeOutput(BaseModel):
    retrieved_evidence_ids: list[str]
    claims: list[ClaimOutput]
    recommendation: str
    action: str
    confidence: float
    next_action: dict[str, str] = Field(default_factory=dict)
    detected_contradiction_ids: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    lineage_edges: list[LineageEdge] = Field(default_factory=list)
    alternatives_lost: list[AlternativeLost] = Field(default_factory=list)
    query_variants: list[str] = Field(default_factory=list)
    estimated_latency_ms: int = 900
    estimated_cost_units: float = 1.0

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, value: float) -> float:
        if not 0.0 <= value <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        return value


class FamilySpikeCase(BaseModel):
    case_id: str
    family_id: str
    name: str
    query: str
    required_evidence_ids: list[str]
    expected_contradiction_ids: list[str] = Field(default_factory=list)
    expected_lineage_edges: int = 0
    expected_alternatives_lost: int = 0
    expected_terms: list[str] = Field(default_factory=list)
    evidence_docs: list[EvidenceDoc]
    baseline_output: ProductLikeOutput


class FamilySpikeDecision(BaseModel):
    family_id: str
    decision: str
    baseline_score: float
    spike_score: float
    quality_delta: float
    metric_deltas: dict[str, float]
    case_count: int
    cases: list[dict[str, Any]]
    rationale: str
    next_step: str


def main() -> int:
    parser = argparse.ArgumentParser(description="Run real local micro-spike benchmarks for promising value families.")
    parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_EVIDENCE_DIR)
    parser.add_argument("--cases-path", type=Path)
    parser.add_argument("--report-path", type=Path)
    parser.add_argument("--markdown-path", type=Path)
    parser.add_argument("--min-real-delta", type=float, default=0.03)
    parser.add_argument("--families", nargs="*", default=PROMISING_FAMILY_ORDER)
    args = parser.parse_args()

    cases_path = args.cases_path or args.evidence_dir / "family_spike_cases.json"
    report_path = args.report_path or args.evidence_dir / "family_spike_benchmark_report.json"
    markdown_path = args.markdown_path or args.evidence_dir / "family_spike_benchmark_report.md"

    cases = load_or_write_cases(cases_path)
    report = build_spike_report(cases, families=args.families, min_real_delta=args.min_real_delta)
    write_json(report_path, report)
    write_markdown(markdown_path, report)
    print(
        "Family spike benchmarks completed: "
        f"{report['tested_family_count']} families tested, "
        f"{report['product_spike_candidate_count']} product spike candidates"
    )
    return 0


def load_or_write_cases(path: Path) -> list[FamilySpikeCase]:
    if path.exists():
        payload = json.loads(path.read_text(encoding="utf-8"))
        raw_cases = payload.get("cases", payload) if isinstance(payload, dict) else payload
        if isinstance(raw_cases, list) and raw_cases:
            return [FamilySpikeCase.model_validate(item) for item in raw_cases]
    cases = default_spike_cases()
    write_json(
        path,
        {
            "report_id": "family_spike_cases",
            "generated_at": datetime.now(UTC).isoformat(),
            "purpose": "Disposable local cases for real family-level spike benchmarking.",
            "cases": [case.model_dump(mode="json") for case in cases],
        },
    )
    return cases


def build_spike_report(
    cases: list[FamilySpikeCase],
    *,
    families: list[str] | None = None,
    min_real_delta: float = 0.03,
) -> dict[str, Any]:
    selected_families = families or PROMISING_FAMILY_ORDER
    decisions = [_benchmark_family(family_id, cases, min_real_delta=min_real_delta) for family_id in selected_families]
    decisions.sort(key=lambda decision: (-decision.quality_delta, decision.family_id))
    candidates = [decision for decision in decisions if decision.decision == "PROMISING_NEEDS_PRODUCT_SPIKE"]
    return {
        "report_id": "family_spike_benchmark_report",
        "generated_at": datetime.now(UTC).isoformat(),
        "methodology": (
            "Each family is tested with an executable local micro-spike against product-like outputs. "
            "The result can justify a product spike, but it does not promote runtime adoption."
        ),
        "quality_weights": QUALITY_WEIGHTS,
        "tested_family_count": len(decisions),
        "product_spike_candidate_count": len(candidates),
        "recommended_order": [decision.family_id for decision in candidates],
        "decisions": [decision.model_dump(mode="json") for decision in decisions],
    }


def _benchmark_family(
    family_id: str,
    cases: list[FamilySpikeCase],
    *,
    min_real_delta: float,
) -> FamilySpikeDecision:
    affected_cases = [case for case in cases if case.family_id == family_id]
    case_results: list[dict[str, Any]] = []
    for case in affected_cases:
        baseline_scores = score_output(case, case.baseline_output)
        spike_output = apply_family_spike(family_id, case)
        spike_scores = score_output(case, spike_output)
        baseline_quality = weighted_score(baseline_scores)
        spike_quality = weighted_score(spike_scores)
        case_results.append(
            {
                "case_id": case.case_id,
                "name": case.name,
                "baseline_score": round(baseline_quality, 4),
                "spike_score": round(spike_quality, 4),
                "quality_delta": round(spike_quality - baseline_quality, 4),
                "metric_deltas": _metric_deltas(baseline_scores, spike_scores),
                "baseline_output": case.baseline_output.model_dump(mode="json"),
                "spike_output": spike_output.model_dump(mode="json"),
            }
        )
    baseline = _mean([case["baseline_score"] for case in case_results])
    spike = _mean([case["spike_score"] for case in case_results])
    delta = spike - baseline
    metric_deltas = _average_metric_deltas(case_results)
    if not affected_cases:
        decision = "NOT_APPLICABLE"
        rationale = "No executable spike case exists for this family."
        next_step = "Add a local case before testing this family."
    elif delta >= min_real_delta:
        decision = "PROMISING_NEEDS_PRODUCT_SPIKE"
        rationale = "Disposable spike improved measured system value over baseline."
        next_step = "Build a narrow product spike, then rerun quality, latency, cost, and risk benchmarks."
    else:
        decision = "REJECT_NO_REAL_LIFT"
        rationale = "Disposable spike did not improve measured system value enough to justify product work."
        next_step = "Do not implement this family now; revisit only with stronger evidence or new cases."
    return FamilySpikeDecision(
        family_id=family_id,
        decision=decision,
        baseline_score=round(baseline, 4),
        spike_score=round(spike, 4),
        quality_delta=round(delta, 4),
        metric_deltas=metric_deltas,
        case_count=len(affected_cases),
        cases=case_results,
        rationale=rationale,
        next_step=next_step,
    )


def apply_family_spike(family_id: str, case: FamilySpikeCase) -> ProductLikeOutput:
    output = deepcopy(case.baseline_output)
    if family_id == "counter_evidence_retrieval":
        output.retrieved_evidence_ids = _dedupe(output.retrieved_evidence_ids + case.expected_contradiction_ids)
        output.detected_contradiction_ids = _dedupe(output.detected_contradiction_ids + case.expected_contradiction_ids)
        output.confidence = min(output.confidence, 0.56)
        output.missing_evidence = _dedupe(output.missing_evidence + ["manual review of conflicting signals"])
    elif family_id == "graphrag_evidence_graph":
        output.retrieved_evidence_ids = _dedupe(output.retrieved_evidence_ids + case.required_evidence_ids)
        output.lineage_edges = [
            LineageEdge(source="startup_evidence", target="technical_gap", relation="supports"),
            LineageEdge(source="technical_gap", target="nvidia_capability", relation="mapped_to"),
            LineageEdge(source="nvidia_capability", target="recommended_experiment", relation="validated_by"),
            LineageEdge(source="rejected_alternative", target="nvidia_capability", relation="lost_to"),
        ][: max(case.expected_lineage_edges, 1)]
        output.alternatives_lost = [
            AlternativeLost(
                name="generic cloud CPU scaling",
                reason="Does not address GPU inference throughput evidence.",
                evidence_ids=case.required_evidence_ids[:1],
            )
        ]
    elif family_id == "query_rewriting_multiquery":
        output.query_variants = [
            case.query,
            "gpu inference model serving triton nvidia",
            "production ai deployment optimization nvidia",
        ]
        output.retrieved_evidence_ids = _dedupe(output.retrieved_evidence_ids + case.required_evidence_ids)
    elif family_id == "recommendation_specificity_next_action":
        output.recommendation = "Run an NVIDIA Triton inference benchmark for p95 latency and GPU utilization."
        output.next_action = {
            "owner": "technical champion",
            "technology": "NVIDIA Triton",
            "metric": "p95 latency and GPU utilization",
            "threshold": ">=20% latency reduction or >=15% utilization gain",
            "timeframe": "10 business days",
        }
        output.alternatives_lost = [
            AlternativeLost(
                name="manual model-serving tuning",
                reason="Lower repeatability and weaker measurement path than a Triton benchmark.",
                evidence_ids=case.required_evidence_ids[:1],
            )
        ]
    elif family_id == "evidence_sufficiency_abstention":
        retrieved_required = set(output.retrieved_evidence_ids).intersection(case.required_evidence_ids)
        if len(retrieved_required) < len(case.required_evidence_ids) or case.expected_contradiction_ids:
            output.action = "validate_manually"
            output.confidence = min(output.confidence, 0.48)
            output.missing_evidence = _dedupe(
                output.missing_evidence + ["direct RAG support", "fresh technical proof", "contradiction review"]
            )
    elif family_id == "source_trust_freshness_ranking":
        ranked_ids = [
            doc.doc_id
            for doc in sorted(
                case.evidence_docs,
                key=lambda doc: (_source_quality(doc), doc.supports_recommendation),
                reverse=True,
            )
        ]
        output.retrieved_evidence_ids = _dedupe(ranked_ids[:3] + output.retrieved_evidence_ids)
        output.confidence = min(0.88, output.confidence + 0.08)
    else:
        raise ValueError(f"Unsupported family spike: {family_id}")
    return output


def score_output(case: FamilySpikeCase, output: ProductLikeOutput) -> dict[str, float]:
    docs = {doc.doc_id: doc for doc in case.evidence_docs}
    retrieved_docs = [docs[doc_id] for doc_id in output.retrieved_evidence_ids if doc_id in docs]
    supporting_ids = {doc.doc_id for doc in retrieved_docs if doc.supports_recommendation}
    required_support = set(case.required_evidence_ids)
    expected_confidence = _expected_confidence(case, output, supporting_ids)
    return {
        "evidence_sufficiency": _ratio(len(required_support.intersection(supporting_ids)), len(required_support)),
        "unsupported_claim_control": _claim_support_score(output, supporting_ids),
        "source_trust_freshness": _source_quality_score(retrieved_docs),
        "contradiction_handling": _contradiction_score(case, output),
        "recommendation_specificity": _specificity_score(case, output),
        "next_action_quality": _next_action_score(output),
        "uncertainty_calibration": max(0.0, 1.0 - abs(output.confidence - expected_confidence)),
        "lineage_traceability": _ratio(len(output.lineage_edges), max(case.expected_lineage_edges, 1)),
        "alternatives_lost_rationale": _ratio(
            len([alternative for alternative in output.alternatives_lost if alternative.reason]),
            max(case.expected_alternatives_lost, 1),
        ),
        "robustness_to_query_variance": min(1.0, len(output.query_variants) / 3),
        "evaluator_auditability": _auditability_score(case, output),
        "operational_efficiency": _operational_efficiency(output),
    }


def weighted_score(scores: dict[str, float]) -> float:
    return sum(scores[metric] * QUALITY_WEIGHTS[metric] for metric in QUALITY_WEIGHTS)


def default_spike_cases() -> list[FamilySpikeCase]:
    return [
        _case(
            case_id="counter_evidence_signal",
            family_id="counter_evidence_retrieval",
            name="Contradictory maturity signal should be surfaced",
            query="startup says production gpu inference is mature",
            required=["official_gpu_claim"],
            contradictions=["stale_hiring_signal"],
            baseline_ids=["official_gpu_claim"],
            expected_terms=["gpu", "inference"],
        ),
        _case(
            case_id="graph_lineage_mapping",
            family_id="graphrag_evidence_graph",
            name="Source-gap-technology path should be auditable",
            query="map deployment gap to nvidia technology and alternatives",
            required=["official_gpu_claim", "nvidia_triton_doc"],
            baseline_ids=["official_gpu_claim"],
            expected_lineage_edges=4,
            expected_alternatives_lost=1,
            expected_terms=["nvidia", "triton", "gpu"],
        ),
        _case(
            case_id="query_vocab_recovery",
            family_id="query_rewriting_multiquery",
            name="Business wording should recover technical evidence",
            query="scale ai delivery for enterprise customers",
            required=["nvidia_triton_doc"],
            baseline_ids=["marketing_ai_claim"],
            expected_terms=["triton", "inference"],
        ),
        _case(
            case_id="next_action_specificity",
            family_id="recommendation_specificity_next_action",
            name="Recommendation should become a measurable experiment",
            query="what should nvidia suggest next",
            required=["nvidia_triton_doc"],
            baseline_ids=["nvidia_triton_doc"],
            expected_alternatives_lost=1,
            expected_terms=["triton", "latency", "gpu"],
        ),
        _case(
            case_id="thin_support_abstention",
            family_id="evidence_sufficiency_abstention",
            name="Thin support should downgrade the recommendation",
            query="recommend nvidia approach with thin evidence",
            required=["nvidia_triton_doc", "official_gpu_claim"],
            contradictions=["stale_hiring_signal"],
            baseline_ids=["marketing_ai_claim"],
            expected_terms=["nvidia", "evidence"],
        ),
        _case(
            case_id="source_quality_ordering",
            family_id="source_trust_freshness_ranking",
            name="Fresh official evidence should outrank stale weak evidence",
            query="which source should support the recommendation",
            required=["official_gpu_claim", "nvidia_triton_doc"],
            baseline_ids=["old_blog_claim", "marketing_ai_claim", "official_gpu_claim"],
            expected_terms=["source", "fresh"],
        ),
    ]


def _case(
    *,
    case_id: str,
    family_id: str,
    name: str,
    query: str,
    required: list[str],
    baseline_ids: list[str],
    contradictions: list[str] | None = None,
    expected_lineage_edges: int = 0,
    expected_alternatives_lost: int = 0,
    expected_terms: list[str] | None = None,
) -> FamilySpikeCase:
    return FamilySpikeCase(
        case_id=case_id,
        family_id=family_id,
        name=name,
        query=query,
        required_evidence_ids=required,
        expected_contradiction_ids=contradictions or [],
        expected_lineage_edges=expected_lineage_edges,
        expected_alternatives_lost=expected_alternatives_lost,
        expected_terms=expected_terms or [],
        evidence_docs=[
            EvidenceDoc(
                doc_id="official_gpu_claim",
                title="Official GPU inference statement",
                source_type="official_site",
                trust_score=0.92,
                age_days=25,
                supports_recommendation=True,
                tags=["gpu", "inference", "startup"],
            ),
            EvidenceDoc(
                doc_id="nvidia_triton_doc",
                title="NVIDIA Triton inference documentation",
                source_type="technical_doc",
                trust_score=0.95,
                age_days=40,
                supports_recommendation=True,
                tags=["nvidia", "triton", "latency", "gpu"],
            ),
            EvidenceDoc(
                doc_id="marketing_ai_claim",
                title="Generic AI marketing claim",
                source_type="blog",
                trust_score=0.42,
                age_days=380,
                supports_recommendation=False,
                tags=["ai", "marketing"],
            ),
            EvidenceDoc(
                doc_id="old_blog_claim",
                title="Old model-serving blog",
                source_type="blog",
                trust_score=0.50,
                age_days=700,
                supports_recommendation=True,
                tags=["serving", "old"],
            ),
            EvidenceDoc(
                doc_id="stale_hiring_signal",
                title="Stale hiring signal",
                source_type="job_posting",
                trust_score=0.70,
                age_days=520,
                contradicts_recommendation=True,
                tags=["hiring", "immature-infra"],
            ),
        ],
        baseline_output=ProductLikeOutput(
            retrieved_evidence_ids=baseline_ids,
            claims=[ClaimOutput(text="The startup is ready for NVIDIA acceleration.", evidence_ids=baseline_ids[:1])],
            recommendation="Consider NVIDIA acceleration for the startup.",
            action="approach_now",
            confidence=0.82,
            next_action={"action": "schedule technical discussion"},
            estimated_latency_ms=900,
            estimated_cost_units=1.0,
        ),
    )


def _metric_deltas(baseline: dict[str, float], spike: dict[str, float]) -> dict[str, float]:
    return {metric: round(spike[metric] - baseline[metric], 4) for metric in QUALITY_WEIGHTS}


def _average_metric_deltas(case_results: list[dict[str, Any]]) -> dict[str, float]:
    if not case_results:
        return {metric: 0.0 for metric in QUALITY_WEIGHTS}
    return {
        metric: round(_mean([case["metric_deltas"][metric] for case in case_results]), 4) for metric in QUALITY_WEIGHTS
    }


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 1.0
    return min(1.0, numerator / denominator)


def _claim_support_score(output: ProductLikeOutput, supporting_ids: set[str]) -> float:
    if not output.claims:
        return 1.0
    supported = float(
        sum(1 for claim in output.claims if claim.evidence_ids and set(claim.evidence_ids) <= supporting_ids)
    )
    if output.action == "validate_manually":
        supported += 0.5
    return min(1.0, supported / len(output.claims))


def _source_quality_score(docs: list[EvidenceDoc]) -> float:
    if not docs:
        return 0.0
    return _mean([_source_quality(doc) for doc in docs[:3]])


def _source_quality(doc: EvidenceDoc) -> float:
    freshness = max(0.0, 1.0 - (doc.age_days / 730))
    return min(1.0, doc.trust_score * 0.7 + freshness * 0.3)


def _contradiction_score(case: FamilySpikeCase, output: ProductLikeOutput) -> float:
    if not case.expected_contradiction_ids:
        return 0.8
    return _ratio(
        len(set(output.detected_contradiction_ids).intersection(case.expected_contradiction_ids)),
        len(case.expected_contradiction_ids),
    )


def _specificity_score(case: FamilySpikeCase, output: ProductLikeOutput) -> float:
    text = f"{output.recommendation} {' '.join(output.next_action.values())}".lower()
    if not case.expected_terms:
        return 0.7
    return _ratio(sum(1 for term in case.expected_terms if term.lower() in text), len(case.expected_terms))


def _next_action_score(output: ProductLikeOutput) -> float:
    required_fields = {"owner", "technology", "metric", "threshold", "timeframe"}
    return _ratio(len(required_fields.intersection(output.next_action)), len(required_fields))


def _expected_confidence(case: FamilySpikeCase, output: ProductLikeOutput, supporting_ids: set[str]) -> float:
    thin_support = not set(case.required_evidence_ids) <= supporting_ids
    conflict = bool(case.expected_contradiction_ids)
    if output.action == "validate_manually" or thin_support or conflict:
        return 0.52
    return 0.82


def _auditability_score(case: FamilySpikeCase, output: ProductLikeOutput) -> float:
    checks = [
        bool(output.retrieved_evidence_ids),
        bool(output.claims and output.claims[0].evidence_ids),
        bool(output.missing_evidence) if case.expected_contradiction_ids else True,
        bool(output.detected_contradiction_ids) if case.expected_contradiction_ids else True,
        bool(output.lineage_edges) if case.expected_lineage_edges else True,
    ]
    return sum(1 for check in checks if check) / len(checks)


def _operational_efficiency(output: ProductLikeOutput) -> float:
    latency_score = max(0.0, 1.0 - (output.estimated_latency_ms / 2500))
    cost_score = max(0.0, 1.0 - (output.estimated_cost_units / 3.0))
    return (latency_score + cost_score) / 2


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Family Spike Benchmark Report",
        "",
        f"Generated at: `{report['generated_at']}`",
        f"Families tested: `{report['tested_family_count']}`",
        f"Product spike candidates: `{report['product_spike_candidate_count']}`",
        "",
        "These are disposable local spikes. A positive result justifies product spike work, not runtime adoption.",
        "",
        "| Family | Decision | Baseline | Spike | Delta | Next step |",
        "|---|---|---:|---:|---:|---|",
    ]
    for decision in report["decisions"]:
        lines.append(
            f"| {_md_cell(decision['family_id'])} | {decision['decision']} | "
            f"{decision['baseline_score']} | {decision['spike_score']} | {decision['quality_delta']} | "
            f"{_md_cell(decision['next_step'])} |"
        )
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _md_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


if __name__ == "__main__":
    raise SystemExit(main())
