#!/usr/bin/env python3
"""Apply a one-time fix so readiness audits only active governed sources."""
from pathlib import Path

path = Path("src/services/product/health_executor.py")
text = path.read_text(encoding="utf-8")
old = '''    manifest_hashes = payload.get("source_hashes") or {}
    if not isinstance(manifest_hashes, dict) or not manifest_hashes:
        return False, "Corpus ingestion manifest has no source hashes"
    current_files = sorted(path for path in corpus_dir.glob("*.md") if path.name != "README.md")
    current_ids = {path.stem for path in current_files}
    if set(manifest_hashes) != current_ids:
        missing = sorted(current_ids - set(manifest_hashes))
        extra = sorted(set(manifest_hashes) - current_ids)
        return False, f"Corpus ingestion manifest source set mismatch (missing={missing}, extra={extra})"
    mismatched: list[str] = []
    for path in current_files:
        current_hash = hashlib.md5(path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
        if str(manifest_hashes.get(path.stem)) != current_hash:
            mismatched.append(path.stem)
    if mismatched:
        return False, f"Corpus changed after ingestion for source(s): {', '.join(sorted(mismatched))}"

    documents_valid = int(payload.get("documents_valid") or 0)
    chunks_created = int(payload.get("chunks_created") or 0)
    if documents_valid != len(current_files) or chunks_created <= 0:
        return False, (
            f"Corpus ingestion manifest is incomplete: documents_valid={documents_valid}, "
            f"files={len(current_files)}, chunks_created={chunks_created}"
        )
'''
new = '''    manifest_hashes = payload.get("source_hashes") or {}
    if not isinstance(manifest_hashes, dict) or not manifest_hashes:
        return False, "Corpus ingestion manifest has no source hashes"

    sources_file = corpus_dir / "sources.yaml"
    if not sources_file.exists():
        return False, "Corpus sources.yaml is missing"
    try:
        import yaml

        sources_payload: dict[str, Any] = yaml.safe_load(sources_file.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        return False, f"Corpus sources.yaml is unreadable: {exc}"
    governed_sources = sources_payload.get("sources") or {}
    active_ids = {
        str(source_id)
        for source_id, item in governed_sources.items()
        if isinstance(item, dict) and item.get("is_active") is not False
    }
    if not active_ids:
        return False, "Corpus sources.yaml has no active governed sources"
    if set(manifest_hashes) != active_ids:
        missing = sorted(active_ids - set(manifest_hashes))
        extra = sorted(set(manifest_hashes) - active_ids)
        return False, f"Corpus ingestion manifest source set mismatch (missing={missing}, extra={extra})"

    missing_documents = sorted(source_id for source_id in active_ids if not (corpus_dir / f"{source_id}.md").exists())
    if missing_documents:
        return False, f"Active corpus document(s) missing: {', '.join(missing_documents)}"
    mismatched: list[str] = []
    for source_id in sorted(active_ids):
        source_path = corpus_dir / f"{source_id}.md"
        current_hash = hashlib.md5(source_path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
        if str(manifest_hashes.get(source_id)) != current_hash:
            mismatched.append(source_id)
    if mismatched:
        return False, f"Corpus changed after ingestion for source(s): {', '.join(sorted(mismatched))}"

    documents_valid = int(payload.get("documents_valid") or 0)
    chunks_created = int(payload.get("chunks_created") or 0)
    if documents_valid != len(active_ids) or chunks_created <= 0:
        return False, (
            f"Corpus ingestion manifest is incomplete: documents_valid={documents_valid}, "
            f"active_sources={len(active_ids)}, chunks_created={chunks_created}"
        )
'''
if old not in text:
    raise RuntimeError("manifest source-set block not found")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
Path(__file__).unlink()
print("corpus manifest now audits active sources from sources.yaml")
