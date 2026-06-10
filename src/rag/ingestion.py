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
        sources[sid] = RagSource(
            source_id=sid,
            title=info.get("title", sid),
            url=info.get("url"),
            product=info.get("product", ""),
            gap_types=info.get("gap_types", []),
            version=info.get("version", "1.0"),
            document_type=info.get("document_type", "nvidia_corpus"),
        )
    return sources


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
