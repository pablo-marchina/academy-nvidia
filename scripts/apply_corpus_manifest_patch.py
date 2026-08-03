#!/usr/bin/env python3
"""Apply the one-time corpus ingestion-manifest readiness fix."""
from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"pattern missing in {path}: {old[:120]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(
    "src/services/product/health_executor.py",
    "import os\nimport time\n",
    "import hashlib\nimport json\nimport os\nimport time\n",
)

manifest_helper = '''\n\ndef _validate_ingestion_manifest(corpus_dir: Path) -> tuple[bool, str]:
    """Validate that the active Qdrant index was built from current corpus bytes.

    Source review freshness and index freshness are deliberately separate. A
    recently built, hash-matched index is operationally usable even when the
    upstream documentation review policy is overdue; that overdue review is
    surfaced as an explicit warning by ``_check_rag_corpus``.
    """
    manifest_path = corpus_dir / ".ingestion_manifest.json"
    if not manifest_path.exists():
        return False, "Corpus ingestion manifest is missing"
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, f"Corpus ingestion manifest is unreadable: {exc}"

    expected_collection = os.environ.get("QDRANT_COLLECTION", "").strip()
    manifest_collection = str(payload.get("collection_name") or "").strip()
    if expected_collection and manifest_collection != expected_collection:
        return False, (
            f"Corpus ingestion manifest targets collection '{manifest_collection}', "
            f"expected '{expected_collection}'"
        )
    if str(payload.get("backend") or "").casefold() != "qdrant":
        return False, "Corpus ingestion manifest was not produced for Qdrant"

    finished_at = payload.get("finished_at")
    if not finished_at:
        return False, "Corpus ingestion manifest has no finished_at timestamp"
    try:
        finished = datetime.fromisoformat(str(finished_at).replace("Z", "+00:00"))
        max_age_hours = float(os.environ.get("RAG_INDEX_MAX_AGE_HOURS", "168"))
    except (TypeError, ValueError) as exc:
        return False, f"Corpus ingestion manifest has invalid freshness metadata: {exc}"
    age_hours = max(0.0, (datetime.now(UTC) - finished).total_seconds() / 3600.0)
    if age_hours > max_age_hours:
        return False, (
            f"Corpus index manifest is {age_hours:.1f}h old, above "
            f"RAG_INDEX_MAX_AGE_HOURS={max_age_hours:g}"
        )

    manifest_hashes = payload.get("source_hashes") or {}
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
    return True, (
        f"hash-matched Qdrant index built {age_hours:.2f}h ago from "
        f"{documents_valid} document(s) and {chunks_created} chunk(s)"
    )
'''
replace_once(
    "src/services/product/health_executor.py",
    "\ndef _check_sources_freshness(sources_file: Path) -> str:\n",
    manifest_helper + "\n\ndef _check_sources_freshness(sources_file: Path) -> str:\n",
)

old_rag = '''        freshness_error = _check_sources_freshness(sources_file)
        if freshness_error:
            return HealthCheckResult(
                status=CapabilityStatus.degraded,
                detail=freshness_error,
            )
        return HealthCheckResult(
            status=CapabilityStatus.available,
            detail=f"Corpus found with {len(md_files)} document(s)",
        )
'''
new_rag = '''        manifest_path = corpus_dir / ".ingestion_manifest.json"
        manifest_ok, manifest_detail = _validate_ingestion_manifest(corpus_dir)
        if manifest_path.exists() and not manifest_ok:
            return HealthCheckResult(
                status=CapabilityStatus.degraded,
                detail=manifest_detail,
            )
        freshness_error = _check_sources_freshness(sources_file)
        if freshness_error and not manifest_ok:
            return HealthCheckResult(
                status=CapabilityStatus.degraded,
                detail=freshness_error,
            )
        detail = manifest_detail if manifest_ok else f"Corpus found with {len(md_files)} document(s)"
        if freshness_error and manifest_ok:
            detail = f"{detail}; upstream review warning: {freshness_error}"
        return HealthCheckResult(
            status=CapabilityStatus.available,
            detail=detail,
        )
'''
replace_once("src/services/product/health_executor.py", old_rag, new_rag)

manifest_writer = '''    report.finished_at = datetime.now(UTC).isoformat()
    if not args.dry_run and args.backend == "qdrant" and report.documents_valid > 0:
        manifest = {
            "schema_version": 1,
            "ingestion_run_id": report.ingestion_run_id,
            "finished_at": report.finished_at,
            "collection_name": report.collection_name,
            "backend": report.backend,
            "embedding_model": args.embedding_model,
            "vector_size": args.vector_size,
            "documents_valid": report.documents_valid,
            "chunks_created": report.chunks_created,
            "chunks_upserted": report.chunks_upserted,
            "source_hashes": {path.stem: content_hash for path, content_hash in valid_docs},
        }
        manifest_path = _CORPUS_DIR / ".ingestion_manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True),
            encoding="utf-8",
        )
    return report
'''
replace_once(
    "scripts/ingest_nvidia_corpus.py",
    "    report.finished_at = datetime.now(UTC).isoformat()\n    return report\n",
    manifest_writer,
)

gitignore = Path(".gitignore")
ignore_text = gitignore.read_text(encoding="utf-8")
entry = "\n# Runtime corpus index manifest\ndata/nvidia_corpus/.ingestion_manifest.json\n"
if "data/nvidia_corpus/.ingestion_manifest.json" not in ignore_text:
    gitignore.write_text(ignore_text.rstrip() + entry, encoding="utf-8")

Path(__file__).unlink()
print("corpus ingestion manifest readiness fix applied")
