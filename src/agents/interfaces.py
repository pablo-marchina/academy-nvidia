"""Protocols for injectable graph node dependencies.

Default implementations wrap the real agent services so that callers
can inject mocks/stubs in tests without ``@patch``.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ScoreService(Protocol):
    """Interface for the ``score_startup`` node.

    Default implementation: ``src.agents.classifier_agent.score_startup``.
    """

    def __call__(
        self,
        profile: dict[str, Any] | None,
        validated_evidence: list[dict[str, Any]],
        run_id: str,
    ) -> tuple[
        dict[str, Any],
        dict[str, Any],
        dict[str, Any],
        dict[str, Any],
        dict[str, Any],
        list[str],
    ]: ...


@runtime_checkable
class RagService(Protocol):
    """Interface for the ``retrieve_nvidia_context`` node.

    Default implementation: ``src.agents.nvidia_rag_agent.retrieve_nvidia_context``.
    Accepts gap diagnosis summary with calibrated gap results, startup profile,
    accepted evidence, and scores. Returns a structured dict with queries,
    contexts, metrics, and status for direct state merge.
    """

    def __call__(
        self,
        run_id: str,
        gap_diagnosis_summary: dict[str, Any] | None,
        startup_profile: dict[str, Any] | None,
        accepted_evidence_items: list[dict[str, Any]],
        claims: list[dict[str, Any]],
        ai_native_score: float | None,
        nvidia_fit_score: float | None,
    ) -> dict[str, Any]: ...


@runtime_checkable
class DiagnoseGapsService(Protocol):
    """Interface for the ``diagnose_gaps`` node.

    Default implementation: ``src.agents.recommendation_agent.diagnose_gaps``.
    """

    def __call__(
        self,
        startup_name: str,
        profile_raw: dict[str, Any] | None,
        validated_evidence_dicts: list[dict[str, Any]],
        classification_raw: dict[str, Any] | None,
        defensibility_raw: dict[str, Any] | None,
        inception_fit_raw: dict[str, Any] | None,
        production_readiness_raw: dict[str, Any] | None,
    ) -> tuple[list[str], dict[str, Any], list[str]]: ...


@runtime_checkable
class RankRecommendationsService(Protocol):
    """Interface for the ``rank_recommendations`` node.

    Default implementation: ``src.agents.recommendation_agent.rank_recommendations``.
    """

    def __call__(
        self,
        startup_name: str,
        profile_raw: dict[str, Any] | None,
        classification_raw: dict[str, Any] | None,
        validated_evidence_dicts: list[dict[str, Any]],
        defensibility_raw: dict[str, Any] | None,
        inception_fit_raw: dict[str, Any] | None,
        production_readiness_raw: dict[str, Any] | None,
        scores_raw: dict[str, Any] | None,
        gap_diagnosis_raw: dict[str, Any] | None,
        rag_contexts: list[str],
    ) -> tuple[list[str], list[str]]: ...


@runtime_checkable
class PersistWorkflowResultService(Protocol):
    """Interface for persisting workflow results to AnalysisRun.

    Default implementation: ``ProductRepository.update_analysis_run_status``
    (via an adapter that handles the session commit).
    """

    def __call__(
        self,
        analysis_run_id: str,
        *,
        status: str,
        output_snapshot: dict[str, Any],
        error_message: str | None = None,
    ) -> Any: ...


@runtime_checkable
class GenerateBriefService(Protocol):
    """Interface for the ``generate_brief`` node.

    Default implementation: ``src.agents.briefing_agent.generate_brief``.
    """

    def __call__(
        self,
        startup_name: str,
        profile: dict[str, Any] | None,
        classification_raw: dict[str, Any] | None,
        scores: dict[str, Any] | None,
        gaps: list[str],
        gap_diagnosis_raw: dict[str, Any] | None,
        recommendations: list[str],
        rag_contexts: list[str],
    ) -> tuple[str, list[str]]: ...
