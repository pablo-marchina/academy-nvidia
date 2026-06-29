from __future__ import annotations

from src.sourcing.adapters.static_html import StaticHtmlAdapter


class DirectoryAdapter(StaticHtmlAdapter):
    source_type = "directory"
