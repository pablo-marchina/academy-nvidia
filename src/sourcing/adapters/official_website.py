from __future__ import annotations

from src.sourcing.adapters.static_html import StaticHtmlAdapter


class OfficialWebsiteAdapter(StaticHtmlAdapter):
    source_type = "official_website"
