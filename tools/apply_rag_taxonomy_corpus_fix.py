from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import yaml


HYBRID_PATH = Path("src/rag/hybrid_retrieval.py")
ALLOWLIST_PATH = Path("data/nvidia_corpus/source_allowlist.yaml")
SOURCES_PATH = Path("data/nvidia_corpus/sources.yaml")
TENSORRT_HASH = "29d617b531042b40d1d9bc1802c4bd5e"
TENSORRT_URL = "https://docs.nvidia.com/deeplearning/tensorrt/latest/"


def patch_hybrid_retrieval() -> None:
    content = HYBRID_PATH.read_text(encoding="utf-8")
    if "def _gap_type_aliases" not in content:
        import_anchor = "from src.rag.vector_store import VectorStore\n"
        import_replacement = (
            "from src.rag.vector_store import VectorStore\n"
            "from src.diagnosis.schemas import GAP_TECH_MAP, GapType\n"
        )
        if import_anchor not in content:
            raise SystemExit("hybrid retrieval import anchor not found")
        content = content.replace(import_anchor, import_replacement, 1)

        helper_anchor = "\n\ndef _apply_filters(\n"
        helper = '''\n\ndef _gap_type_aliases(gap_type: str) -> set[str]:
    """Return diagnosis and technical taxonomy aliases for corpus filtering."""
    aliases = {gap_type}
    try:
        diagnosis_gap = GapType(gap_type)
    except ValueError:
        return aliases
    aliases.update(technical_gap.value for technical_gap in GAP_TECH_MAP.get(diagnosis_gap, []))
    return aliases
'''
        if helper_anchor not in content:
            raise SystemExit("hybrid retrieval filter anchor not found")
        content = content.replace(helper_anchor, helper + helper_anchor, 1)

        semantic_old = '''            gap_type=gap_type,
            source_id=source_id,
'''
        semantic_new = '''            # The corpus stores both diagnosis-level and technical gap taxonomies.
            # Apply the alias-aware filter after dense/lexical fusion rather than
            # forcing an exact Qdrant payload match here.
            gap_type=None,
            source_id=source_id,
'''
        if semantic_old not in content:
            raise SystemExit("semantic retrieval gap filter anchor not found")
        content = content.replace(semantic_old, semantic_new, 1)

        filter_old = '''    if gap_type:
        result = [c for c in result if gap_type in c.gap_types]
'''
        filter_new = '''    if gap_type:
        aliases = _gap_type_aliases(gap_type)
        result = [c for c in result if aliases.intersection(c.gap_types)]
'''
        if filter_old not in content:
            raise SystemExit("post-filter gap anchor not found")
        content = content.replace(filter_old, filter_new, 1)
        HYBRID_PATH.write_text(content, encoding="utf-8")


def patch_allowlist() -> None:
    content = ALLOWLIST_PATH.read_text(encoding="utf-8")
    if "  - source_id: tensorrt\n" in content:
        return
    anchor = "  - source_id: triton\n"
    block = '''  - source_id: tensorrt
    title: "NVIDIA TensorRT"
    url: "https://docs.nvidia.com/deeplearning/tensorrt/latest/"
    product: "TensorRT"
    gap_types: ["computer_vision_need", "high_inference_cost", "high_latency"]
    version: "1.0"
    document_type: "nvidia_corpus"
    allowed: true
    update_frequency: "weekly"
    freshness_policy: "weekly"
    stale_after_days: 7
    expected_format: "markdown"
    license_note: "NVIDIA Documentation License — read-only, no redistribution"
    notes: "General TensorRT inference optimization documentation, including computer-vision deployment."

'''
    if anchor not in content:
        raise SystemExit("allowlist triton anchor not found")
    ALLOWLIST_PATH.write_text(content.replace(anchor, block + anchor, 1), encoding="utf-8")


def patch_sources() -> None:
    document = yaml.safe_load(SOURCES_PATH.read_text(encoding="utf-8")) or {}
    sources = document.setdefault("sources", {})
    if "tensorrt" in sources:
        return
    now = datetime.now(UTC).isoformat()
    entry = {
        "title": "NVIDIA TensorRT",
        "url": TENSORRT_URL,
        "product": "TensorRT",
        "gap_types": ["computer_vision_need", "high_inference_cost", "high_latency"],
        "version": "1.0",
        "document_type": "nvidia_corpus",
        "content_hash": TENSORRT_HASH,
        "previous_content_hash": None,
        "collected_at": now,
        "last_checked_at": now,
        "valid_from": now,
        "valid_until": None,
        "freshness_policy": "weekly",
        "stale_after_days": 7,
        "is_active": True,
        "deprecated_at": None,
        "superseded_by": None,
        "deprecation_reason": None,
        "versions": [
            {
                "version": "1.0",
                "content_hash": TENSORRT_HASH,
                "previous_content_hash": None,
                "collected_at": now,
                "last_checked_at": now,
                "valid_from": now,
                "valid_until": None,
                "freshness_policy": "weekly",
                "stale_after_days": 7,
                "is_active": True,
                "deprecated_at": None,
                "superseded_by": None,
                "deprecation_reason": None,
            }
        ],
    }
    rebuilt: dict[str, object] = {}
    inserted = False
    for key, value in sources.items():
        rebuilt[key] = value
        if key == "tensorrt_llm":
            rebuilt["tensorrt"] = entry
            inserted = True
    if not inserted:
        rebuilt["tensorrt"] = entry
    document["sources"] = rebuilt
    SOURCES_PATH.write_text(
        yaml.safe_dump(document, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def main() -> None:
    patch_hybrid_retrieval()
    patch_allowlist()
    patch_sources()
    print("Applied alias-aware hybrid retrieval and governed TensorRT corpus source.")


if __name__ == "__main__":
    main()
