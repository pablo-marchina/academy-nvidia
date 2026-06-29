from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from hashlib import sha256


@dataclass(frozen=True)
class EvidenceSpan:
    text: str
    source_url: str
    confidence: float = 0.5


@dataclass(frozen=True)
class SourceResult:
    target: str
    status: str
    raw_text: str
    evidence_spans: list[EvidenceSpan] = field(default_factory=list)
    content_hash: str = ""
    collected_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    error: str | None = None


class SourceAdapter:
    source_type = "generic"

    async def collect(self, target: str) -> SourceResult:
        raise NotImplementedError


def build_source_result(target: str, raw_text: str, *, status: str = "collected") -> SourceResult:
    digest = sha256(raw_text.encode("utf-8")).hexdigest()
    spans = [EvidenceSpan(text=raw_text[:500], source_url=target, confidence=0.5)] if raw_text else []
    return SourceResult(target=target, status=status, raw_text=raw_text, evidence_spans=spans, content_hash=digest)
