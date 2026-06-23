from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter
from typing import Any

from src.observability.metrics import RunMetrics, StageLatencyMetric
from src.observability.run_events import RunTrace


class StructuredTracer:
    def __init__(self, run_id: str) -> None:
        self.trace = RunTrace(run_id=run_id)
        self.metrics = RunMetrics()

    def event(self, event_type: str, *, stage: str, payload: dict[str, Any] | None = None) -> None:
        self.trace.add(event_type, stage=stage, payload=payload)

    def timed_stage(self, stage: str) -> "_TimedStage":
        return _TimedStage(self, stage)

    def write_json(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "trace": self.trace.model_dump(mode="json"),
            "metrics": self.metrics.model_dump(mode="json"),
            "total_latency_ms": self.metrics.total_latency_ms,
        }
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class _TimedStage:
    def __init__(self, tracer: StructuredTracer, stage: str) -> None:
        self.tracer = tracer
        self.stage = stage
        self.started = 0.0

    def __enter__(self) -> "_TimedStage":
        self.started = perf_counter()
        self.tracer.event("stage_started", stage=self.stage)
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        latency_ms = (perf_counter() - self.started) * 1000
        self.tracer.metrics.latency_by_stage.append(StageLatencyMetric(stage=self.stage, latency_ms=latency_ms))
        event_type = "stage_failed" if exc is not None else "stage_completed"
        self.tracer.event(event_type, stage=self.stage, payload={"latency_ms": round(latency_ms, 4)})
