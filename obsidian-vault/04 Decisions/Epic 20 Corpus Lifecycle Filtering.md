# Epic 20 Corpus Lifecycle Filtering

**Decision:** Default Product RAG retrieval must exclude inactive, deprecated, superseded, and expired corpus chunks.

## Context

After automated source sync and Qdrant ingestion, the corpus can evolve over time. Without lifecycle metadata, old chunks could remain retrievable after newer content replaces them.

## Decision

Use `data/nvidia_corpus/sources.yaml` as the authoritative lifecycle manifest. Preserve lifecycle metadata through ingestion and vector payloads. Filter default retrieval to active, non-expired content.

## Consequences

- Reingestion is required for existing Qdrant collections to receive the new metadata.
- Stale content is detected by audit but is not yet an Action Brief warning.
- The system remains offline and allowlist-based; no crawler or external calls were added.
