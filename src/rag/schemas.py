"""Schemas for Product RAG module."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RagSource(BaseModel):
    source_id: str
    title: str
    url: str | None = None
    product: str
    gap_types: list[str] = Field(default_factory=list)


class RagDocument(BaseModel):
    source_id: str
    title: str
    raw_text: str


class RagChunk(BaseModel):
    chunk_id: str
    source_id: str
    title: str
    content: str
    product: str
    gap_types: list[str] = Field(default_factory=list)
    url: str | None = None


class RetrievalQuery(BaseModel):
    technology: str | None = None
    gap_type: str | None = None
    keywords: list[str] = Field(default_factory=list)


class RetrievedContext(BaseModel):
    chunk_id: str
    source_id: str
    title: str
    content: str
    product: str
    gap_types: list[str] = Field(default_factory=list)
    url: str | None = None
    relevance_score: float = 0.0


class PlaybookRetrievalResult(BaseModel):
    query: RetrievalQuery
    contexts: list[RetrievedContext] = Field(default_factory=list)
    total_found: int = 0
    missing_context: bool = False
    reasoning: str = ""
