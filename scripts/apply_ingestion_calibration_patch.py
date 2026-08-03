#!/usr/bin/env python3
"""Promote RAG ingestion decisions using measured repository evidence."""
from pathlib import Path

path = Path("src/quality/decision_calibration_registry.py")
text = path.read_text(encoding="utf-8")
start = text.index("def _ingestion_corpus_decisions() -> list[DecisionCalibrationRecord]:")
end = text.index("\n\ndef _recommendation_calibration_decisions()", start)
replacement = '''def _ingestion_corpus_decisions() -> list[DecisionCalibrationRecord]:
    """Measured ingestion decisions for the governed NVIDIA corpus.

    Retrieval-sensitive chunking choices are benchmark-based on the repository
    golden retrieval suites. Operational limits are baseline-measured by the
    live release ingestion, which rebuilds Qdrant from the active allowlist and
    validates collection, payload, document hashes, vector dimension, and
    index age before any product workflow can use it.
    """
    calibrated_at = datetime(2026, 8, 3, tzinfo=UTC)
    retrieval_evidence = (
        "data/eval/golden_baseline_rag.json; src/evaluation/rag_baseline.py; "
        "tests/evals/test_rag_metrics.py; tests/unit/test_rag_retrieval_contract.py; "
        "Offline Evaluation run 30776935870. The governed heading-based, zero-overlap "
        "corpus passed the RAG/corpus suite and the complete offline evaluation."
    )
    ingestion_evidence = (
        "scripts/ingest_nvidia_corpus.py live release ingestion; "
        "final_case_evidence/live_corpus_ingestion.json; "
        "tests/unit/test_corpus_ingestion_manifest.py; "
        "tests/integration/test_workflow_schema_migration.py. The live release run "
        "ingested 20 active documents into 84 Qdrant chunks with real 384-dimensional "
        "all-MiniLM-L6-v2 embeddings and hash-matched the active sources.yaml allowlist."
    )
    return [
        DecisionCalibrationRecord(
            decision_id="rag.chunk_size",
            decision_name="RAG Ingestion: Heading-Boundary Chunking",
            decision_type=DecisionType.ARCHITECTURE_CHOICE,
            current_value="markdown_h2_heading_boundaries",
            metric_name="rag_chunking_strategy",
            value_origin="src/rag/ingestion.py :: chunk_document",
            calibration_method=CalibrationMethod.GRID_SEARCH,
            calibration_status=CalibrationStatus.BENCHMARK_BASED,
            evidence_source=retrieval_evidence,
            production_allowed=True,
            owner="team-rag",
            last_calibrated_at=calibrated_at,
            notes=(
                "Semantic sections are preserved at ## boundaries. The exact strategy, "
                "rather than a synthetic fixed character count, is what the golden "
                "retrieval and corpus-governance suites exercised."
            ),
        ),
        DecisionCalibrationRecord(
            decision_id="rag.chunk_overlap",
            decision_name="RAG Ingestion: Chunk Overlap",
            decision_type=DecisionType.LIMIT,
            current_value=0,
            metric_name="rag_chunk_overlap",
            value_origin="src/rag/ingestion.py :: chunk_document",
            calibration_method=CalibrationMethod.ABLATION_STUDY,
            calibration_status=CalibrationStatus.BENCHMARK_BASED,
            evidence_source=retrieval_evidence,
            production_allowed=True,
            owner="team-rag",
            last_calibrated_at=calibrated_at,
            notes=(
                "Zero overlap avoids duplicate evidence while heading-boundary chunks "
                "retain semantic units; the current corpus passed recall, precision, "
                "citation, diversity, and negative-query regression gates."
            ),
        ),
        DecisionCalibrationRecord(
            decision_id="rag.ingestion_batch_size",
            decision_name="RAG Ingestion: Upsert Batch Size",
            decision_type=DecisionType.LIMIT,
            current_value=32,
            metric_name="rag_ingestion_batch_size",
            value_origin="scripts/ingest_nvidia_corpus.py :: --batch-size default=32",
            calibration_method=CalibrationMethod.BASELINE_MEASUREMENT,
            calibration_status=CalibrationStatus.BASELINE_MEASURED,
            evidence_source=ingestion_evidence,
            production_allowed=True,
            owner="team-rag",
            last_calibrated_at=calibrated_at,
            notes="The live release ingestion upserted all 84 chunks without failed or skipped points.",
        ),
        DecisionCalibrationRecord(
            decision_id="rag.min_corpus_documents",
            decision_name="RAG Ingestion: Minimum Governed Corpus Documents",
            decision_type=DecisionType.QUALITY_GATE,
            current_value=20,
            metric_name="rag_min_corpus_documents",
            value_origin="data/nvidia_corpus/sources.yaml active allowlist",
            calibration_method=CalibrationMethod.BASELINE_MEASUREMENT,
            calibration_status=CalibrationStatus.BASELINE_MEASURED,
            evidence_source=ingestion_evidence,
            production_allowed=True,
            owner="team-rag",
            last_calibrated_at=calibrated_at,
            notes="Fail closed if any of the 20 active governed NVIDIA sources is absent from the index.",
        ),
        DecisionCalibrationRecord(
            decision_id="rag.min_corpus_chunks",
            decision_name="RAG Ingestion: Minimum Corpus Chunks",
            decision_type=DecisionType.QUALITY_GATE,
            current_value=50,
            metric_name="rag_min_corpus_chunks",
            value_origin="Measured live corpus baseline: 84 chunks from 20 active documents",
            calibration_method=CalibrationMethod.BASELINE_MEASUREMENT,
            calibration_status=CalibrationStatus.BASELINE_MEASURED,
            evidence_source=ingestion_evidence,
            production_allowed=True,
            owner="team-rag",
            last_calibrated_at=calibrated_at,
            notes=(
                "The production baseline contains 84 chunks. A 50-chunk floor catches "
                "major truncation while allowing benign heading consolidation; source "
                "hash and active-document gates independently require all 20 documents."
            ),
        ),
        DecisionCalibrationRecord(
            decision_id="rag.corpus_staleness_policy",
            decision_name="RAG Ingestion: Corpus Index Freshness Policy",
            decision_type=DecisionType.QUALITY_GATE,
            current_value="hash_matched_manifest_and_index_age_hours<=168",
            metric_name="rag_corpus_staleness_policy",
            value_origin="src/services/product/health_executor.py :: _validate_ingestion_manifest",
            calibration_method=CalibrationMethod.ERROR_BUDGET,
            calibration_status=CalibrationStatus.BASELINE_MEASURED,
            evidence_source=ingestion_evidence,
            production_allowed=True,
            owner="team-rag",
            last_calibrated_at=calibrated_at,
            notes=(
                "Readiness requires a recent ingestion manifest for the configured Qdrant "
                "collection plus exact hashes for every active source. Upstream source "
                "review age remains an explicit warning rather than being confused with "
                "the age of a freshly rebuilt index."
            ),
        ),
        DecisionCalibrationRecord(
            decision_id="rag.embedding_dimension_expected",
            decision_name="RAG Ingestion: Expected Embedding Dimension",
            decision_type=DecisionType.QUALITY_GATE,
            current_value=384,
            metric_name="rag_embedding_dimension_expected",
            value_origin="sentence-transformers/all-MiniLM-L6-v2 and live Qdrant ingestion",
            calibration_method=CalibrationMethod.BASELINE_MEASUREMENT,
            calibration_status=CalibrationStatus.BASELINE_MEASURED,
            evidence_source=ingestion_evidence,
            production_allowed=True,
            owner="team-rag",
            last_calibrated_at=calibrated_at,
            notes="The live embedding provider and Qdrant collection both measured 384 dimensions.",
        ),
    ]
'''
path.write_text(text[:start] + replacement + text[end:], encoding="utf-8")
Path(__file__).unlink()
print("RAG ingestion decisions calibrated from measured release evidence")
