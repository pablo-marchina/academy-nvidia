from __future__ import annotations

from pathlib import Path


path = Path("src/agents/extractor_agent.py")
content = path.read_text(encoding="utf-8")

if '"claim": canonical_claim' in content:
    print("Evidence contract already repaired.")
    raise SystemExit(0)

old_import = "from src.extraction.schemas import Evidence, SourceType, StartupProfile\n"
new_import = "from src.extraction.schemas import ConfidenceLevel, Evidence, SourceType, StartupProfile\n"
if old_import not in content:
    raise SystemExit("Could not find extraction schema import")
content = content.replace(old_import, new_import, 1)

old = '''    factuality: str = "observed" if text else "unknown"

    item: dict[str, Any] = {
        "evidence_id": str(uuid.uuid4()),
'''
new = '''    factuality: str = "observed" if text else "unknown"
    primary_source = profile.sources[0] if profile.sources else None
    canonical_claim = (
        primary_source.claim
        if primary_source is not None and primary_source.claim
        else f"{profile.startup_name} shows evidence of {', '.join(profile.ai_signals[:3]) or 'AI activity'}."
    )
    canonical_quote = (
        primary_source.quote_or_evidence
        if primary_source is not None and primary_source.quote_or_evidence
        else snippet
    )
    canonical_confidence = (
        primary_source.confidence.value
        if primary_source is not None and hasattr(primary_source.confidence, "value")
        else ConfidenceLevel.from_score(conf).value
    )
    canonical_collected_at = (
        primary_source.collected_at.isoformat()
        if primary_source is not None
        else extracted_at
    )

    item: dict[str, Any] = {
        "evidence_id": str(uuid.uuid4()),
        "claim": canonical_claim,
        "quote_or_evidence": canonical_quote,
        "confidence": canonical_confidence,
'''
if old not in content:
    raise SystemExit("Could not find extraction evidence anchor")
content = content.replace(old, new, 1)
content = content.replace(
    '        "collected_at": extracted_at,\n',
    '        "collected_at": canonical_collected_at,\n',
    1,
)
path.write_text(content, encoding="utf-8")
print("Repaired extraction-to-validation evidence contract.")
