from __future__ import annotations

from src.sourcing.adapters.static_html import StaticHtmlAdapter


class NewsAdapter(StaticHtmlAdapter):
    source_type = "news"
