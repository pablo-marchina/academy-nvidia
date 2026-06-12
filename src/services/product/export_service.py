"""Export generation from persisted Action Brief records."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, cast

from src.database.models import ActionBriefRecord, ExportRecord
from src.repositories.export import ExportRepository
from src.repositories.product import ProductRepository


def _content_hash(data: dict[str, Any] | str) -> str:
    if isinstance(data, str):
        raw = data.encode("utf-8")
    else:
        raw = json.dumps(data, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class ExportService:
    def __init__(
        self,
        repository: ExportRepository,
        product_repo: ProductRepository,
        product_data_dir: str | None = None,
    ) -> None:
        self.repository = repository
        self.product_repo = product_repo
        self.product_data_dir = cast(
            str, product_data_dir or os.getenv("PRODUCT_DATA_DIR", "data/product")
        )

    def create_export(
        self,
        analysis_run_id: str,
        export_type: str,
    ) -> ExportRecord:
        run = self.product_repo.get_analysis_run(analysis_run_id)
        if run is None:
            raise LookupError(f"Analysis run not found: {analysis_run_id}")

        brief = self.product_repo.get_latest_action_brief(analysis_run_id)
        if brief is None:
            raise LookupError(f"Action brief not found for run: {analysis_run_id}")

        try:
            content: dict[str, Any] | str
            if export_type == "json":
                content = self._generate_json(brief)
            elif export_type == "markdown":
                content = self._generate_markdown(brief)
            else:
                raise ValueError(f"Unsupported export type: {export_type}")

            content_hash = _content_hash(content)
            storage_path = self._write_export(analysis_run_id, export_type, content)

            export = self.repository.create(
                analysis_run_id=analysis_run_id,
                action_brief_id=brief.id,
                export_type=export_type,
                status="completed",
                storage_path=storage_path,
                content_hash=content_hash,
            )
            return export
        except Exception as exc:
            export = self.repository.create(
                analysis_run_id=analysis_run_id,
                action_brief_id=brief.id,
                export_type=export_type,
                status="failed",
                error_message=str(exc),
            )
            raise

    def get_export(self, export_id: str) -> ExportRecord | None:
        return self.repository.get(export_id)

    def _generate_json(self, brief: ActionBriefRecord) -> dict[str, Any]:
        return brief.brief_json

    def _generate_markdown(self, brief: ActionBriefRecord) -> str:
        return brief.brief_markdown

    def _write_export(self, analysis_run_id: str, export_type: str, content: Any) -> str:
        base = Path(self.product_data_dir) / "exports" / analysis_run_id
        base.mkdir(parents=True, exist_ok=True)
        extension = "json" if export_type == "json" else "md"
        file_path = base / f"action_brief.{extension}"
        if export_type == "json":
            file_path.write_text(
                json.dumps(content, ensure_ascii=False, indent=2, default=str),
                encoding="utf-8",
            )
        else:
            file_path.write_text(str(content), encoding="utf-8")
        return str(file_path.relative_to(Path(self.product_data_dir).resolve()))
