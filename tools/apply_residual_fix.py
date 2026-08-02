from __future__ import annotations

from pathlib import Path


def update_workload_classifier() -> None:
    path = Path("src/services/product/workload_classifier.py")
    text = path.read_text(encoding="utf-8")
    if '"big data": 3.5,' not in text:
        text = text.replace(
            '            "tabular data": 3.0,\n',
            '            "tabular data": 3.0,\n'
            '            "big data": 3.5,\n'
            '            "data science": 3.0,\n'
            '            "enterprise analytics": 3.0,\n'
            '            "accelerated analytics": 4.0,\n',
        )
    path.write_text(text, encoding="utf-8")


def update_radar_dashboard() -> None:
    path = Path("src/services/product/radar_dashboard_service.py")
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        '            "top_gaps": item.get("top_gaps", []),\n',
        '            "top_gaps": self._relevant_top_gaps(run),\n',
    )
    if "def _relevant_top_gaps(" not in text:
        anchor = "    def _startup_row(self, startup: Startup, latest: AnalysisRun | None) -> dict[str, Any]:\n"
        method = '''    @staticmethod
    def _relevant_top_gaps(run: AnalysisRun | None) -> list[str]:
        """Expose only evidence-supported, medium/high-confidence runtime gaps."""
        if run is None or run.startup is None:
            return []

        from src.services.product.workload_classifier import classify_workloads, needs_guardrails

        startup = run.startup
        evidence_text = " ".join(
            f"{evidence.claim} {evidence.quote_or_evidence}"
            for evidence in (startup.evidence or [])
        )
        profile = (run.output_snapshot_json or {}).get("startup_profile") or {}
        text = " ".join(
            [
                str(startup.description or ""),
                str(startup.product_summary or ""),
                str(profile.get("description") or ""),
                " ".join(str(value) for value in profile.get("ai_signals", []) or []),
                " ".join(str(value) for value in profile.get("tech_stack_signals", []) or []),
                evidence_text,
            ]
        )
        matches = classify_workloads(text, max_families=2)
        if not matches:
            return []

        family_gaps = {
            "llm_nlp": {
                "agent_governance_gap",
                "model_evaluation_gap",
                "observability_gap",
                "high_latency",
                "high_inference_cost",
                "external_api_dependency",
            },
            "voice": {"voice_need", "high_latency", "observability_gap"},
            "computer_vision": {"computer_vision_need", "high_latency", "observability_gap"},
            "tabular_ml": {
                "heavy_tabular_processing",
                "slow_data_pipeline",
                "high_training_cost",
                "high_inference_cost",
            },
            "robotics_simulation": {"robotics_need", "simulation_need"},
            "cybersecurity": {"ai_cybersecurity_need"},
            "medical_imaging": {"healthcare_compliance_need", "computer_vision_need"},
        }
        allowed: set[str] = set()
        for match in matches:
            allowed.update(family_gaps.get(match.family, set()))
        if needs_guardrails(text) and any(match.family == "llm_nlp" for match in matches):
            allowed.add("agent_governance_gap")

        confidence_rank = {"high": 2, "medium": 1}
        supported = [
            gap
            for gap in run.gaps
            if gap.detected
            and gap.gap_type in allowed
            and str(gap.confidence or "").casefold() in confidence_rank
        ]
        supported.sort(
            key=lambda gap: (
                confidence_rank.get(str(gap.confidence or "").casefold(), 0),
                gap.gap_type,
            ),
            reverse=True,
        )
        return [gap.gap_type for gap in supported[:3]]

'''
        if anchor not in text:
            raise RuntimeError("Could not locate _startup_row insertion point")
        text = text.replace(anchor, method + anchor)
    path.write_text(text, encoding="utf-8")


def write_tests() -> None:
    path = Path("tests/unit/test_radar_relevant_gaps.py")
    path.write_text(
        '''from types import SimpleNamespace

from src.services.product.radar_dashboard_service import RadarDashboardService
from src.services.product.workload_classifier import classify_workloads


def test_big_data_and_data_science_map_to_tabular_ml() -> None:
    matches = classify_workloads(
        "Enterprise big data company applying machine learning, analytics and data science."
    )
    assert matches
    assert matches[0].family == "tabular_ml"


def test_dashboard_filters_gaps_to_supported_workloads_and_confidence() -> None:
    startup = SimpleNamespace(
        description="Conversational AI platform using NLP, LLM workflows and AI agents.",
        product_summary="",
        evidence=[],
    )
    gaps = [
        SimpleNamespace(gap_type="agent_governance_gap", detected=True, confidence="high"),
        SimpleNamespace(gap_type="model_evaluation_gap", detected=True, confidence="medium"),
        SimpleNamespace(gap_type="observability_gap", detected=True, confidence="medium"),
        SimpleNamespace(gap_type="computer_vision_need", detected=True, confidence="high"),
        SimpleNamespace(gap_type="robotics_need", detected=True, confidence="high"),
        SimpleNamespace(gap_type="high_latency", detected=True, confidence="low"),
    ]
    run = SimpleNamespace(
        startup=startup,
        output_snapshot_json={"startup_profile": {}},
        gaps=gaps,
    )

    assert RadarDashboardService._relevant_top_gaps(run) == [
        "agent_governance_gap",
        "observability_gap",
        "model_evaluation_gap",
    ]
''',
        encoding="utf-8",
    )


def main() -> None:
    update_workload_classifier()
    update_radar_dashboard()
    write_tests()


if __name__ == "__main__":
    main()
