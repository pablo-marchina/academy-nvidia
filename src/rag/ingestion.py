"""Markdown corpus ingestion and chunking for Product RAG."""

from __future__ import annotations

from pathlib import Path

import yaml

from src.rag.schemas import RagChunk, RagDocument, RagSource

_CORPUS_DIR = Path("data/nvidia_corpus")
_SOURCES_FILE = _CORPUS_DIR / "sources.yaml"


def load_sources() -> dict[str, RagSource]:
    """Load source metadata from sources.yaml."""
    if not _SOURCES_FILE.exists():
        return {}
    raw = _SOURCES_FILE.read_text(encoding="utf-8")
    data = yaml.safe_load(raw)
    sources_raw = data.get("sources", {})
    sources: dict[str, RagSource] = {}
    for sid, info in sources_raw.items():
        active_info = _active_version_info(info)
        sources[sid] = RagSource(
            source_id=sid,
            title=info.get("title", sid),
            url=info.get("url"),
            product=info.get("product", ""),
            gap_types=info.get("gap_types", []),
            version=active_info.get("version", info.get("version", "1.0")),
            document_type=info.get("document_type", "nvidia_corpus"),
            content_hash=active_info.get("content_hash", info.get("content_hash")),
            previous_content_hash=active_info.get("previous_content_hash", info.get("previous_content_hash")),
            collected_at=active_info.get("collected_at", info.get("collected_at")),
            last_checked_at=active_info.get("last_checked_at", info.get("last_checked_at")),
            valid_from=active_info.get("valid_from", info.get("valid_from")),
            valid_until=active_info.get("valid_until", info.get("valid_until")),
            freshness_policy=active_info.get("freshness_policy", info.get("freshness_policy")),
            stale_after_days=active_info.get("stale_after_days", info.get("stale_after_days")),
            is_active=active_info.get("is_active", info.get("is_active", True)),
            deprecated_at=active_info.get("deprecated_at", info.get("deprecated_at")),
            superseded_by=active_info.get("superseded_by", info.get("superseded_by")),
            deprecation_reason=active_info.get("deprecation_reason", info.get("deprecation_reason")),
        )
    return sources


def _active_version_info(info: dict) -> dict:
    versions = info.get("versions")
    if not isinstance(versions, list):
        return info
    active_versions = [v for v in versions if isinstance(v, dict) and v.get("is_active") is True]
    if active_versions:
        return active_versions[-1]
    return versions[-1] if versions and isinstance(versions[-1], dict) else info


def load_markdown_document(path: Path) -> RagDocument | None:
    """Load a single markdown file as a RagDocument."""
    if not path.exists() or path.suffix not in (".md", ".markdown"):
        return None
    text = path.read_text(encoding="utf-8")
    source_id = path.stem
    title = _extract_title(text) or source_id
    return RagDocument(source_id=source_id, title=title, raw_text=text)


def _extract_title(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# ") and not stripped.startswith("## "):
            return stripped[2:].strip()
    return None


def chunk_document(doc: RagDocument, sources: dict[str, RagSource]) -> list[RagChunk]:
    """Split a RagDocument into RagChunks by ## headings."""
    source_info = sources.get(doc.source_id)
    chunks: list[RagChunk] = []
    lines = doc.raw_text.splitlines()
    current_section: list[str] = []
    current_heading = ""
    chunk_index = 0

    for line in lines:
        if line.startswith("## "):
            if current_section and current_heading:
                content = "\n".join(current_section).strip()
                if content:
                    chunks.append(
                        _make_chunk(
                            doc=doc,
                            source_info=source_info,
                            index=chunk_index,
                            heading=current_heading,
                            content=content,
                        )
                    )
                    chunk_index += 1
            current_heading = line[3:].strip()
            current_section = [line]
        else:
            current_section.append(line)

    if current_section and current_heading:
        content = "\n".join(current_section).strip()
        if content:
            chunks.append(
                _make_chunk(
                    doc=doc,
                    source_info=source_info,
                    index=chunk_index,
                    heading=current_heading,
                    content=content,
                )
            )

    return chunks


def _make_chunk(
    doc: RagDocument,
    source_info: RagSource | None,
    index: int,
    heading: str,
    content: str,
) -> RagChunk:
    return RagChunk(
        chunk_id=f"{doc.source_id}_{index:03d}",
        source_id=doc.source_id,
        title=doc.title,
        content=content,
        product=source_info.product if source_info else doc.title,
        gap_types=source_info.gap_types if source_info else [],
        url=source_info.url if source_info else None,
        version=source_info.version if source_info else "1.0",
        document_type=source_info.document_type if source_info else "nvidia_corpus",
        content_hash=source_info.content_hash if source_info else None,
        previous_content_hash=source_info.previous_content_hash if source_info else None,
        collected_at=source_info.collected_at if source_info else None,
        last_checked_at=source_info.last_checked_at if source_info else None,
        valid_from=source_info.valid_from if source_info else None,
        valid_until=source_info.valid_until if source_info else None,
        freshness_policy=source_info.freshness_policy if source_info else None,
        stale_after_days=source_info.stale_after_days if source_info else None,
        is_active=source_info.is_active if source_info else True,
        deprecated_at=source_info.deprecated_at if source_info else None,
        superseded_by=source_info.superseded_by if source_info else None,
        deprecation_reason=source_info.deprecation_reason if source_info else None,
        nvidia_technology=source_info.product if source_info else "",
        corpus_version=source_info.version if source_info else "1.0",
        chunk_index=index,
        char_count=len(content),
    )


def load_and_chunk_corpus() -> list[RagChunk]:
    """Load all markdown files from the corpus directory and chunk them."""
    sources = load_sources()
    all_chunks: list[RagChunk] = []
    if not _CORPUS_DIR.exists():
        return all_chunks
    for md_path in sorted(_CORPUS_DIR.glob("*.md")):
        if md_path.name == "README.md":
            continue
        doc = load_markdown_document(md_path)
        if doc is None:
            continue
        doc_chunks = chunk_document(doc, sources)
        all_chunks.extend(doc_chunks)
    return all_chunks
