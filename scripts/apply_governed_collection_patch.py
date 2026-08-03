#!/usr/bin/env python3
"""Apply the one-time governed collection scope and error-rate fixes."""
from pathlib import Path

scraper_path = Path("src/agents/scraper_agent.py")
scraper = scraper_path.read_text(encoding="utf-8")

marker = "\ndef collect_governed_sources(\n"
helper = '''\n\ndef _timestamp_iso(value: Any) -> str:
    """Serialize collector timestamps without assuming a datetime instance."""
    if value is None:
        return datetime.now(UTC).isoformat()
    isoformat = getattr(value, "isoformat", None)
    if callable(isoformat):
        return str(isoformat())
    return str(value)
'''
if "def _timestamp_iso" not in scraper:
    if marker not in scraper:
        raise RuntimeError("collect_governed_sources marker not found")
    scraper = scraper.replace(marker, helper + marker, 1)

old_registry = '''    # Add non-blocked configured governed sources after the adaptive plan.
    for src in governed_records:
        url = (src.base_url or "").strip()
        if not url and src.source_category == "official_website":
            url = website_url
        if not url or url in seen_urls or src.production_blockers:
            continue
        seen_urls.add(url)
        populated.append(src.model_copy(update={"base_url": url}))
'''
new_registry = '''    # The adaptive plan is authoritative. Global registry sources are a
    # fallback only when no startup-specific plan exists; otherwise unrelated
    # ecosystem directories create false errors and contaminate evidence.
    if not search_plan:
        for src in governed_records:
            url = (src.base_url or "").strip()
            if not url and src.source_category == "official_website":
                url = website_url
            if not url or url in seen_urls or src.production_blockers:
                continue
            seen_urls.add(url)
            populated.append(src.model_copy(update={"base_url": url}))
'''
if new_registry not in scraper:
    if old_registry not in scraper:
        raise RuntimeError("governed registry append block not found")
    scraper = scraper.replace(old_registry, new_registry, 1)

scraper = scraper.replace('"fetched_at": sfr.fetched_at.isoformat(),', '"fetched_at": _timestamp_iso(sfr.fetched_at),')
scraper_path.write_text(scraper, encoding="utf-8")

node_path = Path("src/orchestration/node_impl.py")
node = node_path.read_text(encoding="utf-8")
old_rate = '''    attempted_count = max(1, len(state.search_plan))
    error_rate = len(errors) / attempted_count
'''
new_rate = '''    # Measure the effective acquisition batch, including valid persisted
    # evidence merged above. Counting only planned URLs makes one robots block
    # look like a 100% failure even when several real sources are available.
    attempted_count = max(1, len(evidence_items) + len(errors))
    error_rate = len(errors) / attempted_count
'''
if new_rate not in node:
    if old_rate not in node:
        raise RuntimeError("collection error-rate block not found")
    node = node.replace(old_rate, new_rate, 1)
node_path.write_text(node, encoding="utf-8")

Path(__file__).unlink()
print("governed collection scope, timestamp, and error-rate fixes applied")
