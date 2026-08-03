#!/usr/bin/env python3
"""Apply evidence-schema compatibility and non-fatal collection warnings."""
from pathlib import Path

extractor_path = Path("src/agents/extractor_agent.py")
extractor = extractor_path.read_text(encoding="utf-8")
old_collected = '    collected_at_raw: str = source_candidate.get("collected_at", "")\n'
new_collected = '    collected_at_raw: str = source_candidate.get("collected_at") or source_candidate.get("fetched_at") or ""\n'
if new_collected not in extractor:
    if old_collected not in extractor:
        raise RuntimeError("extractor collected_at pattern not found")
    extractor = extractor.replace(old_collected, new_collected, 1)

old_score = '''    st_value: str = source_type.value if isinstance(source_type, SourceType) else str(source_type)
    score = source_quality_score(source_type)

    factuality: str = "observed" if text else "unknown"

    item: dict[str, Any] = {
'''
new_score = '''    st_value: str = source_type.value if isinstance(source_type, SourceType) else str(source_type)
    score = source_quality_score(source_type)
    from src.extraction.schemas import ConfidenceLevel

    confidence_level = ConfidenceLevel.from_score(conf).value
    summary = profile.product_summary if profile.product_summary != "Not verified" else profile.description
    claim_text = f"{profile.startup_name}: {summary or snippet}"[:1000]
    quote = text[:1200] if text else snippet

    factuality: str = "observed" if text else "unknown"

    item: dict[str, Any] = {
'''
if new_score not in extractor:
    if old_score not in extractor:
        raise RuntimeError("extractor score block not found")
    extractor = extractor.replace(old_score, new_score, 1)

old_item = '''        "evidence_id": str(uuid.uuid4()),
        "source_id": source_id,
        "source_url": source_url,
        "url": source_url,
        "source_type": st_value,
        "title": profile.startup_name,
'''
new_item = '''        "evidence_id": str(uuid.uuid4()),
        "claim": claim_text,
        "source_id": source_id,
        "source_url": source_url,
        "url": source_url,
        "source_type": st_value,
        "quote_or_evidence": quote,
        "confidence": confidence_level,
        "title": profile.startup_name,
'''
if new_item not in extractor:
    if old_item not in extractor:
        raise RuntimeError("extractor evidence item block not found")
    extractor = extractor.replace(old_item, new_item, 1)
extractor_path.write_text(extractor, encoding="utf-8")

node_path = Path("src/orchestration/node_impl.py")
node = node_path.read_text(encoding="utf-8")
old_branch = '''    if errors or failures:
        msg_parts = []
        if errors:
            msg_parts.append(f"Source collection had errors: {'; '.join(errors[:5])}")
        if failures:
            msg_parts.append(f"Source coverage gate failed: {', '.join(failures)}")
        msg = " | ".join(msg_parts)
        return NodeResult(
            status=NodeStatus.FAILED if _is_product_mode() and failures else NodeStatus.DEGRADED,
            error_message=msg if _is_product_mode() and failures else None,
            degraded_reason=msg,
            state_updates=updates,
        )
    return NodeResult(
'''
new_branch = '''    if failures:
        msg_parts = []
        if errors:
            msg_parts.append(f"Source collection had errors: {'; '.join(errors[:5])}")
        msg_parts.append(f"Source coverage gate failed: {', '.join(failures)}")
        msg = " | ".join(msg_parts)
        return NodeResult(
            status=NodeStatus.FAILED if _is_product_mode() else NodeStatus.DEGRADED,
            error_message=msg if _is_product_mode() else None,
            degraded_reason=msg,
            state_updates=updates,
        )
    if errors:
        collection_metrics["warnings"] = errors[:10]
        updates["node_outputs"] = {**state.node_outputs, "collection_metrics": collection_metrics}
    return NodeResult(
'''
if new_branch not in node:
    if old_branch not in node:
        raise RuntimeError("collection result branch not found")
    node = node.replace(old_branch, new_branch, 1)
node_path.write_text(node, encoding="utf-8")

validation_path = Path("scripts/validate_live_outputs.py")
validation = validation_path.read_text(encoding="utf-8")
old_enter = '''            {"url": "https://www.gtlaw.com/en/news/2026/05/press-releases/greenberg-traurig-represents-enter-in-%24100m-series-b--creating-latin-americas-first-ai-unicorn", "type": "news", "anchors": ["Enter", "artificial intelligence", "legal"]},
'''
new_enter = '''            {"url": "https://www.gtlaw.com/en/news/2026/05/press-releases/greenberg-traurig-represents-enter-in-%24100m-series-b--creating-latin-americas-first-ai-unicorn", "type": "news", "anchors": ["Enter", "artificial intelligence", "legal"]},
            {"url": "https://www.infomoney.com.br/mercados/startups-quem-e-a-enter-unicornio-brasileiro-de-ia-do-setor-juridico/", "type": "news", "anchors": ["Enter", "inteligência artificial", "jurídico"]},
'''
if new_enter not in validation:
    if old_enter not in validation:
        raise RuntimeError("Enter source block not found")
    validation = validation.replace(old_enter, new_enter, 1)
validation_path.write_text(validation, encoding="utf-8")

Path(__file__).unlink()
print("evidence schema, collection warning, and Enter source fixes applied")
