from __future__ import annotations

from src.sourcing.adapters.static_html import StaticHtmlAdapter


class FounderProfileAdapter(StaticHtmlAdapter):
    source_type = "founder_profile"
