"""ReviewDecision repository."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.models import ReviewDecision


class ReviewDecisionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        *,
        analysis_run_id: str,
        decision: str,
        reviewer: str,
        notes: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ReviewDecision:
        record = ReviewDecision(
            analysis_run_id=analysis_run_id,
            decision=decision,
            reviewer=reviewer,
            notes=notes,
            metadata_json=metadata or {},
        )
        self.session.add(record)
        self.session.flush()
        return record

    def list_for_run(self, analysis_run_id: str) -> list[ReviewDecision]:
        statement = (
            select(ReviewDecision)
            .where(ReviewDecision.analysis_run_id == analysis_run_id)
            .order_by(ReviewDecision.created_at.desc())
        )
        return list(self.session.scalars(statement))

    def get_latest_for_run(self, analysis_run_id: str) -> ReviewDecision | None:
        statement = (
            select(ReviewDecision)
            .where(ReviewDecision.analysis_run_id == analysis_run_id)
            .order_by(ReviewDecision.created_at.desc())
            .limit(1)
        )
        return self.session.scalar(statement)
