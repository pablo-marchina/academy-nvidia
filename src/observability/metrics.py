from __future__ import annotations

from pydantic import BaseModel, Field


class StageLatencyMetric(BaseModel):
    stage: str
    latency_ms: float = Field(ge=0.0)


class RunMetrics(BaseModel):
    latency_by_stage: list[StageLatencyMetric] = Field(default_factory=list)
    error_count: int = Field(default=0, ge=0)
    fallback_count: int = Field(default=0, ge=0)

    @property
    def total_latency_ms(self) -> float:
        return round(sum(metric.latency_ms for metric in self.latency_by_stage), 4)
