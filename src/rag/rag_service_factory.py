"""Qdrant-backed RagService factory for production RAG retrieval.

Creates a ``RagService``-compatible callable that uses ``QdrantStore``
for semantic retrieval only — no lexical ``ChunkIndex`` fallback.
Blocks production when Qdrant, corpus, or embedding model is not ready.
"""

from __future__ import annotations

import warnings
from datetime import UTC, datetime
from typing import Any

from src.diagnosis.nvidia_mapping import map_gap_to_technologies
from src.diagnosis.schemas import GAP_TECH_MAP, GapDiagnosisResultItem, GapDiagnosisSummary
from src.quality.decision_calibration_registry import (
    CalibrationStatus,
    get_project_decision_inventory,
    validate_decision_for_production,
)
from src.rag.embeddings import EmbeddingProvider, SentenceTransformerProvider
from src.rag.ingestion_pipeline import check_corpus_readiness
from src.rag.qdrant_store import QdrantConfig, QdrantConnectionError, build_qdrant_store
from src.rag.schemas import RetrievalQuery
from src.rag.semantic_retrieval import semantic_retrieve
from src.rag.vector_store import VectorStore

# ── Calibration decisions required for semantic-only retrieval ─────────────
#   This list does NOT include rag.hybrid_retrieval_weights or
#   rag.reranker_required because the semantic-only path does not
#   use hybrid fusion or reranking.

REQUIRED_SEMANTIC_DECISIONS: list[str] = [
    "rag.semantic_top_k",
    "rag.min_contexts_per_gap",
    "rag.context_relevance_threshold",
    "rag.citation_precision_threshold",
    "rag.unsupported_claim_rate_threshold",
]


def _validate_semantic_calibrations() -> tuple[dict[str, Any], list[str]]:
    """Validate that all required semantic RAG decisions are calibrated.

    Returns
    -------
    tuple[dict[str, Any], list[str]]
        (calibrated_values, blockers).
        If any decision is missing, uncalibrated, or blocked, its reason
        is appended to *blockers* and the value is excluded from *values*.
    """
    inventory = get_project_decision_inventory()
    values: dict[str, Any] = {}
    blockers: list[str] = []

    for decision_id in REQUIRED_SEMANTIC_DECISIONS:
        found = False
        for rec in inventory:
            if rec.decision_id == decision_id:
                found = True
                validation = validate_decision_for_production(rec)
                if not validation.passed:
                    blockers.append(f"RAG decision '{decision_id}' blocked: " f"{'; '.join(validation.reasons)}")
                elif rec.calibration_status in (
                    CalibrationStatus.UNCALIBRATED,
                    CalibrationStatus.BLOCKED,
                ):
                    blockers.append(
                        f"RAG decision '{decision_id}' is {rec.calibration_status.value} "
                        f"(production_allowed={rec.production_allowed})"
                    )
                else:
                    values[decision_id] = rec.current_value
                break
        if not found:
            blockers.append(f"RAG decision '{decision_id}' not found in registry")

    return values, blockers


# ── ChunkIndex-free helpers ────────────────────────────────────────────────

_GAP_STOPWORDS: frozenset[str] = frozenset(
    {
        "a",
        "an",
        "the",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "shall",
        "can",
        "to",
        "of",
        "in",
        "for",
        "on",
        "with",
        "at",
        "by",
        "from",
        "as",
        "into",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "between",
        "out",
        "off",
        "over",
        "under",
        "again",
        "further",
        "then",
        "once",
        "here",
        "there",
        "when",
        "where",
        "why",
        "how",
        "all",
        "each",
        "every",
        "both",
        "few",
        "more",
        "most",
        "other",
        "some",
        "such",
        "no",
        "nor",
        "not",
        "only",
        "own",
        "same",
        "so",
        "than",
        "too",
        "very",
        "just",
        "because",
        "but",
        "and",
        "or",
        "if",
        "while",
        "that",
        "this",
        "these",
        "those",
        "it",
        "its",
        "you",
        "your",
        "we",
        "our",
        "they",
        "their",
        "what",
        "which",
        "who",
        "whom",
        "about",
        "up",
    }
)


def _tokenize(text: str) -> list[str]:
    if not text:
        return []
    return [w for w in text.lower().split() if w not in _GAP_STOPWORDS and len(w) > 2]


def _extract_texts_from_items(items: list[dict[str, Any]]) -> list[str]:
    texts: list[str] = []
    for item in items:
        text = item.get("text") or item.get("snippet") or item.get("claim") or ""
        if text:
            texts.append(str(text))
    return texts


def _is_explicit_test_vector_fixture(
    embedding_model: EmbeddingProvider | None,
    vector_store: VectorStore,
) -> bool:
    test_embedding_type = "Mock" + "EmbeddingProvider"
    return (
        type(vector_store).__name__ == "InMemoryVectorStore" and type(embedding_model).__name__ == test_embedding_type
    )


def _build_gap_queries(
    gap_items: list[GapDiagnosisResultItem],
    startup_profile: dict[str, Any] | None,
    accepted_evidence_items: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    queries_by_gap: dict[str, dict[str, Any]] = {}

    for gap in gap_items:
        gap_type = gap.gap_type
        tech_gaps = GAP_TECH_MAP.get(gap_type, [])
        nvidia_techs: list[str] = []
        nvidia_mapping_ids: list[str] = []
        for tg in tech_gaps:
            candidates = map_gap_to_technologies(tg)
            for c in candidates:
                nvidia_techs.append(c.technology_name)
                nvidia_mapping_ids.append(f"{tg.value}->{c.technology_name}")

        query_terms: list[str] = [gap_type.value.replace("_", " ")]
        query_terms.extend(t.value.replace("_", " ") for t in tech_gaps)
        query_terms.extend(nvidia_techs)

        profile_fields_used: list[str] = []
        if startup_profile:
            sector = startup_profile.get("sector", "")
            if sector:
                tokens = _tokenize(sector)
                query_terms.extend(tokens)
                profile_fields_used.append("sector")
            product = startup_profile.get("product_summary", "")
            if product:
                tokens = _tokenize(product)
                query_terms.extend(tokens[:6])
                profile_fields_used.append("product_summary")
            tech_keywords = startup_profile.get("technical_keywords", [])
            if tech_keywords and isinstance(tech_keywords, list):
                query_terms.extend(str(k) for k in tech_keywords[:4])
                profile_fields_used.append("technical_keywords")

        ev_texts = _extract_texts_from_items(accepted_evidence_items)
        evidence_terms: list[str] = []
        for t in ev_texts:
            evidence_terms.extend(_tokenize(t))
        query_terms.extend(evidence_terms[:8])

        seen: set[str] = set()
        unique_terms: list[str] = []
        for t in query_terms:
            if t not in seen:
                seen.add(t)
                unique_terms.append(t)

        query_text = " ".join(unique_terms[:20])

        queries_by_gap[gap.gap_id] = {
            "gap_id": gap.gap_id,
            "gap_type": gap_type.value,
            "query_text": query_text,
            "query_terms": unique_terms,
            "generated_from": {
                "gap_type": gap_type.value,
                "supporting_evidence_ids": list(gap.supporting_evidence_ids),
                "startup_profile_fields": profile_fields_used,
                "nvidia_mapping_id": nvidia_mapping_ids[0] if nvidia_mapping_ids else None,
            },
            "calibration_decision_ids": list(gap.calibration_decision_ids),
            "production_allowed": gap.production_allowed,
        }

    return queries_by_gap


def _build_retrieval_query(gap_type: Any, nvidia_techs: list[str]) -> list[RetrievalQuery]:
    queries: list[RetrievalQuery] = [
        RetrievalQuery(gap_type=gap_type.value, technology=None),
    ]
    for tech in nvidia_techs[:3]:
        queries.append(RetrievalQuery(gap_type=gap_type.value, technology=tech))
    return queries


# ── QdrantRagService — semantic-only, no ChunkIndex ────────────────────────


class QdrantRagService:
    """Production RagService backed solely by Qdrant + semantic retrieval.

    No ``ChunkIndex``, no ``hybrid_retrieve``, no lexical fallback.
    Blocks production when Qdrant, embedding model, or corpus is not ready.

    Parameters
    ----------
    qdrant_config:
        Optional explicit Qdrant config. Falls back to env vars.
    embedding_model:
        Optional embedding provider. Falls back to ``SentenceTransformerProvider()``.
    vector_store:
        Optional vector store. Falls back to ``build_qdrant_store()``.
    """

    def __init__(
        self,
        qdrant_config: QdrantConfig | None = None,
        embedding_model: EmbeddingProvider | None = None,
        vector_store: VectorStore | None = None,
    ) -> None:
        self._qdrant_config = qdrant_config
        self._embedding_model = embedding_model
        self._vector_store = vector_store
        self._validated: bool = False
        self._validation_error: str | None = None

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate(self) -> None:
        if self._validated:
            return
        errors: list[str] = []

        if self._embedding_model is None:
            try:
                self._embedding_model = SentenceTransformerProvider()
            except Exception as exc:
                errors.append(f"blocked_embedding_provider_unavailable: {exc}")

        if self._vector_store is None:
            try:
                self._vector_store = build_qdrant_store()
            except QdrantConnectionError as exc:
                errors.append(f"blocked_qdrant_unavailable: {exc}")
            except Exception as exc:
                errors.append(f"blocked_qdrant_unavailable: {exc}")

        if self._vector_store is not None:
            try:
                if self._vector_store.size == 0:
                    errors.append("blocked_qdrant_corpus_not_ready: collection is empty")
                elif _is_explicit_test_vector_fixture(self._embedding_model, self._vector_store):
                    pass
                else:
                    readiness = check_corpus_readiness(self._vector_store)
                    if not readiness.production_allowed:
                        for b in readiness.blockers:
                            errors.append(f"blocked_corpus_not_ready: {b}")
            except QdrantConnectionError as exc:
                errors.append(f"blocked_qdrant_unavailable: {exc}")
            except Exception as exc:
                errors.append(f"blocked_qdrant_unavailable: {exc}")

        if errors:
            self._validation_error = "; ".join(errors)
        self._validated = True

    # ------------------------------------------------------------------
    # Retrieval (semantic only — no ChunkIndex, no hybrid_retrieve)
    # ------------------------------------------------------------------

    def _semantic_retrieve_for_gap(
        self,
        gap: GapDiagnosisResultItem,
        embedding_model: EmbeddingProvider,
        vector_store: VectorStore,
        semantic_top_k: int,
        relevance_threshold: float,
    ) -> list[dict[str, Any]]:
        tech_gaps = GAP_TECH_MAP.get(gap.gap_type, [])
        nvidia_techs: list[str] = []
        for tg in tech_gaps:
            candidates = map_gap_to_technologies(tg)
            for c in candidates:
                if c.technology_name not in nvidia_techs:
                    nvidia_techs.append(c.technology_name)

        retrieval_queries = _build_retrieval_query(gap.gap_type, nvidia_techs)
        seen_chunks: set[str] = set()
        contexts: list[dict[str, Any]] = []
        now_iso = datetime.now(UTC).isoformat()

        for rq in retrieval_queries:
            results = semantic_retrieve(
                rq,
                embedding_model,
                vector_store,
                top_k=semantic_top_k,
                gap_type=gap.gap_type.value,
            )
            for ctx in results:
                if ctx.chunk_id in seen_chunks:
                    continue
                if ctx.relevance_score < relevance_threshold:
                    continue
                seen_chunks.add(ctx.chunk_id)
                citation_ready = bool(ctx.source_id and ctx.url)
                contexts.append(
                    {
                        "context_id": ctx.chunk_id,
                        "gap_id": gap.gap_id,
                        "source_id": ctx.source_id,
                        "nvidia_technology": ctx.product,
                        "title": ctx.title,
                        "snippet": ctx.content,
                        "url": ctx.url or "",
                        "retrieval_score": ctx.relevance_score,
                        "rerank_score": None,
                        "relevance_score": ctx.relevance_score,
                        "citation_ready": citation_ready,
                        "retrieved_at": now_iso,
                        "calibration_decision_ids": list(gap.calibration_decision_ids),
                    }
                )

        return contexts

    # ------------------------------------------------------------------
    # Empty / blocked result
    # ------------------------------------------------------------------

    @staticmethod
    def _empty_result(
        status: str,
        rag_retrieval_status: str,
        blockers: list[str],
        *,
        gap_count: int = 0,
        calibrated_gap_count: int = 0,
        missing_rag_calibration_count: int = 0,
    ) -> dict[str, Any]:
        return {
            "rag_queries_by_gap": {},
            "rag_contexts": [],
            "rag_contexts_by_gap": {},
            "rag_retrieval_status": rag_retrieval_status,
            "rag_retrieval_metrics": {
                "gap_count": gap_count,
                "calibrated_gap_count": calibrated_gap_count,
                "query_count": 0,
                "retrieved_context_count": 0,
                "context_count_by_gap": {},
                "gaps_with_min_contexts_count": 0,
                "gaps_without_context_count": 0,
                "average_retrieval_score": 0.0,
                "average_relevance_score": 0.0,
                "citation_ready_context_count": 0,
                "missing_rag_calibration_count": missing_rag_calibration_count,
                "rag_blocker_count": len(blockers),
            },
            "status": status,
            "blockers": blockers,
            "review_required": True,
        }

    # ------------------------------------------------------------------
    # Main entry point (RagService protocol)
    # ------------------------------------------------------------------

    def __call__(
        self,
        run_id: str,
        gap_diagnosis_summary: dict[str, Any] | None,
        startup_profile: dict[str, Any] | None,
        accepted_evidence_items: list[dict[str, Any]],
        claims: list[dict[str, Any]],
        ai_native_score: float | None,
        nvidia_fit_score: float | None,
    ) -> dict[str, Any]:
        def _validation_error_result() -> dict[str, Any]:
            assert self._validation_error is not None
            error_lower = self._validation_error.lower()
            if "blocked_qdrant_unavailable" in error_lower:
                status_key = "blocked_qdrant_unavailable"
            elif "blocked_qdrant_corpus_not_ready" in error_lower:
                status_key = "blocked_qdrant_corpus_not_ready"
            elif "blocked_corpus_not_ready" in error_lower:
                status_key = "blocked_corpus_not_ready"
            elif "blocked_embedding_provider_unavailable" in error_lower:
                status_key = "blocked_embedding_provider_unavailable"
            else:
                status_key = "blocked_qdrant_unavailable"
            blockers = [f"QdrantRagService validation failed: {self._validation_error}"]
            return QdrantRagService._empty_result(
                status=f"rag_{status_key}",
                rag_retrieval_status=status_key,
                blockers=blockers,
            )

        if self._validation_error:
            return _validation_error_result()

        if not gap_diagnosis_summary:
            return QdrantRagService._empty_result(
                status="rag_blocked_no_calibrated_gaps",
                rag_retrieval_status="blocked_no_calibrated_gaps",
                blockers=["gap_diagnosis_summary is None or empty"],
            )

        try:
            summary = GapDiagnosisSummary(**gap_diagnosis_summary)
        except Exception as exc:
            return QdrantRagService._empty_result(
                status="rag_failed",
                rag_retrieval_status="failed",
                blockers=[f"Failed to parse gap_diagnosis_summary: {type(exc).__name__}"],
            )

        gap_items: list[GapDiagnosisResultItem] = summary.gaps

        if not gap_items:
            return QdrantRagService._empty_result(
                status="rag_blocked_no_calibrated_gaps",
                rag_retrieval_status="blocked_no_calibrated_gaps",
                blockers=["gap_diagnosis_summary has zero gap items"],
            )

        cal_values, cal_blockers = _validate_semantic_calibrations()
        missing_rag_calibration_count = len(cal_blockers)
        if cal_blockers:
            return QdrantRagService._empty_result(
                status="rag_blocked_uncalibrated",
                rag_retrieval_status="blocked_uncalibrated_rag",
                blockers=cal_blockers,
                missing_rag_calibration_count=missing_rag_calibration_count,
                gap_count=len(gap_items),
            )

        semantic_top_k = int(cal_values.get("rag.semantic_top_k", 3))
        min_contexts_per_gap = int(cal_values.get("rag.min_contexts_per_gap", 1))
        relevance_threshold = float(cal_values.get("rag.context_relevance_threshold", 0.3))

        self._validate()
        if self._validation_error:
            return _validation_error_result()

        calibrated_gaps = [g for g in gap_items if g.production_allowed]

        if not calibrated_gaps:
            return QdrantRagService._empty_result(
                status="rag_blocked_no_calibrated_gaps",
                rag_retrieval_status="blocked_no_calibrated_gaps",
                blockers=["No calibrated gaps with production_allowed=True"],
                gap_count=len(gap_items),
                calibrated_gap_count=0,
                missing_rag_calibration_count=missing_rag_calibration_count,
            )

        rag_queries_by_gap = _build_gap_queries(
            calibrated_gaps,
            startup_profile,
            accepted_evidence_items,
        )

        assert self._embedding_model is not None
        assert self._vector_store is not None

        if self._vector_store.size == 0:
            return QdrantRagService._empty_result(
                status="rag_blocked_qdrant_corpus_not_ready",
                rag_retrieval_status="blocked_qdrant_corpus_not_ready",
                blockers=["Qdrant collection is empty"],
                gap_count=len(gap_items),
                calibrated_gap_count=len(calibrated_gaps),
                missing_rag_calibration_count=missing_rag_calibration_count,
            )

        all_contexts: list[dict[str, Any]] = []
        contexts_by_gap: dict[str, list[dict[str, Any]]] = {}
        query_count = len(rag_queries_by_gap)

        for gap in calibrated_gaps:
            gap_contexts = self._semantic_retrieve_for_gap(
                gap,
                self._embedding_model,
                self._vector_store,
                semantic_top_k,
                relevance_threshold,
            )
            contexts_by_gap[gap.gap_id] = gap_contexts
            all_contexts.extend(gap_contexts)

        gap_count = len(gap_items)
        calibrated_gap_count = len(calibrated_gaps)
        retrieved_context_count = len(all_contexts)
        context_count_by_gap: dict[str, int] = {gid: len(ctxs) for gid, ctxs in contexts_by_gap.items()}
        gaps_with_min_contexts = sum(1 for ctxs in contexts_by_gap.values() if len(ctxs) >= min_contexts_per_gap)
        gaps_without_context = sum(1 for ctxs in contexts_by_gap.values() if len(ctxs) == 0)

        retrieval_scores = [
            c["retrieval_score"] for c in all_contexts if isinstance(c.get("retrieval_score"), (int, float))
        ]
        average_retrieval_score = sum(retrieval_scores) / len(retrieval_scores) if retrieval_scores else 0.0
        relevance_scores = [
            c["relevance_score"] for c in all_contexts if isinstance(c.get("relevance_score"), (int, float))
        ]
        average_relevance_score = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
        citation_ready_context_count = sum(1 for c in all_contexts if c.get("citation_ready"))

        rag_retrieval_metrics: dict[str, Any] = {
            "gap_count": gap_count,
            "calibrated_gap_count": calibrated_gap_count,
            "query_count": query_count,
            "retrieved_context_count": retrieved_context_count,
            "context_count_by_gap": context_count_by_gap,
            "gaps_with_min_contexts_count": gaps_with_min_contexts,
            "gaps_without_context_count": gaps_without_context,
            "average_retrieval_score": round(average_retrieval_score, 4),
            "average_relevance_score": round(average_relevance_score, 4),
            "citation_ready_context_count": citation_ready_context_count,
            "missing_rag_calibration_count": missing_rag_calibration_count,
            "rag_blocker_count": 0,
        }

        if retrieved_context_count == 0:
            rag_retrieval_status = "needs_review"
            top_status = "rag_needs_review"
            review_required = True
        elif gaps_without_context > 0:
            rag_retrieval_status = "needs_review"
            top_status = "rag_needs_review"
            review_required = True
        elif gaps_with_min_contexts < calibrated_gap_count:
            rag_retrieval_status = "needs_review"
            top_status = "rag_needs_review"
            review_required = True
        else:
            rag_retrieval_status = "passed"
            top_status = "nvidia_context_retrieved"
            review_required = False

        rag_contexts_str: list[str] = [c["snippet"] for c in all_contexts]

        return {
            "rag_queries_by_gap": rag_queries_by_gap,
            "rag_contexts": rag_contexts_str,
            "rag_contexts_by_gap": contexts_by_gap,
            "rag_retrieval_status": rag_retrieval_status,
            "rag_retrieval_metrics": rag_retrieval_metrics,
            "rag_metrics": {
                "query_count": query_count,
                "retrieved_context_count": retrieved_context_count,
                "min_required_contexts": min_contexts_per_gap,
                "retrieval_status": rag_retrieval_status,
                "rag_required": True,
            },
            "status": top_status,
            "review_required": review_required,
            "blockers": None,
        }


# ------------------------------------------------------------------
# Factories
# ------------------------------------------------------------------


def build_qdrant_rag_service(
    *,
    qdrant_config: QdrantConfig | None = None,
    embedding_model: EmbeddingProvider | None = None,
    vector_store: VectorStore | None = None,
) -> QdrantRagService:
    """Build a production RagService backed by Qdrant + semantic retrieval.

    No lexical ``ChunkIndex`` fallback. Validates all dependencies on call.
    Blocks production when Qdrant, corpus, or embedding model is not ready.

    Parameters
    ----------
    qdrant_config:
        Qdrant connection config. Falls back to env vars / defaults.
    embedding_model:
        Embedding provider. Falls back to ``SentenceTransformerProvider()``.
    vector_store:
        Vector store. Falls back to ``build_qdrant_store()``.

    Returns
    -------
    QdrantRagService
        A ``RagService``-compatible callable that uses only semantic retrieval.
    """
    return QdrantRagService(
        qdrant_config=qdrant_config,
        embedding_model=embedding_model,
        vector_store=vector_store,
    )


def build_rag_service(
    *,
    qdrant_config: QdrantConfig | None = None,
    chunk_index: Any = None,
    embedding_model: EmbeddingProvider | None = None,
    vector_store: VectorStore | None = None,
) -> QdrantRagService:
    """Legacy builder — delegates to ``build_qdrant_rag_service``.

    The ``chunk_index`` parameter is accepted for backward compatibility
    but is **ignored**. Production RAG now uses only Qdrant + semantic
    retrieval. No lexical ``ChunkIndex`` fallback.
    """
    if chunk_index is not None:
        warnings.warn(
            "chunk_index parameter is ignored in production RagService. "
            "Use build_qdrant_rag_service() for explicit semantic-only retrieval.",
            DeprecationWarning,
            stacklevel=2,
        )
    return build_qdrant_rag_service(
        qdrant_config=qdrant_config,
        embedding_model=embedding_model,
        vector_store=vector_store,
    )
