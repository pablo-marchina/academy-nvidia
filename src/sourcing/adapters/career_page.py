from __future__ import annotations

from src.sourcing.adapters.static_html import StaticHtmlAdapter


class CareerPageAdapter(StaticHtmlAdapter):
    source_type = "career_page"
