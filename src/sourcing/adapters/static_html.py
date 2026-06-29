from __future__ import annotations

import urllib.request

from src.sourcing.adapters.base import SourceAdapter, SourceResult, build_source_result


class StaticHtmlAdapter(SourceAdapter):
    source_type = "static_html"

    async def collect(self, target: str) -> SourceResult:
        try:
            with urllib.request.urlopen(target, timeout=20) as response:
                text = response.read(1_000_000).decode("utf-8", errors="replace")
        except Exception as exc:
            return SourceResult(target=target, status="failed", raw_text="", error=str(exc))
        return build_source_result(target, text)
