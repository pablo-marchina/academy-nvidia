"""Typed state definitions for the future LangGraph workflow."""

from __future__ import annotations

from typing import TypedDict

from src.extraction.schemas import AINativeLevel, Evidence, NvidiaRecommendation, StartupProfile


class StartupRadarState(TypedDict, total=False):
    user_query: str
    search_plan: list[str]
    collected_sources: list[str]
    extracted_profiles: list[StartupProfile]
    validated_evidence: list[Evidence]
    ai_native_classification: AINativeLevel
    maturity_diagnosis: str
    rag_context: list[str]
    recommendations: list[NvidiaRecommendation]
    briefing: str
    errors: list[str]
