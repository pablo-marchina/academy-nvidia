from __future__ import annotations

from src.sourcing.adapters.static_html import StaticHtmlAdapter


class DynamicPageAdapter(StaticHtmlAdapter):
    source_type = "dynamic_page"
