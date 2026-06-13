"""Transactional product models for the NVIDIA Startup AI Radar."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utc_now() -> datetime:
    return datetime.now(UTC)


def new_id() -> str:
    return str(uuid4())


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class Startup(TimestampMixin, Base):
    __tablename__ = "startups"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    normalized_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    website: Mapped[str] = mapped_column(String(2048), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False, default="Brazil")
    sector: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    product_summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active", index=True)
    tags_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    evidence: Mapped[list[StartupEvidence]] = relationship(
        back_populates="startup", cascade="all, delete-orphan"
    )
    analysis_runs: Mapped[list[AnalysisRun]] = relationship(
        back_populates="startup", cascade="all, delete-orphan"
    )


class StartupEvidence(TimestampMixin, Base):
    __tablename__ = "startup_evidence"
    __table_args__ = (Index("ix_startup_evidence_startup_collected", "startup_id", "collected_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    startup_id: Mapped[str] = mapped_column(
        ForeignKey("startups.id", ondelete="CASCADE"), nullable=False, index=True
    )
    claim: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[str] = mapped_column(String(2048), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    quote_or_evidence: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[str] = mapped_column(String(20), nullable=False)
    evidence_kind: Mapped[str] = mapped_column(
        String(50), nullable=False, default="unverified", index=True
    )
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    startup: Mapped[Startup] = relationship(back_populates="evidence")


class AnalysisRun(TimestampMixin, Base):
    __tablename__ = "analysis_runs"
    __table_args__ = (Index("ix_analysis_runs_startup_created", "startup_id", "created_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    startup_id: Mapped[str] = mapped_column(
        ForeignKey("startups.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="queued", index=True)
    error_message: Mapped[str | None] = mapped_column(Text)
    degraded_reason: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    input_snapshot_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    output_snapshot_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    pipeline_version: Mapped[str] = mapped_column(String(100), nullable=False, default="current")
    corpus_version: Mapped[str | None] = mapped_column(String(100))
    config_snapshot_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    startup: Mapped[Startup] = relationship(back_populates="analysis_runs")
    scores: Mapped[list[ScoreRecord]] = relationship(
        back_populates="analysis_run", cascade="all, delete-orphan"
    )
    gaps: Mapped[list[GapDiagnosisRecord]] = relationship(
        back_populates="analysis_run", cascade="all, delete-orphan"
    )
    mappings: Mapped[list[NvidiaMappingRecord]] = relationship(
        back_populates="analysis_run", cascade="all, delete-orphan"
    )
    briefs: Mapped[list[ActionBriefRecord]] = relationship(
        back_populates="analysis_run", cascade="all, delete-orphan"
    )
    readiness_checks: Mapped[list[ProductReadinessCheck]] = relationship(
        back_populates="analysis_run", cascade="all, delete-orphan"
    )
    reviews: Mapped[list[ReviewDecision]] = relationship(
        back_populates="analysis_run", cascade="all, delete-orphan"
    )
    exports: Mapped[list[ExportRecord]] = relationship(
        back_populates="analysis_run", cascade="all, delete-orphan"
    )
    activation_recommendations: Mapped[list[ActivationRecommendationRecord]] = relationship(
        back_populates="analysis_run", cascade="all, delete-orphan"
    )
    dossiers: Mapped[list[ActivationDossierRecord]] = relationship(
        back_populates="analysis_run", cascade="all, delete-orphan"
    )
    quality_runs: Mapped[list[ProductQualityRun]] = relationship(
        back_populates="analysis_run", cascade="all, delete-orphan"
    )


class ScoreRecord(TimestampMixin, Base):
    __tablename__ = "score_records"
    __table_args__ = (UniqueConstraint("analysis_run_id", "score_type", name="uq_run_score_type"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    analysis_run_id: Mapped[str] = mapped_column(
        ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    score_type: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[str] = mapped_column(String(20), nullable=False)
    components_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    missing_evidence_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    analysis_run: Mapped[AnalysisRun] = relationship(back_populates="scores")


class GapDiagnosisRecord(TimestampMixin, Base):
    __tablename__ = "gap_diagnosis_records"
    __table_args__ = (UniqueConstraint("analysis_run_id", "gap_type", name="uq_run_gap_type"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    analysis_run_id: Mapped[str] = mapped_column(
        ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    gap_type: Mapped[str] = mapped_column(String(100), nullable=False)
    detected: Mapped[bool] = mapped_column(Boolean, nullable=False)
    confidence: Mapped[str] = mapped_column(String(20), nullable=False)
    evidence_tag: Mapped[str] = mapped_column(String(50), nullable=False)
    reasoning: Mapped[str] = mapped_column(Text, nullable=False, default="")
    evidence_refs_json: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, nullable=False, default=list
    )
    missing_evidence_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    analysis_run: Mapped[AnalysisRun] = relationship(back_populates="gaps")
    mappings: Mapped[list[NvidiaMappingRecord]] = relationship(back_populates="gap_record")


class NvidiaMappingRecord(TimestampMixin, Base):
    __tablename__ = "nvidia_mapping_records"
    __table_args__ = (
        Index(
            "ix_nvidia_mapping_run_gap_technology",
            "analysis_run_id",
            "addresses_gap",
            "technology_name",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    analysis_run_id: Mapped[str] = mapped_column(
        ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    gap_record_id: Mapped[str | None] = mapped_column(
        ForeignKey("gap_diagnosis_records.id", ondelete="SET NULL"), index=True
    )
    technology_name: Mapped[str] = mapped_column(String(255), nullable=False)
    addresses_gap: Mapped[str] = mapped_column(String(100), nullable=False)
    justification: Mapped[str] = mapped_column(Text, nullable=False, default="")
    recommendation_action: Mapped[str | None] = mapped_column(String(50))
    priority: Mapped[str | None] = mapped_column(String(20))
    details_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    analysis_run: Mapped[AnalysisRun] = relationship(back_populates="mappings")
    gap_record: Mapped[GapDiagnosisRecord | None] = relationship(back_populates="mappings")


class ActionBriefRecord(TimestampMixin, Base):
    __tablename__ = "action_brief_records"
    __table_args__ = (
        UniqueConstraint("analysis_run_id", "version", name="uq_run_brief_version"),
        Index("ix_action_brief_run_latest", "analysis_run_id", "is_latest"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    analysis_run_id: Mapped[str] = mapped_column(
        ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    schema_version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0")
    brief_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    brief_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    is_latest: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    analysis_run: Mapped[AnalysisRun] = relationship(back_populates="briefs")


class ProductReadinessCheck(TimestampMixin, Base):
    __tablename__ = "product_readiness_checks"
    __table_args__ = (
        Index("ix_readiness_run_code", "analysis_run_id", "code"),
        Index("ix_readiness_status_observed", "status", "observed_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    analysis_run_id: Mapped[str | None] = mapped_column(
        ForeignKey("analysis_runs.id", ondelete="CASCADE"), index=True
    )
    code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    user_message: Mapped[str] = mapped_column(Text, nullable=False)
    internal_detail: Mapped[str] = mapped_column(Text, nullable=False, default="")
    recommended_action: Mapped[str] = mapped_column(Text, nullable=False, default="")
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )

    analysis_run: Mapped[AnalysisRun | None] = relationship(back_populates="readiness_checks")


class ReviewDecision(TimestampMixin, Base):
    __tablename__ = "review_decisions"
    __table_args__ = (Index("ix_review_run_created", "analysis_run_id", "created_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    analysis_run_id: Mapped[str] = mapped_column(
        ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    decision: Mapped[str] = mapped_column(String(50), nullable=False)
    reviewer: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    analysis_run: Mapped[AnalysisRun] = relationship(back_populates="reviews")


class ExportRecord(TimestampMixin, Base):
    __tablename__ = "export_records"
    __table_args__ = (Index("ix_export_run_type", "analysis_run_id", "export_type"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    analysis_run_id: Mapped[str] = mapped_column(
        ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    action_brief_id: Mapped[str | None] = mapped_column(
        ForeignKey("action_brief_records.id", ondelete="SET NULL")
    )
    export_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    storage_path: Mapped[str] = mapped_column(String(2048), nullable=False, default="")
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    error_message: Mapped[str | None] = mapped_column(Text)

    analysis_run: Mapped[AnalysisRun] = relationship(back_populates="exports")
    action_brief: Mapped[ActionBriefRecord | None] = relationship()


class ClaimRecord(TimestampMixin, Base):
    __tablename__ = "claim_records"
    __table_args__ = (
        Index("ix_claim_startup_type", "startup_id", "claim_type"),
        Index("ix_claim_run_review", "analysis_run_id", "review_status"),
        Index("ix_claim_support", "support_level"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    startup_id: Mapped[str] = mapped_column(
        ForeignKey("startups.id", ondelete="CASCADE"), nullable=False, index=True
    )
    analysis_run_id: Mapped[str] = mapped_column(
        ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    claim_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    support_level: Mapped[str] = mapped_column(String(20), nullable=False, default="unsupported")
    confidence: Mapped[str] = mapped_column(String(20), nullable=False, default="low")
    evidence_refs_json: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, nullable=False, default=list
    )
    used_in_score: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    used_in_gap: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    used_in_mapping: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    used_in_brief: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    review_status: Mapped[str] = mapped_column(String(20), nullable=False, default="unreviewed")
    reviewer_notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    startup: Mapped[Startup] = relationship()
    analysis_run: Mapped[AnalysisRun] = relationship()


class ActivationRecommendationRecord(TimestampMixin, Base):
    __tablename__ = "activation_recommendations"
    __table_args__ = (
        Index("ix_activation_run_id", "analysis_run_id"),
        Index("ix_activation_playbook_id", "playbook_id"),
        Index("ix_activation_recommended_motion", "recommended_motion"),
        Index("ix_activation_priority", "priority"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    analysis_run_id: Mapped[str] = mapped_column(
        ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    playbook_id: Mapped[str] = mapped_column(String(100), nullable=False)
    playbook_name: Mapped[str] = mapped_column(String(255), nullable=False)
    matched_gap_types_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    matched_claim_ids_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    nvidia_technologies_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    technical_experiment: Mapped[str] = mapped_column(Text, nullable=False, default="")
    success_metrics_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    recommended_motion: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    confidence: Mapped[str] = mapped_column(String(20), nullable=False, default="low")
    reasoning: Mapped[str] = mapped_column(Text, nullable=False, default="")
    evidence_refs_json: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, nullable=False, default=list
    )
    risks_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    next_step: Mapped[str] = mapped_column(Text, nullable=False, default="")

    analysis_run: Mapped[AnalysisRun] = relationship(back_populates="activation_recommendations")


class ActivationDossierRecord(TimestampMixin, Base):
    __tablename__ = "activation_dossier_records"
    __table_args__ = (
        UniqueConstraint("analysis_run_id", "version", name="uq_run_dossier_version"),
        Index("ix_dossier_run_latest", "analysis_run_id", "is_latest"),
        Index("ix_dossier_recommended_motion", "recommended_motion"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    analysis_run_id: Mapped[str] = mapped_column(
        ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    schema_version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0")
    dossier_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    dossier_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    is_latest: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    evidence_coverage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    unsupported_claim_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    top_activation_playbook_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    recommended_motion: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    review_status: Mapped[str | None] = mapped_column(String(50), nullable=True)

    analysis_run: Mapped[AnalysisRun] = relationship(back_populates="dossiers")


class ProductQualityRun(TimestampMixin, Base):
    __tablename__ = "product_quality_runs"
    __table_args__ = (
        Index("ix_quality_run_analysis", "analysis_run_id"),
        Index("ix_quality_run_status", "status"),
        Index("ix_quality_run_created", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    analysis_run_id: Mapped[str] = mapped_column(
        ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    dossier_id: Mapped[str | None] = mapped_column(
        ForeignKey("activation_dossier_records.id", ondelete="SET NULL"), nullable=True
    )
    action_brief_id: Mapped[str | None] = mapped_column(
        ForeignKey("action_brief_records.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="running")
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    evaluator_version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0")
    metrics_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    summary_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    degraded_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    analysis_run: Mapped[AnalysisRun] = relationship(back_populates="quality_runs")
    dossier: Mapped[ActivationDossierRecord | None] = relationship()
    action_brief: Mapped[ActionBriefRecord | None] = relationship()
    metrics: Mapped[list[ProductQualityMetric]] = relationship(
        back_populates="quality_run", cascade="all, delete-orphan"
    )


class ProductQualityMetric(TimestampMixin, Base):
    __tablename__ = "product_quality_metrics"
    __table_args__ = (
        Index("ix_quality_metric_run", "quality_run_id"),
        Index("ix_quality_metric_name", "metric_name"),
        Index("ix_quality_metric_passed", "passed"),
        Index("ix_quality_metric_severity", "severity"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    quality_run_id: Mapped[str] = mapped_column(
        ForeignKey("product_quality_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="warn")
    details_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    quality_run: Mapped[ProductQualityRun] = relationship(back_populates="metrics")
