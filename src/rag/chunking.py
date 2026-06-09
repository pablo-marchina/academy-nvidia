"""Scaffold for document chunking policies used by the RAG pipeline."""


def chunk_document(text: str) -> list[str]:
    """Placeholder chunker that will be replaced with a retrieval-aware strategy."""

    return [text] if text else []
